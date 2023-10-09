import io
import PyPDF2


def read_pdf_object(pdf):
    # If the input is bytes, convert it to a file-like object
    if isinstance(pdf, bytes):
        pdf = io.BytesIO(pdf)
    reader = PyPDF2.PdfReader(pdf)
    content = ""
    for page in range(len(reader.pages)):
        content += reader.pages[page].extract_text()
    return content


def read_pdf_file(path):
    with open(path, "rb") as pdf_file:
        print("Found PDF")
        reader = PyPDF2.PdfReader(pdf_file)
        content = ""
        for page in range(len(reader.pages)):
            content += reader.pages[page].extract_text()
        return content
