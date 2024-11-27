from fastapi import UploadFile
import fitz
import os
import tempfile
import time

async def parse_resume_text(file):
    try:
        # Create a temporary file to save the uploaded file content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(await file.read())  # Write the uploaded file content to the temp file
            temp_file.close()  # Close the temp file so it's not being used when we try to remove it

        # Now you can process the resume text from the temp file
        resume_text = extract_resume_text(temp_file_path)

        # Add a small delay before removing the temp file to ensure no other process is using it
        time.sleep(1)

        # Clean up the temporary file after processing
        os.remove(temp_file_path)
        return resume_text

    except Exception as e:
        print(f"Error while processing the resume: {str(e)}")
        raise
    
def extract_resume_text(temp_file_path):
    doc = fitz.open(temp_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text