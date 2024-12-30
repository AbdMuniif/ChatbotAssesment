
FROM python:3.9-slim


RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    pip install pytesseract pdfplumber pymupdf
    RUN pip install mysql-connector-python

WORKDIR /app


COPY . /app


CMD ["python", "ocr_script.py"]
