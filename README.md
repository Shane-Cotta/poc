# Django CSV Processor POC

A Django-based proof of concept that automatically processes CSV files containing ZIP codes and email addresses. The system scans for CSV files, enriches them with location data from the Zippopotam API, and sends emails to the addresses.

## Features

- 🔄 Automatic scanning of incoming folder every 2 minutes
- 📧 Email processing using Django's console backend
- 🌍 ZIP code to state/city lookup via Zippopotam API
- 📊 Database tracking of all processing activities
- 🧪 Comprehensive test suite
- 🐳 VS Code Dev Container with GitHub Copilot support
- 📝 Detailed prompt logging for Copilot usage

## Architecture

### Components

1. **Django App (`csv_processor`)**: Core application logic
2. **Models**:
   - `CSVProcessingRecord`: Tracks each CSV file processed
   - `EmailRecord`: Tracks individual email/ZIP entries
3. **Management Command (`process_csv`)**: Handles CSV scanning and processing
4. **Admin Interface**: View and manage processing records

### Workflow

```
incoming/file.csv → Scan → Parse → API Lookup → Send Email → processed/file_timestamp.csv
                      ↓
                   Database Record
```

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Shane-Cotta/poc.git
cd poc
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create directories (if not already present):
```bash
mkdir incoming processed
```

5. (Optional) Copy sample data to test:
```bash
cp sample_data.csv incoming/
```

### Usage

#### Run Once

Process all CSV files in the incoming folder once:

```bash
python manage.py process_csv --once
```

#### Continuous Processing

Run continuously, scanning every 2 minutes (default):

```bash
python manage.py process_csv
```

Or specify a custom interval (in seconds):

```bash
python manage.py process_csv --interval 120
```

### CSV Format

CSV files should have the following format:

```csv
zip,email
90210,user1@example.com
10001,user2@example.com
02101,user3@example.com
```

### Testing

Run the test suite:

```bash
python manage.py test csv_processor
```

### Admin Interface

1. Create a superuser:
NOTE: current sqllite db user is vscode:password
```bash
python manage.py createsuperuser
```

2. Run the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```

3. Access the admin at http://localhost:8000/admin/

## Development with VS Code + Copilot

### Using Dev Container

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted (or CMD+SHIFT+P on mac and search "Rebuild in container")
4. The container will automatically:
   - Install Python dependencies
   - Run database migrations
   - Configure GitHub Copilot

### Run & Debug Profiles

- Open the Run and Debug view in VS Code to access project-ready launch profiles from `.vscode/launch.json`.
- Use `Django: Run All Tests` to debug the full Django test suite (`python manage.py test`).
- Use `Django: Debug process_csv Command` to step through a re-occuring execution of `python manage.py process_csv --once` while processing local CSV fixtures.

### Copilot Resources

Check the `.copilot_prompts/` directory for:
- Prompt examples and best practices
- Development tips
- Common patterns used in this project
- **Logging best practices** - Django logging standards and implementation guide

## Project Structure

```
poc/
├── .copilot_prompts/        # Copilot prompt logs and documentation
├── .devcontainer/           # VS Code dev container configuration
├── .vscode/                 # VS Code Settings
├── csv_processor/           # Main Django app
│   ├── management/
│   │   └── commands/
│   │       └── process_csv.py  # CSV processing command
│   ├── migrations/
│   ├── admin.py            # Admin interface configuration
│   ├── models.py           # Data models
│   └── tests.py            # Test suite
├── csv_project/            # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py
│   └── wsgi.py
├── incoming/               # Place CSV files here
├── processed/              # Processed files moved here
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Configuration

Configuration is in `csv_project/settings.py`:

- `EMAIL_BACKEND`: Set to console backend (prints emails to console)
- `CSV_INCOMING_DIR`: Directory to scan for CSV files
- `CSV_PROCESSED_DIR`: Directory for processed files
- `ZIP_API_URL`: Zippopotam API endpoint
- `LOGGING`: Logging configuration with console and file handlers

### Logging

The application uses Python's `logging` module following Django best practices:

- **Log File**: `csv_processor.log` in project root (gitignored)
- **Log Levels**:
  - INFO: Normal operations (file processing, completions)
  - WARNING: Recoverable issues (missing data, failed rows)
  - ERROR: Serious failures (file errors, API failures)
  - DEBUG: Detailed diagnostic information
- **Handlers**: Console output and file logging
- **Format**: `{levelname} {asctime} {name} {message}`

To view logs in real-time:
```bash
tail -f csv_processor.log
```

For more details, see [Logging Best Practices](.copilot_prompts/LoggingBestPractices.md).

## API Integration

The project uses the [Zippopotam.us API](https://api.zippopotam.us/) to convert ZIP codes to state and city information:

- Endpoint: `https://api.zippopotam.us/us/{zip}`
- No API key required
- Rate limiting: Be respectful of the free service

## Email Backend

Uses Django's console email backend for development:
- Emails are printed to the console
- No SMTP server required
- To use a real email backend, update `EMAIL_BACKEND` in settings.py

## Database

Uses SQLite by default (`db.sqlite3`):
- Suitable for development and small-scale use
- For production, configure PostgreSQL or MySQL in settings.py

## Troubleshooting

### CSV Files Not Processing

1. Check that files are in the `incoming/` directory
2. Verify CSV has correct format (zip,email columns)
3. Check console output for error messages
4. Review database records in admin interface

### API Errors

1. Verify internet connectivity
2. Check ZIP code format (5 digits)
3. Review error messages in EmailRecord.error_message
4. API may be temporarily unavailable

### Email Not Sending

1. Check that EMAIL_BACKEND is set to console backend
2. Look for email output in console
3. For production email, configure SMTP settings

## Future Enhancements

Potential improvements:
- [ ] Support for Excel files (.xlsx)
- [ ] Rate limiting for API calls
- [ ] Retry logic for failed API requests
- [ ] Web dashboard for monitoring
- [ ] Multiple email templates
- [ ] Batch processing optimization
- [ ] Celery integration for async processing
- [ ] Support for additional data sources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python manage.py test`
5. Submit a pull request

## License

This is a proof of concept project for demonstration purposes.

## Contact

For questions or issues, please open an issue on GitHub.
