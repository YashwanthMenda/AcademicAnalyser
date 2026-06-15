"""
Simple PDF Text Extractor
Extracts only selectable text, ignores all images
"""

import pdfplumber
import PyPDF2
import io
import streamlit as st
from docx import Document


def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded file
    Supports: PDF, TXT, DOCX
    Ignores: Images, scanned content
    
    Args:
        uploaded_file: Uploaded file object from Streamlit
        
    Returns:
        str: Extracted text (text only, no images)
    """
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    
    if file_extension == 'txt':
        return extract_from_txt(uploaded_file)
    
    elif file_extension == 'docx':
        return extract_from_docx(uploaded_file)
    
    elif file_extension == 'pdf':
        return extract_from_pdf(uploaded_file)
    
    else:
        st.error(f"❌ Unsupported file type: {file_extension}")
        st.info("✅ Supported: PDF, TXT, DOCX (text-based files only)")
        return None


def extract_from_txt(txt_file):
    """Extract text from TXT file"""
    
    try:
        text = txt_file.read().decode('utf-8')
        
        if text and text.strip():
            word_count = len(text.split())
            st.success(f"✅ Extracted {word_count:,} words from TXT file")
            return text
        
        st.warning("⚠️ TXT file appears to be empty")
        return None
        
    except Exception as e:
        st.error(f"❌ Error reading TXT file: {str(e)}")
        return None


def extract_from_docx(docx_file):
    """Extract text from DOCX file (ignores images)"""
    
    try:
        doc = Document(docx_file)
        
        # Extract only paragraph text (ignores images, tables, etc.)
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        
        full_text = '\n\n'.join(paragraphs)
        
        if full_text and full_text.strip():
            word_count = len(full_text.split())
            st.success(f"✅ Extracted {word_count:,} words from DOCX")
            return full_text
        
        st.warning("⚠️ No text found in DOCX file")
        return None
        
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {str(e)}")
        return None


def extract_from_pdf(pdf_file):
    """
    Extract ONLY TEXT from PDF
    Completely ignores images, scanned content, and graphics
    """
    
    st.info("📄 Extracting text from PDF (images will be ignored)...")
    
    # Validate PDF first
    if not validate_pdf_structure(pdf_file):
        return None
    
    # Try extraction methods in order of reliability
    methods = [
        ("pdfplumber", extract_with_pdfplumber),
        ("PyPDF2", extract_with_pypdf2)
    ]
    
    for method_name, method_func in methods:
        try:
            pdf_file.seek(0)
            st.info(f"🔍 Trying {method_name}...")
            
            text = method_func(pdf_file)
            
            if text and len(text.strip()) > 100:
                return text
            
        except Exception as e:
            st.warning(f"⚠️ {method_name} failed: {str(e)}")
            continue
    
    # All methods failed
    st.error("❌ Could not extract text from PDF")
    st.error("**Possible reasons:**")
    st.error("• PDF contains only scanned images (no selectable text)")
    st.error("• PDF is password protected")
    st.error("• PDF is corrupted")
    
    show_quick_solutions()
    return None


def validate_pdf_structure(pdf_file):
    """Check if PDF is valid and readable"""
    
    try:
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        # Check minimum size
        if len(pdf_bytes) < 100:
            st.error("❌ File is too small to be a valid PDF")
            return False
        
        # Check PDF header
        if not pdf_bytes.startswith(b'%PDF'):
            st.error("❌ File is not a valid PDF")
            return False
        
        # Try to open
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)
            
            if page_count == 0:
                st.error("❌ PDF has 0 pages")
                return False
            
            st.success(f"✅ Valid PDF with {page_count} pages")
            return True
            
        except Exception as e:
            st.error(f"❌ Cannot open PDF: {str(e)}")
            return False
            
    except Exception as e:
        st.error(f"❌ Cannot read file: {str(e)}")
        return False


# PyMuPDF extraction removed to avoid C dependencies


def extract_with_pdfplumber(pdf_file):
    """
    Extract text using pdfplumber
    Only extracts text, ignores images
    """
    
    try:
        full_text = []
        
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for page_num, page in enumerate(pdf.pages):
                status_text.text(f"📖 Reading page {page_num + 1}/{total_pages}")
                
                # Extract only text (not images or tables)
                text = page.extract_text()
                
                if text and text.strip():
                    full_text.append(text.strip())
                
                progress_bar.progress((page_num + 1) / total_pages)
            
            progress_bar.empty()
            status_text.empty()
        
        # Combine all text
        result = '\n\n'.join(full_text)
        
        if result and result.strip():
            word_count = len(result.split())
            st.success(f"✅ pdfplumber: Extracted {word_count:,} words from {total_pages} pages")
            return result
        
        return None
        
    except Exception as e:
        raise e


def extract_with_pypdf2(pdf_file):
    """
    Extract text using PyPDF2
    Only extracts text, ignores images
    """
    
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        
        full_text = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for page_num in range(total_pages):
            status_text.text(f"📖 Reading page {page_num + 1}/{total_pages}")
            
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            if text and text.strip():
                full_text.append(text.strip())
            
            progress_bar.progress((page_num + 1) / total_pages)
        
        progress_bar.empty()
        status_text.empty()
        
        # Combine all text
        result = '\n\n'.join(full_text)
        
        if result and result.strip():
            word_count = len(result.split())
            st.success(f"✅ PyPDF2: Extracted {word_count:,} words from {total_pages} pages")
            return result
        
        return None
        
    except Exception as e:
        raise e


def validate_pdf(pdf_file):
    """Validate uploaded file"""
    
    if pdf_file is None:
        return False
    
    # Check file extension
    allowed_extensions = ['pdf', 'txt', 'docx']
    file_ext = pdf_file.name.lower().split('.')[-1]
    
    if file_ext not in allowed_extensions:
        st.error(f"❌ Unsupported file type: {file_ext}")
        st.info("✅ Supported: PDF, TXT, DOCX")
        return False
    
    # Check file size (max 200MB)
    file_size_mb = pdf_file.size / (1024 * 1024)
    if file_size_mb > 200:
        st.error(f"❌ File too large ({file_size_mb:.1f}MB). Maximum 200MB")
        return False
    
    return True


def get_pdf_info(pdf_file):
    """Get basic file information"""
    
    try:
        file_ext = pdf_file.name.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            page_count = len(reader.pages)
            
            return {
                'pages': page_count,
                'size_mb': len(pdf_bytes) / (1024 * 1024)
            }
        else:
            return {
                'pages': 1,
                'size_mb': pdf_file.size / (1024 * 1024)
            }
            
    except Exception as e:
        return {
            'pages': 0,
            'size_mb': pdf_file.size / (1024 * 1024)
        }


def show_quick_solutions():
    """Show solutions for extraction failures"""
    
    with st.expander("💡 Quick Solutions", expanded=True):
        st.markdown("""
        ### ✅ Your PDF has no selectable text. Here's what to do:
        
        #### Option 1: Convert PDF to Text (Recommended)
        
        **Method A - Google Drive (Free, Easy):**
        ```
        1. Go to drive.google.com
        2. Upload your PDF
        3. Right-click → Open with → Google Docs
        4. Google will convert it to text
        5. File → Download → PDF Document
        6. Upload the new PDF here
        ```
        
        **Method B - Adobe Online (Free):**
        ```
        1. Visit: adobe.com/acrobat/online/pdf-to-word
        2. Upload and convert
        3. Download Word file
        4. Save as PDF from Word
        5. Upload here
        ```
        
        ---
        
        #### Option 2: Use Different Format
        
        **Save as Text:**
        - If you can open the PDF, copy all text (Ctrl+A, Ctrl+C)
        - Save as .TXT file
        - Upload TXT instead
        
        **Save as DOCX:**
        - Open PDF in Word
        - File → Save As → Word Document (.docx)
        - Upload DOCX here
        
        ---
        
        #### Option 3: Manual Input
        
        Switch to the **"Paste Text"** tab and:
        1. Open your PDF
        2. Select all text (Ctrl+A)
        3. Copy (Ctrl+C)
        4. Paste in the text box
        5. Click "Process Text"
        
        ---
        
        ### How to Check if PDF has Text:
        
        ✅ **Has Text** (Will work):
        - You can select/highlight text with mouse
        - You can copy-paste text
        - Created from Word/Google Docs
        
        ❌ **No Text** (Won't work):
        - Cannot select text
        - Just images/scans
        - Scanned from books
        - Screenshots saved as PDF
        """)

# Compatibility alias
extract_text_from_pdf = extract_text_from_file

