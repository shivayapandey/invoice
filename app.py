import streamlit as st
import os
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Text, Title, ListItem, Table
from langchain_groq import ChatGroq
import tempfile
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using Unstructured with improved settings"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_file.flush()
        
        try:
            elements = partition_pdf(
                tmp_file.name,
                strategy="hi_res",  # Changed to hi_res for better extraction
                include_metadata=True,
                include_page_breaks=True,
                include_tables=True,
                max_partition=6000
            )
            
            # Improved text extraction with formatting preservation
            text_elements = []
            for element in elements:
                if isinstance(element, (Text, Title)):
                    text_elements.append(str(element))
                elif isinstance(element, Table):
                    # Format tables properly
                    table_text = "\n".join([" | ".join(row) for row in element.dimensions])
                    text_elements.append(table_text)
                elif isinstance(element, ListItem):
                    text_elements.append(f"• {str(element)}")
            
            return "\n".join(text_elements)
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return ""
        finally:
            os.unlink(tmp_file.name)

def extract_invoice_data(text, llm):
    """Extract invoice data with improved prompt"""
    prompt = """You are an expert invoice data extractor. Analyze the following text and extract ONLY invoice-related information.
    
    Key information to identify and extract:
    1. Invoice numbers/IDs
    2. Issue dates and due dates
    3. Company names (both vendor and client)
    4. Billing addresses
    5. Line items with:
       - Item descriptions
       - Quantities
       - Unit prices
       - Subtotals
    6. Tax amounts
    7. Total amounts
    8. Payment terms
    9. Payment instructions if present
    
    Format the output to maintain the original invoice structure.
    If you find an invoice, format it clearly with appropriate sections and spacing.
    If no invoice-like content is found, return exactly "NO_INVOICE_FOUND".
    
    Text to analyze:
    {text}
    """.format(text=text)

    try:
        response = llm.invoke(prompt).content
        return None if response.strip() == "NO_INVOICE_FOUND" else response
    except Exception as e:
        st.error(f"LLM Processing Error: {str(e)}")
        return None

def create_pdf(text):
    """Create better formatted PDF output"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up dimensions
    margin = inch
    y = letter[1] - margin  # Start from top margin
    x = margin
    line_height = 14
    page_height = letter[1]
    
    # Set font
    c.setFont("Helvetica", 10)
    
    lines = text.split('\n')
    for line in lines:
        # Check if we need a new page
        if y < margin:
            c.showPage()
            y = page_height - margin
            c.setFont("Helvetica", 10)
        
        # Handle long lines
        while len(line) > 0:
            # Calculate how much of the line will fit
            line_width = c.stringWidth(line, "Helvetica", 10)
            available_width = letter[0] - 2 * margin
            
            if line_width <= available_width:
                c.drawString(x, y, line)
                line = ""
            else:
                # Find the break point
                break_point = int(len(line) * (available_width / line_width))
                while break_point > 0 and not line[break_point].isspace():
                    break_point -= 1
                
                if break_point == 0:
                    break_point = int(available_width / (c.stringWidth('x', "Helvetica", 10)))
                
                c.drawString(x, y, line[:break_point])
                line = line[break_point:].lstrip()
                y -= line_height
                
                if y < margin:
                    c.showPage()
                    y = page_height - margin
                    c.setFont("Helvetica", 10)
        
        y -= line_height
    
    c.save()
    buffer.seek(0)
    return buffer

def main():
    st.title("📄 Enhanced Invoice Extractor")
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Please set GROQ_API_KEY environment variable")
        return
    
    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.2-1b-preview"
    )
    
    # File uploader with better instructions
    st.info("Upload one or more PDF files containing invoices. The app will extract and combine all invoice information.")
    uploaded_files = st.file_uploader(
        "Select PDF files", 
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        extracted_invoices = []
        progress = st.progress(0)
        status = st.empty()
        
        for idx, file in enumerate(uploaded_files):
            status.text(f"Processing file {idx + 1} of {len(uploaded_files)}: {file.name}")
            
            # Extract text
            text = extract_text_from_pdf(file)
            
            if text:
                # Process with LLM
                invoice_data = extract_invoice_data(text, llm)
                if invoice_data:
                    extracted_invoices.append(f"--- Invoice from {file.name} ---\n{invoice_data}")
            
            progress.progress((idx + 1) / len(uploaded_files))
        
        status.empty()
        
        if extracted_invoices:
            st.success(f"Successfully extracted {len(extracted_invoices)} invoices!")
            
            # Combine all invoices
            combined_text = "\n\n" + "="*50 + "\n\n".join(extracted_invoices)
            
            # Create PDF
            pdf_buffer = create_pdf(combined_text)
            
            col1, col2 = st.columns(2)
            
            # Download button
            with col1:
                st.download_button(
                    "📥 Download Extracted Invoices",
                    pdf_buffer,
                    f"invoices_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    "application/pdf"
                )
            
            # Show preview
            with col2:
                if st.button("👁️ View Extracted Text"):
                    st.text_area("Extracted Invoice Text", combined_text, height=400)
        else:
            st.error("No invoices could be detected in the uploaded documents. Please ensure the PDFs contain invoice data and try again.")
            st.info("Tips:\n" + 
                   "• Make sure the PDF is not password protected\n" +
                   "• Check if the PDF contains searchable text\n" +
                   "• Ensure the invoice format is standard and readable")

if __name__ == "__main__":
    main()