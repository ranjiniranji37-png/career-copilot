# AI Productivity Toolkit — Prompt Engineering Module

A beginner-friendly demo project for experimenting with prompt templates for:
- summarizing text
- drafting content
- classifying feedback
- generating study/interview practice questions

## Important note
This starter version uses simple Python rules and templates. It does **not** call a real LLM/API yet. To make it a real Generative AI application, connect an LLM provider and store the API key securely (never commit API keys to GitHub).

## Run locally
1. Install Python 3.10 or newer.
2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```

## Run in Google Colab
1. Upload `notebooks/Module2_Prompt_Engineering.ipynb` to Google Colab.
2. Choose **Runtime → Run all**.
3. The notebook runs with Python's built-in libraries; no API key is required.

## Project structure
- `app.py` — Streamlit demo app
- `notebooks/Module2_Prompt_Engineering.ipynb` — notebook for Colab
- `toolkit/prompts.py` — prompt templates and helper functions
- `prompts.json` — editable prompt templates
- `reports/test_report.md` — basic test checklist/results
- `linkedin_post.md` — optional LinkedIn post draft
- `requirements.txt` — app dependencies

## GitHub upload
Extract this ZIP first, then upload the **contents of the extracted folder** to a public GitHub repository. Do not upload only the ZIP if the assignment asks for project files.
