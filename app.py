from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import io
import base64

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        return f"Error in generating response: {str(e)}"

def input_pdf_setup(uploaded_file):
    try:
        if uploaded_file is not None:
            # Open the PDF using PyMuPDF
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            # Extract the first page as an image
            first_page = pdf_document[0]
            pix = first_page.get_pixmap()
            
            # Convert the image to a byte array
            img_byte_arr = io.BytesIO()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(img_byte_arr, format="JPEG")
            img_byte_arr = img_byte_arr.getvalue()
            
            # Prepare the content for the Gemini API
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }
            ]
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded")
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input Fields
input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Tell Me About the Resume")
submit2 = st.button("How Can I Improve My Skills")
submit3 = st.button("Percentage Match")

# Input Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are an expert career advisor. Suggest ways to improve the applicant's skills based on the provided resume and job description.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Evaluate the resume against the provided job description. Give the percentage match, highlight missing keywords, and provide final thoughts.
"""

# Button Logic
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt1)
            st.subheader("The Response is:")
            st.write(response)
    else:
        st.error("Please upload the resume.")

elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt2)
            st.subheader("Suggestions to Improve Skills:")
            st.write(response)
    else:
        st.error("Please upload the resume.")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt3)
            st.subheader("The Response is:")
            st.write(response)
    else:
        st.error("Please upload the resume.")
