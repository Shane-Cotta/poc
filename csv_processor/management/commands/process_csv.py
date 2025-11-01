import csv
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from csv_processor.models import CSVProcessingRecord, EmailRecord

# Get logger for this module
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scans incoming folder for CSV files, processes them, and sends emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once instead of continuously',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=120,
            help='Interval in seconds between scans (default: 120)',
        )

    def handle(self, *args, **options):
        run_once = options['once']
        interval = options['interval']
        
        # Ensure directories exist
        self.ensure_directories()
        
        if run_once:
            logger.info('Starting single CSV scan')
            self.stdout.write(self.style.SUCCESS('Running single scan...'))
            self.process_csv_files()
        else:
            logger.info('Starting continuous CSV scan with %d second interval', interval)
            self.stdout.write(self.style.SUCCESS(f'Starting continuous scan every {interval} seconds...'))
            while True:
                self.process_csv_files()
                time.sleep(interval)

    def ensure_directories(self):
        """Ensure incoming and processed directories exist"""
        logger.debug('Ensuring directories exist: incoming=%s, processed=%s',
                    settings.CSV_INCOMING_DIR, settings.CSV_PROCESSED_DIR)
        settings.CSV_INCOMING_DIR.mkdir(exist_ok=True)
        settings.CSV_PROCESSED_DIR.mkdir(exist_ok=True)

    def process_csv_files(self):
        """Process all CSV files in the incoming directory"""
        incoming_dir = settings.CSV_INCOMING_DIR
        
        csv_files = list(incoming_dir.glob('*.csv'))
        
        if not csv_files:
            logger.info('No CSV files found in %s', incoming_dir)
            self.stdout.write(f'[{datetime.now()}] No CSV files found in {incoming_dir}')
            return
        
        logger.info('Found %d CSV file(s) to process in %s', len(csv_files), incoming_dir)
        self.stdout.write(self.style.SUCCESS(f'[{datetime.now()}] Found {len(csv_files)} CSV file(s) to process'))
        
        for csv_file in csv_files:
            self.process_single_csv(csv_file)

    def process_single_csv(self, csv_file_path):
        """Process a single CSV file"""
        logger.info('Processing CSV file: %s', csv_file_path.name)
        self.stdout.write(f'Processing {csv_file_path.name}...')
        
        # Create processing record
        record = CSVProcessingRecord.objects.create(
            filename=csv_file_path.name,
            status='processing'
        )
        logger.debug('Created processing record with ID: %d for file: %s',
                    record.id, csv_file_path.name)
        
        total_rows = 0
        successful_rows = 0
        failed_rows = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    total_rows += 1
                    
                    # Extract zip and email from CSV
                    zip_code = row.get('zip', '').strip()
                    email = row.get('email', '').strip()
                    
                    if not zip_code or not email:
                        failed_rows += 1
                        logger.warning('Row %d in %s has missing data: zip=%s, email=%s',
                                      total_rows, csv_file_path.name, 
                                      zip_code or 'MISSING', email or 'MISSING')
                        EmailRecord.objects.create(
                            processing_record=record,
                            email_address=email or 'N/A',
                            zip_code=zip_code or 'N/A',
                            success=False,
                            error_message='Missing zip code or email'
                        )
                        continue
                    
                    # Process the row
                    success = self.process_row(record, zip_code, email)
                    if success:
                        successful_rows += 1
                    else:
                        failed_rows += 1
            
            # Update record
            record.total_rows = total_rows
            record.successful_rows = successful_rows
            record.failed_rows = failed_rows
            record.status = 'completed'
            record.save()
            
            logger.info('Completed processing %s: %d/%d rows successful, %d failed',
                       csv_file_path.name, successful_rows, total_rows, failed_rows)
            
            # Move to processed folder
            self.move_to_processed(csv_file_path)
            
            self.stdout.write(self.style.SUCCESS(
                f'Completed {csv_file_path.name}: {successful_rows}/{total_rows} successful'
            ))
            
        except Exception as e:
            logger.error('Error processing CSV file %s: %s', csv_file_path.name, str(e),
                        exc_info=True)
            record.status = 'failed'
            record.save()
            self.stdout.write(self.style.ERROR(f'Error processing {csv_file_path.name}: {str(e)}'))

    def process_row(self, record, zip_code, email):
        """Process a single row: fetch state from API and send email"""
        try:
            logger.debug('Processing row: email=%s, zip=%s', email, zip_code)
            
            # Call ZIP API
            state, city = self.get_location_from_zip(zip_code)
            
            # Send email
            self.send_email_to_address(email, zip_code, state, city)
            
            # Record success
            EmailRecord.objects.create(
                processing_record=record,
                email_address=email,
                zip_code=zip_code,
                state=state,
                city=city,
                success=True
            )
            
            logger.debug('Successfully processed row: email=%s, zip=%s, state=%s, city=%s',
                        email, zip_code, state, city)
            return True
            
        except Exception as e:
            logger.warning('Failed to process row: email=%s, zip=%s, error=%s',
                          email, zip_code, str(e))
            # Record failure
            EmailRecord.objects.create(
                processing_record=record,
                email_address=email,
                zip_code=zip_code,
                success=False,
                error_message=str(e)
            )
            self.stdout.write(self.style.WARNING(f'Failed to process {email}: {str(e)}'))
            return False

    def get_location_from_zip(self, zip_code):
        """Fetch state and city information from ZIP code API"""
        url = settings.ZIP_API_URL.format(zip=zip_code)
        timeout = getattr(settings, 'ZIP_API_TIMEOUT', 5)
        
        try:
            logger.debug('Calling ZIP API for zip=%s, url=%s', zip_code, url)
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract state and city from response
            if 'places' in data and len(data['places']) > 0:
                place = data['places'][0]
                state = place.get('state', 'Unknown')
                city = place.get('place name', 'Unknown')
                logger.debug('ZIP API returned: zip=%s, state=%s, city=%s',
                            zip_code, state, city)
                return state, city
            else:
                logger.warning('ZIP API returned no places for zip=%s', zip_code)
                return 'Unknown', 'Unknown'
                
        except requests.RequestException as e:
            logger.error('ZIP API request failed for zip=%s: %s', zip_code, str(e))
            raise Exception(f'API error for ZIP {zip_code}: {str(e)}')

    def send_email_to_address(self, email, zip_code, state, city):
        """Send email using Django's email backend"""
        subject = f'Location Information for ZIP {zip_code}'
        message = f'''
Hello,

Here is the location information for ZIP code {zip_code}:

City: {city}
State: {state}

Thank you!
'''
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        
        logger.debug('Sending email to %s with subject: %s', email, subject)
        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        logger.info('Email sent successfully to %s for ZIP %s', email, zip_code)

    def move_to_processed(self, csv_file_path):
        """Move processed CSV file to processed directory"""
        processed_dir = settings.CSV_PROCESSED_DIR
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{csv_file_path.stem}_{timestamp}{csv_file_path.suffix}"
        
        destination = processed_dir / new_filename
        logger.info('Moving processed file from %s to %s', csv_file_path, destination)
        shutil.move(str(csv_file_path), str(destination))
