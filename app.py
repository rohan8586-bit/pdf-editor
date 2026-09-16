import os
import urllib.request
import fitz  # PyMuPDF
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Marathi PDF Editor", page_icon="📄", layout="centered")

FONT_PATH = "MarathiFont.ttf"

def download_marathi_font():
    """Ensure Marathi font exists locally"""
    if not os.path.exists(FONT_PATH):
        try:
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari-Regular.ttf"
            urllib.request.urlretrieve(url, FONT_PATH)
        except Exception as e:
            st.error(f"Failed to download font: {e}")

download_marathi_font()

st.title("📄 Marathi PDF Editor")
st.write("Add Marathi/English text overlays directly to your PDF documents.")

# 1. File Upload
uploaded_file = st.file_uploader("1. Choose a PDF File", type=["pdf"])

if uploaded_file:
    # Read PDF using PyMuPDF from memory bytes
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = len(doc)
    st.success(f"PDF Loaded successfully! Total Pages: {total_pages}")

    # Sidebar Controls (Mobile-friendly drawer)
    st.sidebar.header("Text & Layout Settings")
    
    font_style = st.sidebar.selectbox("Font Style", ["Regular", "Bold", "Italic"])
    font_size = st.sidebar.number_input("Font Size (pt)", min_value=5, max_value=200, value=20)
    
    # Position
    col1, col2 = st.sidebar.columns(2)
    with col1:
        x_pos = st.number_input("X Position", min_value=0, max_value=5000, value=100)
    with col2:
        y_pos = st.number_input("Y Position", min_value=0, max_value=5000, value=100)

    # Page Selection
    page_mode = st.sidebar.radio("Apply Text To:", ["Single Page", "Page Range"])
    
    if page_mode == "Single Page":
        start_page = st.sidebar.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
        end_page = start_page
    else:
        start_page = st.sidebar.number_input("Start Page", min_value=1, max_value=total_pages, value=1)
        end_page = st.sidebar.number_input("End Page", min_value=1, max_value=total_pages, value=total_pages)

    # Text Input
    text_to_add = st.text_area("2. Enter Text (Marathi / English)", placeholder="इथे मजकूर लिहा...")

    # Process & Download Button
    if st.button("3. Process PDF & Generate Download Link", type="primary"):
        if not text_to_add.strip():
            st.warning("Please enter some text first.")
        elif start_page > end_page:
            st.error("Start Page cannot be greater than End Page.")
        else:
            try:
                font_weight = "bold" if font_style == "Bold" else "normal"
                font_style_attr = "italic" if font_style == "Italic" else "normal"

                css_style = f"""
                @font-face {{
                    font-family: 'MarathiCustom';
                    src: url('{FONT_PATH}');
                }}
                * {{
                    font-family: 'MarathiCustom';
                    font-size: {font_size}pt;
                    font-weight: {font_weight};
                    font-style: {font_style_attr};
                    color: black;
                    line-height: 1.2;
                }}
                """
                
                html_content = f"<div>{text_to_add.replace('\n', '<br>')}</div>"
                archive = fitz.Archive(".")

                for page_num in range(start_page - 1, end_page):
                    page = doc[page_num]
                    rect = fitz.Rect(x_pos, y_pos, page.rect.width - 20, page.rect.height - 20)
                    page.insert_htmlbox(rect, html_content, css=css_style, archive=archive)

                # Save output to memory
                output_pdf_bytes = doc.tobytes(garbage=4, deflate=True)
                doc.close()

                # Streamlit Download Button
                st.download_button(
                    label="📥 Download Processed PDF",
                    data=output_pdf_bytes,
                    file_name="modified_output.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
