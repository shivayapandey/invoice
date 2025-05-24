# Invoice Extractor

> **Extract, analyze, and download invoices from PDFs  **

Invoice Extractor is a modern tool for extracting structured invoice data from one or many PDF files. Upload your invoices—InvoiceFusion leverages advanced PDF parsing and Large Language Models (LLMs) to extract key fields (invoice numbers, dates, addresses, line items, totals, payment terms, and more), then allows you to download all results as a single PDF or view the raw extracted data.

## ✨ Features
- **Multi-invoice extraction:** Upload multiple PDFs at once, batch process, and consolidate results.
- **LLM-powered extraction:** Uses Groq’s Llama-3 model for accurate, context-aware parsing of real-world invoices.
- **Smart PDF parsing:** Handles tables, lists, and mixed content with Unstructured.
- **Download as PDF:** Get all extracted invoices in a single, well-formatted PDF.
- **Interactive UI:** Built with Streamlit for a smooth user experience.
- **No manual template setup:** Works with many invoice formats out of the box.


## 🛠️ Tech Stack
- [Python 3.8+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Unstructured](https://github.com/Unstructured-IO/unstructured)
- [langchain-groq](https://python.langchain.com/docs/integrations/llms/groq)
- [ReportLab](https://www.reportlab.com/)
- [OpenCV (headless)](https://pypi.org/project/opencv-python-headless/)

## 📦 Installation

```bash
git clone https://github.com/shivayapandey/invoice.git
cd invoice
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 🔑 Setup

1. **API Key:**  
   Get a Groq API key and set it in your environment:
   ```bash
   export GROQ_API_KEY=your_groq_key_here
   ```
   Or add it to a `.env` file.

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## 📂 Usage

1. Open the Streamlit app.
2. Upload one or more invoice PDFs.
3. Wait for extraction and review the results.
4. Download the consolidated invoice PDF or view the extracted text.

## 🤖 How does it work?
- PDFs are parsed with Unstructured for robust text and table extraction.
- Extracted text is sent to a Groq LLM (Llama-3) with a precise prompt to extract invoice fields.
- All invoice data is formatted and made available for download or review.

## ❓ Troubleshooting
- Ensure PDFs are not password protected and contain selectable/searchable text.
- Some complex or poorly-scanned invoices may not extract perfectly.
- If extraction fails, double-check your Groq API key and Streamlit logs.

## 📝 License
MIT
