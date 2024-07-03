import pandas as pd
import requests
import time
from PyPDF2 import PdfReader
from io import BytesIO
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic
import os
import io
import langdetect

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv('CLAUDE_API_KEY')

# Initialize prompt counter and token counter
prompt_counter = 1
token_counter = 0
last_reset_time = time.time()

# Define the assets and their categories
assets = {
    "Data assets": ["Training data", "Fine-tune training data", "Data for retrieval to add to prompt", "Model input data (prompt)", "User session data", "Model output data", "Model parameters (weights)", "Model hyper parameters", "Log data"],
    "LLM-Ops Environment asset": ["Cloud running the development environment", "Cloud running the model", "Cloud running the AI applications", "Hybrid and multi-cloud infrastructure", "Access control(IAM, Network)", "Continuous monitoring", "Cloud to host training data"],
    "Model": ["Foundation Model", "Fine-Tuned Model", "Open Source vs. Closed Source Models"],
    "Orchestrated Services": ["caching services", "security gateways such as LLM gateway", "monitoring services", "optimization services", "customization and integration (with other systems and/or apps)", "LLM General agents (not just stateless and workflow but rather also monitoring agents, data processor agent, explainability agent, optimization, scaling and collaboration agents)"],
    "AI Applications": ["AI applications"]
}

# Define the life cycle stages and their categories
life_cycle = {
    "Preparation": ["Data Collection", "Data Curation", "Data storage", "Compute/Cloud", "Skills and Expertise"],
    "Development": ["Design", "Development Supply chain", "Training"],
    "Evaluation/Validation": ["Evaluation", "Validation", "Re-Evaluation"],
    "Deployment": ["Orchestration", "AI Services Supply Chain", "Applications"],
    "Delivery": ["Operation", "Maintenance", "Continuous Improvement"],
    "Service Retirement": ["Service Retirement"]
}

# Define the threat categories and their definitions
threat_categories = {
    "Evasion - Model Manipulation": "This category involves attempts to evade detection or manipulate the LLM model to produce inaccurate or misleading results. It encompasses techniques such as prompt injection (adversarial inputs), which aim to exploit vulnerabilities in the model's understanding and decision-making processes.",
    "Data Poisoning": "Data poisoning refers to the malicious manipulation of training data used to train the LLM model. Attackers may inject false or misleading data points into the training set, leading the model to learn incorrect patterns or make biased predictions.",
    "Sensitive Data Disclosure": "This category encompasses threats related to the unauthorized access, exposure, or leakage of sensitive information processed or stored by the LLM service. Sensitive data may include personal information, proprietary data, or confidential documents, the exposure of which could lead to privacy violations or security breaches.",
    "Model Stealing": "Model stealing involves unauthorized access to or replication of the LLM model by malicious actors. Attackers may attempt to reverse-engineer the model architecture or extract proprietary algorithms and parameters, leading to intellectual property theft or the creation of unauthorized replicas.",
    "Failure / Malfunctioning": "This category covers various types of failures or malfunctions within the LLM service, including software bugs, hardware failures, or operational errors. Such incidents can disrupt service availability, degrade performance, or compromise the accuracy and reliability of the LLM model's outputs.",
    "Insecure Supply Chain": "Insecure supply chain refers to vulnerabilities introduced through third-party components, dependencies, or services integrated into the LLM ecosystem. Weaknesses in the supply chain, such as compromised software libraries or hardware components, can be exploited to compromise the overall security and trustworthiness of the LLM service.",
    "Insecure Apps/Plugins": "This category pertains to vulnerabilities introduced by third-party applications, plugins, functional calls, or extensions that interact with the LLM service. Insecure or maliciously designed apps/plugins may introduce security loopholes, elevate privilege levels, or facilitate unauthorized access to sensitive resources.",
    "Denial of Service (DoS)": "Denial of Service attacks aim to disrupt the availability or functionality of the LLM service by overwhelming it with a high volume of requests or malicious traffic. DoS attacks can render the service inaccessible to legitimate users, causing downtime, service degradation, or loss of trust.",
    "Loss of Governance / Compliance": "This category involves the risk of non-compliance with regulatory requirements, industry standards, or internal governance policies governing the operation and use of the LLM service. Failure to adhere to governance and compliance standards can result in legal liabilities, financial penalties, or reputational damage."
}

# Define the impact categories and their definitions
impact_categories = {
    "Loss of Confidentiality": "The unauthorized access, exposure, or leakage of sensitive information, leading to a breach of confidentiality.",
    "Loss of Integrity": "The unauthorized modification or alteration of data or systems, compromising their integrity and trustworthiness.",
    "Loss of Availability": "The disruption or unavailability of services, systems, or data, preventing legitimate access or use."
}

# Define the input and output file names
input_file_name = 'input.xlsx'
output_file_name = 'output.xlsx'

# Load the input file
df = pd.read_excel(input_file_name)

# Add the new column for Claude-Review if it doesn't exist
if 'Claude-Review' not in df.columns:
    df['Claude-Review'] = ''

# Function to download and parse PDF content
def get_pdf_content(url):
    response = requests.get(url)
    pdf_reader = PdfReader(BytesIO(response.content))
    content = ''
    for page_num in range(len(pdf_reader.pages)):
        content += pdf_reader.pages[page_num].extract_text()
    return content

# Function to parse HTML content
def get_html_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

# Function to fetch content based on the link type
def fetch_content(link):
    if link.endswith('.pdf'):
        return get_pdf_content(link)
    else:
        return get_html_content(link)

# Function to detect language
def is_english(text):
    try:
        return langdetect.detect(text) == 'en'
    except:
        return False

