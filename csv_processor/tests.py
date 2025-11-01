import csv
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import CSVProcessingRecord, EmailRecord


class CSVProcessingRecordModelTest(TestCase):
    def test_create_record(self):
        record = CSVProcessingRecord.objects.create(
            filename='test.csv',
            total_rows=10,
            successful_rows=8,
            failed_rows=2,
            status='completed'
        )
        self.assertEqual(record.filename, 'test.csv')
        self.assertEqual(record.total_rows, 10)
        self.assertEqual(record.successful_rows, 8)
        self.assertEqual(record.failed_rows, 2)
        self.assertEqual(record.status, 'completed')

    def test_string_representation(self):
        record = CSVProcessingRecord.objects.create(filename='test.csv')
        self.assertIn('test.csv', str(record))


class EmailRecordModelTest(TestCase):
    def setUp(self):
        self.processing_record = CSVProcessingRecord.objects.create(
            filename='test.csv'
        )

    def test_create_email_record(self):
        email_record = EmailRecord.objects.create(
            processing_record=self.processing_record,
            email_address='test@example.com',
            zip_code='90210',
            state='California',
            city='Beverly Hills',
            success=True
        )
        self.assertEqual(email_record.email_address, 'test@example.com')
        self.assertEqual(email_record.zip_code, '90210')
        self.assertEqual(email_record.state, 'California')
        self.assertTrue(email_record.success)

    def test_string_representation(self):
        email_record = EmailRecord.objects.create(
            processing_record=self.processing_record,
            email_address='test@example.com',
            zip_code='90210'
        )
        self.assertIn('test@example.com', str(email_record))
        self.assertIn('90210', str(email_record))


class ProcessCSVCommandTest(TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.incoming_dir = Path(self.test_dir) / 'incoming'
        self.processed_dir = Path(self.test_dir) / 'processed'
        self.incoming_dir.mkdir()
        self.processed_dir.mkdir()

    def tearDown(self):
        # Clean up temporary directories
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_csv(self, filename, rows):
        """Helper to create a test CSV file"""
        csv_path = self.incoming_dir / filename
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['zip', 'email'])
            writer.writeheader()
            writer.writerows(rows)
        return csv_path

    @override_settings(
        CSV_INCOMING_DIR=None,  # Will be set in test
        CSV_PROCESSED_DIR=None  # Will be set in test
    )
    @patch('csv_processor.management.commands.process_csv.Command.get_location_from_zip')
    @patch('csv_processor.management.commands.process_csv.send_mail')
    def test_process_single_csv(self, mock_send_mail, mock_get_location):
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        mock_get_location.return_value = ('California', 'Beverly Hills')

        # Create test CSV
        test_data = [
            {'zip': '90210', 'email': 'test1@example.com'},
            {'zip': '10001', 'email': 'test2@example.com'},
        ]
        self.create_test_csv('test.csv', test_data)

        # Run command
        call_command('process_csv', '--once')

        # Verify
        self.assertEqual(CSVProcessingRecord.objects.count(), 1)
        record = CSVProcessingRecord.objects.first()
        self.assertEqual(record.filename, 'test.csv')
        self.assertEqual(record.total_rows, 2)
        self.assertEqual(record.successful_rows, 2)
        self.assertEqual(record.status, 'completed')

        # Check email records
        self.assertEqual(EmailRecord.objects.count(), 2)

        # Check that send_mail was called
        self.assertEqual(mock_send_mail.call_count, 2)

        # Check that CSV was moved to processed
        self.assertFalse((self.incoming_dir / 'test.csv').exists())
        processed_files = list(self.processed_dir.glob('test_*.csv'))
        self.assertEqual(len(processed_files), 1)

    @override_settings(
        CSV_INCOMING_DIR=None,
        CSV_PROCESSED_DIR=None
    )
    @patch('csv_processor.management.commands.process_csv.Command.get_location_from_zip')
    @patch('csv_processor.management.commands.process_csv.send_mail')
    def test_process_csv_with_missing_data(self, mock_send_mail, mock_get_location):
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        # Setup mock to return valid data
        mock_get_location.return_value = ('California', 'Beverly Hills')

        # Create test CSV with missing data
        test_data = [
            {'zip': '90210', 'email': 'test1@example.com'},
            {'zip': '', 'email': 'test2@example.com'},  # Missing zip
            {'zip': '10001', 'email': ''},  # Missing email
        ]
        self.create_test_csv('test.csv', test_data)

        # Run command
        call_command('process_csv', '--once')

        # Verify
        record = CSVProcessingRecord.objects.first()
        self.assertEqual(record.total_rows, 3)
        self.assertEqual(record.failed_rows, 2)
        self.assertEqual(record.successful_rows, 1)

    @override_settings(
        CSV_INCOMING_DIR=None,
        CSV_PROCESSED_DIR=None
    )
    @patch('csv_processor.management.commands.process_csv.Command.get_location_from_zip')
    @patch('csv_processor.management.commands.process_csv.send_mail')
    def test_api_error_handling(self, mock_send_mail, mock_get_location):
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        # Simulate API error
        mock_get_location.side_effect = Exception('API Error')

        # Create test CSV
        test_data = [
            {'zip': '90210', 'email': 'test1@example.com'},
        ]
        self.create_test_csv('test.csv', test_data)

        # Run command
        call_command('process_csv', '--once')

        # Verify that error was recorded
        email_record = EmailRecord.objects.first()
        self.assertFalse(email_record.success)
        self.assertIn('API Error', email_record.error_message)

    @override_settings(
        CSV_INCOMING_DIR=None,
        CSV_PROCESSED_DIR=None
    )
    def test_no_csv_files(self):
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        # Run command with no CSV files
        call_command('process_csv', '--once')

        # Verify no records created
        self.assertEqual(CSVProcessingRecord.objects.count(), 0)
        self.assertEqual(EmailRecord.objects.count(), 0)


