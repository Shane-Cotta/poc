# Quick Reference Guide

## Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser

# Create directories
mkdir incoming processed
```

## Processing Commands

```bash
# Process CSV files once
python manage.py process_csv --once

# Run continuously (default: every 2 minutes)
python manage.py process_csv

# Run with custom interval (in seconds)
python manage.py process_csv --interval 60
```

## Testing & Validation

```bash
# Run all tests
python manage.py test csv_processor

# Run tests with verbose output
python manage.py test csv_processor -v 2

# Run Django system check
python manage.py check
```

## Development Server

```bash
# Start development server
python manage.py runserver

# Start on specific port
python manage.py runserver 8080

# Access admin interface
# http://localhost:8000/admin/
```

## Database Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell

# View database records
python manage.py shell -c "from csv_processor.models import *; print(CSVProcessingRecord.objects.all())"
```

## CSV File Format

Your CSV files should be in this format:

```csv
zip,email
90210,user1@example.com
10001,user2@example.com
02101,user3@example.com
```

## Common Workflows

### Testing the System

1. Copy sample data:
   ```bash
   cp sample_data.csv incoming/
   ```

2. Run the processor once:
   ```bash
   python manage.py process_csv --once
   ```

3. Check the results:
   ```bash
   ls processed/
   python manage.py shell -c "from csv_processor.models import *; print(f'Total records: {CSVProcessingRecord.objects.count()}')"
   ```

### Monitoring Processing

1. Start the processor in one terminal:
   ```bash
   python manage.py process_csv
   ```

2. Add CSV files to the incoming folder:
   ```bash
   cp my_data.csv incoming/
   ```

3. Watch the console output for processing status

### Viewing Results in Admin

1. Create a superuser (if not already done):
   ```bash
   python manage.py createsuperuser
   ```

2. Start the server:
   ```bash
   python manage.py runserver
   ```

3. Open browser to http://localhost:8000/admin/

4. Login and navigate to:
   - CSV Processor → CSV Processing Records (overall file stats)
   - CSV Processor → Email Records (individual email processing)

## Troubleshooting

### No CSV files being processed
- Check that files are in `incoming/` directory
- Verify CSV has correct format (zip,email columns)
- Check console output for errors

### API errors
- Verify internet connectivity
- Check ZIP code format (5 digits, US only)
- Review error messages in EmailRecord.error_message field

### Email not visible
- Emails are printed to console (not sent via SMTP)
- Check the terminal where process_csv is running
- Look for email content in the output

### Database errors
- Run migrations: `python manage.py migrate`
- Check database file exists: `ls -la db.sqlite3`
- Reset database (WARNING: deletes all data):
  ```bash
  rm db.sqlite3
  python manage.py migrate
  ```

## Development with VS Code

### Using Dev Container

1. Open project in VS Code
2. Install "Dev Containers" extension
3. Press F1 → "Dev Containers: Reopen in Container"
4. Wait for container to build and start
5. Dependencies are automatically installed

### GitHub Copilot Tips

- Check `.copilot_prompts/README.md` for prompt examples
- Use Copilot Chat for code explanations
- Ask for test generation with specific scenarios
- Request refactoring suggestions

## Environment Variables (Production)

For production deployment, set these environment variables:

```bash
# Django settings
export DJANGO_SECRET_KEY="your-secret-key-here"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# Database (example for PostgreSQL)
export DATABASE_URL="postgresql://user:password@localhost/dbname"

# Email settings (example for SMTP)
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-password"
export DEFAULT_FROM_EMAIL="noreply@yourdomain.com"
```

## Performance Tips

- For large CSV files, consider increasing `ZIP_API_TIMEOUT`
- Use `--interval` to adjust scan frequency based on volume
- Monitor database size and archive old records periodically
- Consider using Celery for async processing at scale
