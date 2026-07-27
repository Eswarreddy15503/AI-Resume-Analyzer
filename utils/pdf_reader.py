import io
import PyPDF2
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file stream or file path.
    
    Args:
        pdf_file: A file-like object (e.g., BytesIO from Streamlit) or a file path.
        
    Returns:
        str: Extracted text from the PDF.
    """
    text = ""
    try:
        # If pdf_file is bytes, wrap it in BytesIO
        if isinstance(pdf_file, bytes):
            pdf_file = io.BytesIO(pdf_file)
            
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Iterate through pages and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise RuntimeError(f"Could not parse PDF file: {str(e)}")
        
    return text.strip()
