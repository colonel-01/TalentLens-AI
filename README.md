<p align="center">
  <img src="assets/banner.png" width="800"/>
</p>

<h1 align="center">TalentLens-AI</h1>

<p align="center">
AI-powered resume parsing and candidate matching system using LLMs.
</p>


TalentLens-AI

An AI-powered resume parsing and candidate evaluation system that extracts structured information from resumes and matches candidate profiles with job requirements.

Overview

TalentLens-AI is designed to convert unstructured resume documents into structured data using document processing and Large Language Models (LLMs).

The objective is to build an intelligent recruitment assistant that can:

Extract important candidate information from resumes
Convert resume content into structured JSON format
Analyze candidate skills and experience
Compare candidate profiles with job descriptions
Generate a suitability score for different roles
Current Features
Resume PDF Extraction
Extracts text from PDF resumes using PyMuPDF
Processes resume documents for further analysis
Structured Information Extraction
Converts extracted resume text into structured JSON
Uses Pydantic models for data validation
LLM-Based Processing
Uses Groq API for intelligent information extraction
Generates consistent structured outputs based on defined schemas
Tech Stack
Backend
Python
PyMuPDF for PDF text extraction
Pydantic for schema validation
Groq API for LLM inference
Environment Management
uv for Python dependency and environment management
Version Control
Git and GitHub
Project Structure
TalentLens-AI/

├── src/
│   ├── res_parser.py
│   └── __init__.py
│
├── test_code/
│
├── data/
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md

Note: The data directory contains resume files and is excluded from version control.

Installation

Clone the repository:

git clone https://github.com/colonel-01/TalentLens-AI.git

Navigate to the project directory:

cd TalentLens-AI

Install dependencies using uv:

uv sync
Environment Setup

Create a .env file in the project root:

GROQ_API_KEY=your_api_key_here
Running the Project

Run the resume parser:

python src/res_parser.py

The system performs the following steps:

Reads the resume PDF
Extracts text from the document
Processes the extracted content using an LLM
Generates structured candidate information

Example output:

{
  "name": "John Doe",
  "skills": [
    "Python",
    "Machine Learning",
    "SQL"
  ],
  "experience": "2 years"
}



Contribution

Contributions and suggestions are welcome.

Feel free to open issues or submit pull requests.

License

This project is licensed under the MIT License.
