from flask import Flask, render_template, request
import pdfplumber
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "extracted_texts"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TEXT_FOLDER"] = TEXT_FOLDER

# Create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        if "pdf_file" in request.files:
            file = request.files["pdf_file"]

            if file.filename != "":
                pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(pdf_path)

                extracted_text = ""

                # Extract text using pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page_number, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text()

                        # Add page number at top left
                        extracted_text += f"PAGE {page_number}\n"
                        extracted_text += "-" * 20 + "\n"

                        if text:
                            extracted_text += text + "\n\n"

                # Create txt file name
                txt_filename = file.filename.replace(".pdf", ".txt")
                txt_path = os.path.join(app.config["TEXT_FOLDER"], txt_filename)

                # Save extracted text into .txt file
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(extracted_text)

                message = f"Text extracted and saved as {txt_filename}"

    return render_template("index.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
