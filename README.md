# Enterprise Company Research Analyst Agent (Python Version)

A high-performance company research agent built entirely in **Python** using **Streamlit** for the interactive chat interface, **BeautifulSoup4** for crawling, **FPDF2** for generating PDF reports, and **OpenRouter** for AI analysis.

---

## 🚀 Key Features

1. **Intelligent Company Resolution**: Automatically searches Google via Serper.dev to find the official website when a company name (e.g. "Stripe") is submitted.
2. **BeautifulSoup Crawling**: Crawls up to 7 pages (About, Products, services, Contact, etc.) of the resolved domain, removing junk tags (header, footer, nav, script, style) and deduplicating paths.
3. **Structured AI Insights**: Queries OpenRouter models (Gemini, Llama, GPT, Claude) to synthesize summaries, key products, and realistic operational pain points.
4. **Professional PDF Reports**: Generates customized report PDFs using FPDF2 with corporate theme styling, lines, grids, and automatic page counting.
5. **Discord Integration**: Pushes candidate name/email and uploads the PDF report as an attachment to a specified channel via Bot token.
6. **Streamlit UI/UX**: Chat interface built with Streamlit containing:
   - Sidebar settings to configure keys, applicant details, and selected model.
   - Collapsible live-progress indicators showing crawling and API progress status.
   - Elegant report cards with quick PDF download buttons.

---

## ⚙️ Environment Variables Setup

Create a `.env` file in the project root directory (or enter keys directly in the sidebar):

```bash
# Serper.dev API key for Google searches
SERPER_API_KEY=your_serper_api_key_here

# OpenRouter API key for LLM queries
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## 💻 Local Setup & Execution

### Prerequisites
Ensure Node.js and Python 3.10+ are installed. A virtual environment `.venv` is already configured in this repository.

### 1. Install Dependencies
Run pip inside the virtual environment:
```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

### 2. Run Web Application
Boot the Streamlit server locally:
```bash
.venv\Scripts\streamlit.exe run app.py
```
This will open the application in your browser automatically (usually at `http://localhost:8501`).

---

## 📂 Project Architecture

```
vikas/
├── app.py                  # Streamlit entry point (UI & Chat controls)
├── requirements.txt        # Streamlit, BeautifulSoup, FPDF2, and requests
├── utils/
│   ├── crawler.py          # BS4 website parsing
│   ├── discord_client.py   # Discord Bot upload delivery (multipart PDF)
│   ├── openrouter.py       # OpenRouter completion prompt client
│   ├── pdf_generator.py    # FPDF2 layout builder
│   └── serper.py           # Serper.dev query helper
└── task.docx               # Project guidelines reference doc
```

---

## 🧪 Verification & Walkthrough

The application has been verified for compiler success and runs cleanly. A comprehensive walkthrough can be accessed in [walkthrough.md](file:///C:/Users/sinha/.gemini/antigravity-ide/brain/0aee2358-cdb5-4e37-9eda-7794b2f797df/walkthrough.md).
