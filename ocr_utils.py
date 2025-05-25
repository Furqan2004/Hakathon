import os
import tempfile
import fitz  # PyMuPDF
import cv2
import requests
import pytesseract

def save_pdf_pages(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    img_paths = []
    temp_dir = tempfile.mkdtemp()
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(temp_dir, f"page_{i}.png")
        pix.save(img_path)
        img_paths.append(img_path)
    return img_paths, temp_dir

def save_image_file(file):
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, file.filename)
    file.save(path)
    return [path], temp_dir

def handle_file(file):
    if file.filename.lower().endswith(".pdf"):
        return save_pdf_pages(file)
    return save_image_file(file)

def run_ocr(image_paths):
    all_text = []
    for path in image_paths:
        image = cv2.imread(path)
        if image is None:
            all_text.append(f"Error loading image: {path}")
            continue

        # Convert image to RGB (pytesseract expects RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # OCR
        text = pytesseract.image_to_string(rgb_image)

        all_text.append(text.strip())
    return "\n".join(all_text)

