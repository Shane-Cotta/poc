# Django Logging Best Practices

This document outlines the logging improvements implemented in this project and best practices for Django logging.

## Implementation Summary (2025-11-01)

### What Was Changed

The CSV processor management command was updated to use Python's `logging` module instead of relying solely on `self.stdout.write()` for operational messages.

**Changes made:**
1. Added `import logging` to the process_csv.py command
2. Created a module-level logger: `logger = logging.getLogger(__name__)`
3. Replaced print-style messages with appropriate log levels
4. Added logging configuration to Django settings.py
5. Kept `self.stdout.write()` for user-facing command output

### Django Logging Best Practices

#### 1. Use Python's Built-in Logging Module

Django provides excellent integration with Python's `logging` module. Always use it for diagnostic and operational logging.

```python
import logging

logger = logging.getLogger(__name__)
```

#### 2. Choose Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information for troubleshooting
  ```python
  logger.debug('Processing row: email=%s, zip=%s', email, zip_code)
  ```

- **INFO**: General informational messages about normal operations
  ```python
  logger.info('Completed processing %s: %d/%d rows successful', filename, success, total)
  ```

- **WARNING**: Indication of something unexpected or potential issues
  ```python
  logger.warning('Failed to process row: email=%s, error=%s', email, str(e))
  ```

- **ERROR**: Serious problems that need attention
  ```python
  logger.error('Error processing CSV file %s: %s', filename, str(e), exc_info=True)
  ```

- **CRITICAL**: Very serious errors that may cause the application to stop
  ```python
  logger.critical('Database connection lost')
  ```

#### 3. Use Structured Logging with Placeholders

**DO:**
```python
logger.info('Processing file: %s with %d rows', filename, row_count)
```

**DON'T:**
```python
logger.info(f'Processing file: {filename} with {row_count} rows')
```

Using placeholders (`%s`, `%d`) is more efficient because string interpolation only happens if the log message is actually output.

#### 4. Include Exception Information

When logging exceptions, use `exc_info=True` to include the traceback:

```python
try:
    # code that might fail
    process_data()
except Exception as e:
    logger.error('Failed to process data: %s', str(e), exc_info=True)
```

#### 5. Configure Logging in settings.py

Django's LOGGING setting provides powerful configuration options:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'app.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'your_app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### 6. Separate User Output from Logging

In management commands, use:
- `self.stdout.write()` for user-facing output and command results
- `logger.*()` for diagnostic/operational logging

```python
# User-facing output
self.stdout.write(self.style.SUCCESS('Processing completed!'))

# Operational logging
logger.info('Processed %d records successfully', count)
```

#### 7. Use Named Loggers

Always use `logging.getLogger(__name__)` to get a logger for your module. This creates a logger hierarchy that matches your Python package structure.

```python
# At the top of your module
import logging
logger = logging.getLogger(__name__)
```

For `csv_processor.management.commands.process_csv`, this creates a logger named `csv_processor.management.commands.process_csv`, which can be configured separately from other loggers.

#### 8. Environment-Specific Configuration

Configure different log levels and handlers for different environments:

```python
# Development: verbose console logging
if DEBUG:
    LOGGING['loggers']['csv_processor']['level'] = 'DEBUG'
    
# Production: file logging with rotation
else:
    LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/django/csv_processor.log',
        'maxBytes': 1024 * 1024 * 10,  # 10 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
```

#### 9. Don't Log Sensitive Information

Be careful not to log passwords, API keys, or other sensitive data:

```python
# DON'T
logger.info('Login attempt with password: %s', password)

# DO
logger.info('Login attempt for user: %s', username)
```

#### 10. Performance Considerations

For expensive operations (like serializing large objects), use lazy evaluation:

```python
# Only formats the message if DEBUG level is enabled
if logger.isEnabledFor(logging.DEBUG):
    logger.debug('Large data structure: %s', expensive_serialization())
```

## Project-Specific Logging Strategy

### CSV Processor Command

The process_csv command uses logging at different levels:

- **INFO**: Major milestones (start, file found, completion, file moved)
- **DEBUG**: Detailed processing steps (each row, API calls, email sending)
- **WARNING**: Recoverable issues (missing data, failed rows)
- **ERROR**: Serious failures (file processing errors, API failures)

### Example Log Output

```
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Starting single CSV scan
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Found 1 CSV file(s) to process in /incoming
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Processing CSV file: data.csv
DEBUG 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Processing row: email=user@example.com, zip=90210
DEBUG 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Calling ZIP API for zip=90210
DEBUG 2025-11-01 19:16:30 csv_processor.management.commands.process_csv ZIP API returned: state=California, city=Beverly Hills
DEBUG 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Sending email to user@example.com
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Email sent successfully to user@example.com
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Completed processing data.csv: 10/10 rows successful, 0 failed
INFO 2025-11-01 19:16:30 csv_processor.management.commands.process_csv Moving processed file to /processed/data_20251101_191630.csv
```

## Testing Logging

When testing, you can capture and verify log messages:

```python
import logging
from django.test import TestCase

class LoggingTestCase(TestCase):
    def test_logging(self):
        with self.assertLogs('csv_processor', level='INFO') as cm:
            # Code that triggers logging
            process_csv_file()
            
        # Verify log messages
        self.assertIn('Processing CSV file', cm.output[0])
```

## Resources

- [Django Logging Documentation](https://docs.djangoproject.com/en/4.2/topics/logging/)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)

## Future Enhancements

Potential improvements to logging:
- [ ] Add structured logging (JSON format) for production
- [ ] Implement log rotation for the file handler
- [ ] Add application performance monitoring (APM) integration
- [ ] Create custom log filters for sensitive data
- [ ] Add correlation IDs for tracking requests across logs
