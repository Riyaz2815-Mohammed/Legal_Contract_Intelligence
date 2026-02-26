from flask import Flask, render_template, request, jsonify
import pdfplumber
import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import json

app = Flask(__name__)

# Load env from backend dir
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# AWS Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Initialize S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

UPLOAD_FOLDER = "backend/data/uploads"
TEXT_FOLDER = "extracted_texts"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TEXT_FOLDER"] = TEXT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)


def extract_text_from_file(local_path: str) -> str:
    """
    Extract plain text from a file, dispatching based on extension.
    Supports: .pdf, .docx, .txt
    """
    ext = os.path.splitext(local_path)[1].lower()
    extracted_text = ""

    if ext == ".pdf":
        with pdfplumber.open(local_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                extracted_text += f"PAGE {page_number}\n"
                extracted_text += "-" * 20 + "\n"
                extracted_text += text + "\n\n"

    elif ext == ".docx":
        from docx import Document
        doc = Document(local_path)
        # Group paragraphs – use heading breaks as "pages"
        page_number = 1
        extracted_text += f"PAGE {page_number}\n" + "-" * 20 + "\n"
        for para in doc.paragraphs:
            if para.text.strip():
                extracted_text += para.text.strip() + "\n"

    elif ext == ".txt":
        with open(local_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        extracted_text += "PAGE 1\n" + "-" * 20 + "\n" + content

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return extracted_text


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        if "pdf_file" in request.files:
            file = request.files["pdf_file"]

            if file.filename != "":
                local_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(local_path)

                try:
                    extracted_text = extract_text_from_file(local_path)
                except Exception as e:
                    message = f"Extraction error: {e}"
                    return render_template("index.html", message=message)

                # Derive txt filename based on actual extension
                base_name = os.path.splitext(file.filename)[0]
                txt_filename = base_name + ".txt"
                txt_path = os.path.join(app.config["TEXT_FOLDER"], txt_filename)

                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)

                message = f"Text extracted and saved as {txt_filename}"

    return render_template("index.html", message=message)


@app.route("/extract_s3/<path:file_key>")
def extract_s3(file_key):
    """Pull a file from S3, extract text, classify clauses, return JSON results.

    Optional query params:
        document_type  — e.g. NDA, MSA, SOW  (default: "Unknown")
        source         — "client" or "legal"  (default: "unknown")
    """
    local_path = os.path.join(app.config["UPLOAD_FOLDER"], file_key)

    # Read optional metadata from query string
    document_type = request.args.get("document_type", "Unknown")
    source        = request.args.get("source", "unknown")

    try:
        print(f"☁️ Downloading {file_key} from S3...")
        s3_client.download_file(BUCKET_NAME, file_key, local_path)
        print(f"✅ Downloaded to {local_path}")

        # Extract text (handles PDF, DOCX, TXT)
        extracted_text = extract_text_from_file(local_path)

        # Derive filenames from actual extension
        base_name = os.path.splitext(file_key)[0]
        txt_filename = base_name + ".txt"
        json_filename = base_name + ".json"
        txt_path = os.path.join(app.config["TEXT_FOLDER"], txt_filename)
        json_path = os.path.join(app.config["TEXT_FOLDER"], json_filename)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        print(f"📝 Saved extracted text to {txt_path}")

        # Parse and classify — pass document type and source
        from clause_engine import parse_text_file, process_document
        raw_blocks = parse_text_file(txt_path)
        classification_results = process_document(
            raw_blocks,
            document=document_type,
            source=source
        )

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(classification_results, f, indent=2, ensure_ascii=False)

        print(f"✅ Classification complete: {len(classification_results)} clauses → {json_path}")

        return jsonify({
            "status": "success",
            "message": f"Extracted and classified. {len(classification_results)} clauses saved as {json_filename}",
            "txt_path": txt_path,
            "json_path": json_path,
            "clauses_found": len(classification_results)
        })
    except Exception as e:
        import traceback
        print(f"❌ extract_s3 error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