class LoggingTest(TestCase):
    """Test that logging is working correctly"""
    
    def setUp(self):
        # Create temporary directories for testing
        import tempfile
        self.test_dir = tempfile.mkdtemp()
        self.incoming_dir = Path(self.test_dir) / 'incoming'
        self.processed_dir = Path(self.test_dir) / 'processed'
        self.incoming_dir.mkdir()
        self.processed_dir.mkdir()

    def tearDown(self):
        # Clean up temporary directories
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_csv(self, filename, rows):
        """Helper to create a test CSV file"""
        csv_path = self.incoming_dir / filename
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['zip', 'email'])
            writer.writeheader()
            writer.writerows(rows)
        return csv_path

    @override_settings(
        CSV_INCOMING_DIR=None,
        CSV_PROCESSED_DIR=None
    )
    @patch('csv_processor.management.commands.process_csv.Command.get_location_from_zip')
    @patch('csv_processor.management.commands.process_csv.send_mail')
    def test_logging_messages(self, mock_send_mail, mock_get_location):
        """Test that appropriate log messages are generated"""
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        mock_get_location.return_value = ('California', 'Beverly Hills')

        # Create test CSV
        test_data = [
            {'zip': '90210', 'email': 'test@example.com'},
        ]
        self.create_test_csv('test.csv', test_data)

        # Run command and capture logs
        with self.assertLogs('csv_processor.management.commands.process_csv', level='INFO') as cm:
            call_command('process_csv', '--once')

        # Verify log messages contain expected content
        log_output = ' '.join(cm.output)
        self.assertIn('Starting single CSV scan', log_output)
        self.assertIn('Found 1 CSV file(s) to process', log_output)
        self.assertIn('Processing CSV file: test.csv', log_output)
        self.assertIn('Email sent successfully', log_output)
        self.assertIn('Completed processing test.csv', log_output)
        self.assertIn('Moving processed file', log_output)

    @override_settings(
        CSV_INCOMING_DIR=None,
        CSV_PROCESSED_DIR=None
    )
    @patch('csv_processor.management.commands.process_csv.Command.get_location_from_zip')
    @patch('csv_processor.management.commands.process_csv.send_mail')
    def test_warning_logging_for_missing_data(self, mock_send_mail, mock_get_location):
        """Test that warnings are logged for missing data"""
        # Setup
        from django.conf import settings
        settings.CSV_INCOMING_DIR = self.incoming_dir
        settings.CSV_PROCESSED_DIR = self.processed_dir

        mock_get_location.return_value = ('California', 'Beverly Hills')

        # Create test CSV with missing data
        test_data = [
            {'zip': '', 'email': 'test@example.com'},  # Missing zip
        ]
        self.create_test_csv('test.csv', test_data)

        # Run command and capture logs at WARNING level
        with self.assertLogs('csv_processor.management.commands.process_csv', level='WARNING') as cm:
            call_command('process_csv', '--once')

        # Verify warning was logged
        log_output = ' '.join(cm.output)
        self.assertIn('has missing data', log_output)
        self.assertIn('MISSING', log_output)


