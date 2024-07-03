
## LLM Threat Analysis Validator

This Python script is designed to validate and analyze potential threats to Large Language Models (LLMs) by processing input data, fetching related web content, and using the Claude API to validate and suggest corrections for various threat categories and impacts.

### Features

* Reads input data from an Excel file
* Fetches and processes web content (both HTML and PDF)
* Uses the Claude API to validate threat categories and impacts
* Writes results to an Excel file and a text log file
* Implements rate limiting for API calls

### Prerequisites

* Python 3.x
* Required Python packages: pandas, requests, PyPDF2, beautifulsoup4, python-dotenv, anthropic, langdetect

### Setup

1. Install the required packages:
   ```
   pip install pandas requests PyPDF2 beautifulsoup4 python-dotenv anthropic langdetect
   ```

2. Create a `.env` file in the same directory as the script and add your Claude API key:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

3. Prepare an input Excel file named `input.xlsx` with the required columns.

### Key Components

1. **Data Structures**: The script defines several dictionaries to categorize assets, life cycle stages, threat categories, and impact categories.

2. **File Handling**:
   - Reads input from `input.xlsx`
   - Writes output to `output.xlsx`
   - Logs details to `result.txt`

3. **Web Content Fetching**:
   - `get_pdf_content()`: Extracts text from PDF files
   - `get_html_content()`: Extracts text from HTML pages
   - `fetch_content()`: Determines the content type and calls the appropriate function

4. **Language Detection**: Uses the `langdetect` library to ensure the fetched content is in English.

5. **Claude API Integration**:
   - `call_claude_api()`: Constructs the prompt and makes the API call
   - Implements rate limiting (30 calls per minute, max 30,000 tokens)

6. **Data Processing**:
   - Iterates through each row of the input data
   - Fetches related web content
   - Calls the Claude API for validation
   - Updates the output with the API response

### Main Workflow

1. Load the input Excel file
2. Process each row (skipping the first two rows)
3. Fetch web content based on the provided link
4. Check if the content is in English
5. If English, prepare the context and row content for the API call
6. Call the Claude API for validation
7. Update the 'Claude-Review' column with the API response
8. Save results to the output Excel file and log file
9. Implement rate limiting between API calls

### Output

- An updated Excel file (`output.xlsx`) with a new 'Claude-Review' column containing the validation results
- A text file (`result.txt`) logging all prompts sent to the API and the responses received

### Error Handling

The script includes error handling for API calls and file operations, logging any errors to both the console and the `result.txt` file.

### Rate Limiting

To comply with API usage limits, the script implements a rate limiting mechanism:
- Maximum 30 calls per minute
- Maximum 30,000 tokens per minute
- Waits for 61 seconds between each row processing

### Customization

You can modify the `assets`, `life_cycle`, `threat_categories`, and `impact_categories` dictionaries to update the categories used for validation.

### Note

Ensure you have the necessary permissions and comply with the terms of service for the Claude API and any websites you're fetching content from.

This script is designed for threat analysis and validation in the context of LLMs. Always use it responsibly and in compliance with relevant laws and regulations.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/1990516/decf57aa-1f80-4a78-8970-dcecfaeaf3b3/paste.txt
