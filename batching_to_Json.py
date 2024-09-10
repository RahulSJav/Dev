import pandas as pd
import streamlit as st
import os
import json
from groq import Groq

# Set up the Streamlit app
st.title("Batching with JSONL files")

# Initialize the Groq client with the API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# System message to guide the assistant
st.subheader("Enter the System Prompt")
system_prompt = st.text_area('Type here...')

# Provide the model
st.subheader("Provide the Model")
model_input = st.text_input('Type here...')

# Initialize error flag
error_message = ""

# Upload CSV file
st.subheader("Upload your CSV")
uploaded_file = st.file_uploader("The uploaded file should be CSV", type="csv")

# Check if a file is uploaded and display column selection
if uploaded_file is not None:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)
    column_names = df.columns.tolist()
    selected_column = st.selectbox("Select a column", column_names)
    st.write(f"Selected column: {selected_column}")

if st.button("Convert to JSONL"):
    if not system_prompt or not model_input:
        if not system_prompt:
            error_message += "System prompt is required. 🚨 "
        if not model_input:
            error_message += "Model is required. 🚨 "
    else:
        if uploaded_file is not None:
            tasks = []
        
            for index, row in df.iterrows():
                title = row[selected_column]
                
                task = {
                    "custom_id": f"task-{index}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model_input,
                        "response_format": {
                            "type": "json_object"
                        },
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": title,
                            }
                        ]            
                    }
                }
                
                tasks.append(task)
            
            # Save records to a JSONL file
            jsonl_file_path = "output.jsonl"
            with open(jsonl_file_path, 'w') as f:
                for task in tasks:
                    f.write(json.dumps(task) + '\n')
            
            st.success(f"The records are updated into JSONL format and saved to {jsonl_file_path}.")
        else:
            st.error("No file uploaded.")
    
    if error_message:
        st.error(error_message)