# Function to call Claude API using Anthropics API client
def call_claude_api(context, row_content):
    global prompt_counter, token_counter, last_reset_time
    client = anthropic.Anthropic(api_key=api_key)
    
    # Construct the user input part of the prompt
    user_input = "Here is the user input for this row:\n"
    focused_columns = [
        'HIGH LEVEL THREAT CATEGORY', 'AFFECTED_LIFECYCLE L1', 'AFFECTED_LIFECYCLE L2', 
        'AFFECTED_ASSET L1 (1)', 'AFFECTED_ASSET L1 (x2)_if multiple assets are affected', 
        'AFFECTED_ASSET L2 (1)', 'AFFECTED_ASSET L2 (2)_if multiple assets are affected', 
        'AFFECTED_ASSET L2 (3)_if multiple assets are affected', 'IMPACT (Only CIA triad)', 
        'IMPACT (2)', 'AI_SPECIFIC?', 'AI_RELATED_RISK?'
    ]
    
    for column in focused_columns:
        if column in row_content:
            user_input += f"{column}: {row_content[column]}\n"
    
    prompt = f"""Using the following context from the web: {context} {user_input} 
    Here are the defined categories and options: 
    Assets: {assets} 
    Life Cycle Stages: {life_cycle} 
    Threat Categories: {threat_categories} 
    Impact Categories: {impact_categories} 
    Validate the user's input for each column. Follow these instructions carefully: 
    1. For any incorrect columns, provide the following information: 
        - Column name 
        - Incorrect value 
        - Suggested correct value (must be from the defined categories above) 
        - A short reason for the correction based on the content from web, limited it to 30 tokens 
    2. If multiple columns are incorrect, separate each error with a new line. 
    3. Do not output anything for correct columns. 
    4. If ALL columns are correct, respond with exactly: "correct" 
    5. Note that level 2 items are inside [ ], and each cell can have more than 1 item. 
    6. Only focus on validating the following columns:
    """

    print("Prompt sent to Claude API:")
    print(prompt)
    
    # Save the prompt to result.txt
    write_to_result_txt(f"Prompt {prompt_counter}:\n{prompt}\n\n\n")
    
    # Check and reset token counter if a minute has passed
    current_time = time.time()
    if current_time - last_reset_time >= 60:
        token_counter = 0
        last_reset_time = current_time
    
    # Check if we've exceeded the rate limit
    if prompt_counter > 30 or token_counter >= 30000:
        time.sleep(60 - (current_time - last_reset_time))
        token_counter = 0
        prompt_counter = 1
        last_reset_time = time.time()
    
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if response:
            response_text = response.content[0].text
            # Update token counter
            token_counter += response.usage.output_tokens + response.usage.input_tokens
            # Save the response to result.txt
            write_to_result_txt(f"Response {prompt_counter}:\n{response_text}\n\n\n")
            prompt_counter += 1
            return response_text
        else:
            error_message = "Error: Unable to get response from Claude API"
            # Save the error message to result.txt
            write_to_result_txt(f"Error {prompt_counter}:\n{error_message}\n\n\n")
            prompt_counter += 1
            return error_message
    except Exception as e:
        error_message = f"Error calling Claude API: {e}"
        print(error_message)
        # Save the error message to result.txt
        write_to_result_txt(f"Error {prompt_counter}:\n{error_message}\n\n\n")
        prompt_counter += 1
        return f"Error: API call failed - {e}"

# Function to write to result.txt
def write_to_result_txt(content):
    mode = 'a' if os.path.exists('result.txt') else 'w'
    with io.open('result.txt', mode, encoding='utf-8') as f:
        f.write(content)

# Function to save to output.xlsx
def save_to_output_xlsx(df):
    if os.path.exists(output_file_name):
        # If file exists, read existing data and update it
        existing_df = pd.read_excel(output_file_name)
        # Update existing data with new data
        existing_df.update(df)
        existing_df.to_excel(output_file_name, index=False)
    else:
        # If file doesn't exist, create new file
        df.to_excel(output_file_name, index=False)

# Get the focused column names
def get_focused_columns():
    return [
        'HIGH LEVEL THREAT CATEGORY', 'AFFECTED_LIFECYCLE L1', 'AFFECTED_LIFECYCLE L2', 
        'AFFECTED_ASSET L1 (1)', 'AFFECTED_ASSET L1 (x2)_if multiple assets are affected', 
        'AFFECTED_ASSET L2 (1)', 'AFFECTED_ASSET L2 (2)_if multiple assets are affected', 
        'AFFECTED_ASSET L2 (3)_if multiple assets are affected', 'IMPACT (Only CIA triad)', 
        'IMPACT (2)', 'AI_SPECIFIC?', 'AI_RELATED_RISK?'
    ]

# Print the column names for verification
focused_columns = get_focused_columns()
print("Focused columns:", focused_columns)

# Process each row starting from the 3rd row
for idx, row in df.iterrows():
    if idx < 1:  # Skip the first two rows (heading and empty row)
        continue
    
    # Fetch content from the link
    link = row['PRIMARY_CONTENT_LINK']
    content = fetch_content(link)
    
    # Check if the content is in English
    if not is_english(content):
        df.at[idx, 'Claude-Review'] = "The web content is not in English, cannot validate"
    else:
        # Prepare context and row content for the API call
        row_content = {column: row[column] for column in focused_columns if column in row.index}
        # Call the Claude API
        response = call_claude_api(content, row_content)
        # Process the response and update the 'Claude-Review' column
        df.at[idx, 'Claude-Review'] = response
    
    # Flush results to output.xlsx and result.txt after processing each row
    save_to_output_xlsx(df)
    write_to_result_txt(f"Processed row {idx+1}\n\n")
    
    # Implement rate limiting (30 calls per minute)
    time.sleep(61)

print(f"Processing complete. Output saved to {output_file_name}")
