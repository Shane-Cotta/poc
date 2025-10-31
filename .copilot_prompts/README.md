# Copilot Prompt Logs

This directory contains logs and documentation of prompts used during the development of this project.

## Initial Project Setup (2025-10-30)

### Prompt 1: Create Django Project Structure
**Prompt:**
"Create a Django project called csv_project with an app called csv_processor for processing CSV files"

**Result:**
- Created Django project structure
- Created csv_processor app
- Configured settings.py with app registration

### Prompt 2: Define Models
**Prompt:**
"Create models to track CSV processing records and individual email records with fields for zip code, state, city, and success status"

**Result:**
- Created CSVProcessingRecord model to track overall file processing
- Created EmailRecord model to track individual row processing
- Added relationship between models
- Registered models in admin

### Prompt 3: Implement Management Command
**Prompt:**
"Create a Django management command that:
- Scans incoming/ folder for CSV files
- Reads zip and email from each CSV row
- Calls zippopotam.us API to get state/city
- Sends email using Django console backend
- Moves processed files to processed/ folder
- Runs continuously every 2 minutes"

**Result:**
- Created process_csv management command
- Implemented CSV scanning and processing logic
- Added API integration for zip code lookup
- Configured email sending with console backend
- Added file movement to processed directory
- Implemented continuous scanning with configurable interval

### Prompt 4: Add Tests
**Prompt:**
"Create comprehensive tests for models and the management command including edge cases"

**Result:**
- Added model tests for CSVProcessingRecord and EmailRecord
- Created command tests with mocking for external dependencies
- Added tests for error handling and edge cases
- Used temporary directories for isolated testing

### Prompt 5: Configure Development Container
**Prompt:**
"Create a .devcontainer configuration for VS Code with Python, Django, and GitHub Copilot extensions"

**Result:**
- Created devcontainer.json with Python 3.11 image
- Configured VS Code settings for Python development
- Added GitHub Copilot and Copilot Chat extensions
- Set up post-create command to install dependencies and run migrations
- Configured port forwarding for Django development server

## Development Tips

### Useful Copilot Prompts for This Project

1. **Testing:**
   - "Generate a test case for CSV processing with invalid data"
   - "Create a mock for the zippopotam.us API response"
   - "Add test for email sending failure"

2. **Features:**
   - "Add logging to the CSV processing command"
   - "Implement retry logic for API failures"
   - "Create a Django admin action to reprocess failed records"

3. **Debugging:**
   - "Why is the CSV file not being moved to processed folder?"
   - "How to debug email sending in Django console backend?"
   - "Explain the error 'zip_code not found in CSV'"

4. **Enhancements:**
   - "Add support for processing Excel files"
   - "Implement rate limiting for API calls"
   - "Create a dashboard view to monitor processing status"

## Best Practices Discovered

1. **CSV Processing:**
   - Always handle missing fields gracefully
   - Use DictReader for column-based access
   - Close file handles properly

2. **API Integration:**
   - Use timeouts on all requests
   - Implement error handling for network failures
   - Cache API responses when appropriate

3. **Django Management Commands:**
   - Support both one-time and continuous execution modes
   - Use command arguments for configuration
   - Provide clear console output for monitoring

4. **Testing:**
   - Use temporary directories for file operations
   - Mock external API calls
   - Test both success and failure scenarios

## Project Evolution

This project was built incrementally with the following approach:
1. Set up basic Django structure
2. Define data models
3. Implement core processing logic
4. Add tests
5. Configure development environment
6. Document with README and prompts

Each step was validated before moving to the next, ensuring a solid foundation.
