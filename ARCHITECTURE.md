# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Django CSV Processor POC                      │
└─────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │  User Action │
                        │ (Copy CSV to │
                        │  incoming/)  │
                        └──────┬───────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Management Command                            │
│                   python manage.py process_csv                   │
│                   (Runs every 2 minutes)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Scan incoming/  │
                  │   for *.csv      │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Parse CSV     │
                  │ (Extract zip &  │
                  │     email)      │
                  └────────┬─────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
    ┌─────────────┐              ┌─────────────────┐
    │  API Call   │              │  Database Save  │
    │ zippopotam  │◄─────────────┤ CSVProcessing   │
    │  .us/us/    │              │    Record       │
    │   {zip}     │              └─────────────────┘
    └──────┬──────┘                       │
           │                              │
           ▼                              │
    ┌─────────────┐                       │
    │   Extract   │                       │
    │ State & City│                       │
    └──────┬──────┘                       │
           │                              │
           ▼                              │
    ┌─────────────┐                       │
    │ Send Email  │                       │
    │  (Console   │                       │
    │   Backend)  │                       │
    └──────┬──────┘                       │
           │                              │
           ▼                              │
    ┌─────────────┐                       │
    │ Save Email  │◄──────────────────────┘
    │   Record    │
    │ (Success/   │
    │   Failure)  │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Move CSV   │
    │     to      │
    │ processed/  │
    │ (Timestamp) │
    └─────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                       Data Flow Example                          │
└─────────────────────────────────────────────────────────────────┘

Input CSV (incoming/data.csv):
┌────────────────────────┐
│ zip,email              │
│ 90210,user@example.com │
└────────────────────────┘
           │
           ▼
API Response:
┌────────────────────────┐
│ State: California      │
│ City: Beverly Hills    │
└────────────────────────┘
           │
           ▼
Email Content (Console):
┌────────────────────────────────────────┐
│ To: user@example.com                   │
│ Subject: Location Info for ZIP 90210   │
│ Body:                                  │
│   City: Beverly Hills                  │
│   State: California                    │
└────────────────────────────────────────┘
           │
           ▼
Database Record:
┌────────────────────────────────────────┐
│ EmailRecord                            │
│ - email: user@example.com              │
│ - zip: 90210                           │
│ - state: California                    │
│ - city: Beverly Hills                  │
│ - success: True                        │
└────────────────────────────────────────┘
           │
           ▼
Output File:
┌────────────────────────────────────────┐
│ processed/data_20231030_120000.csv     │
└────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      Component Overview                          │
└─────────────────────────────────────────────────────────────────┘

Django Project (csv_project)
├── Models
│   ├── CSVProcessingRecord
│   │   ├── filename
│   │   ├── total_rows
│   │   ├── successful_rows
│   │   ├── failed_rows
│   │   └── status
│   └── EmailRecord
│       ├── email_address
│       ├── zip_code
│       ├── state
│       ├── city
│       ├── success
│       └── error_message
│
├── Management Command (process_csv)
│   ├── scan_incoming_folder()
│   ├── process_csv_files()
│   ├── get_location_from_zip()
│   ├── send_email_to_address()
│   └── move_to_processed()
│
├── Admin Interface
│   ├── CSVProcessingRecordAdmin
│   └── EmailRecordAdmin
│
└── Tests (8 tests)
    ├── Model tests
    ├── Command tests
    ├── API error handling
    └── Edge case tests


┌─────────────────────────────────────────────────────────────────┐
│                    Technology Stack                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Django     │  │   Requests   │  │   SQLite     │
│    4.2.x     │  │    2.31.x    │  │  (Default)   │
└──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Python    │  │  VS Code     │  │   GitHub     │
│    3.11+     │  │ Dev Container│  │   Copilot    │
└──────────────┘  └──────────────┘  └──────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
└─────────────────────────────────────────────────────────────────┘

Zippopotam API
┌────────────────────────────────────────────────────┐
│ URL: https://api.zippopotam.us/us/{zip}            │
│ Method: GET                                        │
│ Timeout: 5 seconds                                 │
│ Response: JSON with state, city, places            │
└────────────────────────────────────────────────────┘

Email Backend (Console)
┌────────────────────────────────────────────────────┐
│ Type: django.core.mail.backends.console.EmailBackend
│ Output: Prints emails to console/stdout            │
│ Use: Development/testing purposes                  │
└────────────────────────────────────────────────────┘
