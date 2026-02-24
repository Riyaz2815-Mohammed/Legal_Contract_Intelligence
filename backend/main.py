from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import secrets
import uuid
import requests
from datetime import datetime, timedelta
import jwt
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import requests
from embeddings.sbert_model import load_model

app = FastAPI(title="LACCIS API", description="Legal Clause Classification Intelligence System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Data storage (use database in production)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
CLIENTS_FILE = DATA_DIR / "clients.json"
LEGAL_TEAM_FILE = DATA_DIR / "legal_team.json"
DOCUMENTS_FILE = DATA_DIR / "documents.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Load environment variables                
load_dotenv()
EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY")

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

# Debug: Print if credentials are loaded
print(f"✓ EMAILJS_SERVICE_ID loaded: {bool(EMAILJS_SERVICE_ID)}")
print(f"✓ EMAILJS_TEMPLATE_ID loaded: {bool(EMAILJS_TEMPLATE_ID)}")
print(f"✓ EMAILJS_PUBLIC_KEY loaded: {bool(EMAILJS_PUBLIC_KEY)}")

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ClientCreate(BaseModel):
    name: str
    email: EmailStr

class LegalTeamMemberCreate(BaseModel):
    name: str
    email: EmailStr

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str  # 'admin' or 'client'

class DocumentUpload(BaseModel):
    document_type: str  # 'NDA', 'MSA', 'SOW', 'Redlined', 'Others'
    shared_with: Optional[str] = None  # client_id or 'admin'
    
class DocumentShare(BaseModel):
    document_id: str
    share_with: str  # client_id or 'admin'

class MessageSend(BaseModel):
    recipient_id: str  # client_id or 'admin'
    content: str

class Message(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    content: str
    timestamp: str

# Helper functions
def load_json(file_path):
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
        except Exception as e:
            print(f"ERROR loading {file_path}: {e}")
            return []
    return []

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def create_token(user_id: str, email: str, role: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def send_email(to_email: str, subject: str, body: str):
    """
    Send email via EmailJS REST API
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML format)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Check if EmailJS credentials are configured
        if not all([EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY]):
            error_msg = f"EmailJS credentials not configured. SERVICE_ID: {bool(EMAILJS_SERVICE_ID)}, TEMPLATE_ID: {bool(EMAILJS_TEMPLATE_ID)}, PUBLIC_KEY: {bool(EMAILJS_PUBLIC_KEY)}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        
        # EmailJS API endpoint
        url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # Prepare email data
        email_data = {
            "service_id": EMAILJS_SERVICE_ID,
            "template_id": EMAILJS_TEMPLATE_ID,
            "user_id": EMAILJS_PUBLIC_KEY,
            "accessToken": EMAILJS_PRIVATE_KEY,  # Required for Strict Mode
            "template_params": {
                "to_email": to_email,
                "subject": subject,
                "html_content": body
            }
        }
        
        print(f"📤 Sending email to {to_email} via EmailJS...")
        print(f"   Service: {EMAILJS_SERVICE_ID}")
        print(f"   Template: {EMAILJS_TEMPLATE_ID}")
        
        # Send via EmailJS
        response = requests.post(url, json=email_data, timeout=10)
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Body: {response.text}")
        
        if response.status_code == 200:
            print(f"✓ Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': f'Email sent successfully to {to_email}'
            }
        else:
            error_msg = f"EmailJS error: {response.status_code} - {response.text}"
            print(f"✗ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
    
    except requests.exceptions.Timeout:
        error_msg = "EmailJS request timeout - check your internet connection"
        print(f"✗ {error_msg}")
        return {'success': False, 'message': error_msg}
    
    except requests.exceptions.RequestException as e:
        error_msg = f"EmailJS request error: {str(e)}"
        print(f"✗ {error_msg}")
        return {'success': False, 'message': error_msg}
    
    except Exception as e:
        error_msg = f"Email error: {str(e)}"
        print(f"✗ {error_msg}")
        return {'success': False, 'message': error_msg}

# Initialize default admin user
def init_default_users():
    users = load_json(USERS_FILE)
    if not users:
        admin = {
            "id": "admin-1",
            "name": "Legal Team Admin",
            "email": "admin@laccis.com",
            "password": "admin123",  # Change in production!
            "role": "admin",
            "created_at": datetime.now().isoformat()
        }
        save_json(USERS_FILE, [admin])

init_default_users()

# Routes
@app.get("/")
def root():
    return {"message": "LACCIS API is running", "version": "1.0.0"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    users = load_json(USERS_FILE)
    
    user = next((u for u in users if u["email"] == request.email), None)
    
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["email"], user["role"])
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.post("/api/clients/create")
def create_client(client: ClientCreate, current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create clients")
    
    # Generate unique ID and random password
    client_id = f"client-{uuid.uuid4().hex[:8]}"
    random_suffix = secrets.token_hex(3).upper()
    password = f"LACCIS-{random_suffix}"
    
    # Create client user
    users = load_json(USERS_FILE)
    clients = load_json(CLIENTS_FILE)
    
    # Check if email already exists
    if any(u["email"] == client.email for u in users):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "id": client_id,
        "name": client.name,
        "email": client.email,
        "password": password,
        "role": "client",
        "created_at": datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_json(USERS_FILE, users)
    
    # Save client info
    new_client = {
        "id": client_id,
        "name": client.name,
        "email": client.email,
        "created_at": datetime.now().isoformat()
    }
    
    clients.append(new_client)
    save_json(CLIENTS_FILE, clients)
    
    # Load and customize email template
    try:
        template_path = Path("email_template.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            email_body = f.read()
        
        # Replace placeholders
        email_body = email_body.replace('{CLIENT_NAME}', client.name)
        email_body = email_body.replace('{CLIENT_EMAIL}', client.email)
        email_body = email_body.replace('{CLIENT_PASSWORD}', password)
    except Exception as e:
        print(f"Error loading template: {e}")
        # Fallback to basic email
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #6366f1;">Welcome to LACCIS</h2>
                <p>Hello {client.name},</p>
                <p>Your account has been created for the Legal Clause Classification Intelligence System.</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Your Login Credentials:</h3>
                    <p><strong>Email:</strong> {client.email}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>
                
                <p>You can now log in and upload your contract documents for analysis.</p>
                <p><a href="http://localhost:5173" style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;">Login to LACCIS</a></p>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">Please keep your credentials secure and do not share them with anyone.</p>
            </div>
        </body>
        </html>
        """
    
    email_sent = send_email(client.email, "Your LACCIS Login Credentials", email_body)
    
    return {
        "message": "Client created successfully",
        "client": new_client,
        "email_sent": email_sent['success'],
        "email_message": email_sent['message'],
        "credentials": {
            "email": client.email,
            "password": password
        }
    }


@app.post("/api/legal/create")
def create_legal_team_member(member: LegalTeamMemberCreate, current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create legal team members")
    
    # Generate unique ID and random password
    member_id = f"legal-{uuid.uuid4().hex[:8]}"
    password = secrets.token_urlsafe(12)
    
    # Create legal team user
    users = load_json(USERS_FILE)
    legal_team = load_json(LEGAL_TEAM_FILE)
    
    # Check if email already exists
    if any(u["email"] == member.email for u in users):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "id": member_id,
        "name": member.name,
        "email": member.email,
        "password": password,
        "role": "legal_team",
        "created_at": datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_json(USERS_FILE, users)
    
    # Save legal team info
    new_member = {
        "id": member_id,
        "name": member.name,
        "email": member.email,
        "created_at": datetime.now().isoformat()
    }
    
    legal_team.append(new_member)
    save_json(LEGAL_TEAM_FILE, legal_team)
    
    # Send email with credentials
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #6366f1;">Welcome to LACCIS Legal Team</h2>
            <p>Hello {member.name},</p>
            <p>Your account has been created for the Legal Clause Classification Intelligence System.</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Your Login Credentials:</h3>
                <p><strong>Email:</strong> {member.email}</p>
                <p><strong>Password:</strong> {password}</p>
            </div>
            
            <p>You can now log in to review contracts.</p>
            <p><a href="http://localhost:5173" style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;">Login to LACCIS</a></p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">Please keep your credentials secure and do not share them with anyone.</p>
        </div>
    </body>
    </html>
    """
    
    email_sent = send_email(member.email, "LACCIS Legal Team Account", email_body)
    
    return {
        "message": "Legal team member created successfully",
        "member": new_member,
        "email_sent": email_sent,
        "credentials": {
            "email": member.email,
            "password": password
        }
    }

@app.get("/api/legal/list")
def list_legal_team(current_user: dict = Depends(verify_token)):
    # Allowed for both admin and client roles to facilitate chat
    legal_team = load_json(LEGAL_TEAM_FILE)
    return {"members": legal_team}

@app.delete("/api/legal/delete/{member_id}")
def delete_legal_team_member(member_id: str, current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete legal team members")
    
    # Load data
    legal_team = load_json(LEGAL_TEAM_FILE)
    users = load_json(USERS_FILE)
    
    # Find member
    member = next((m for m in legal_team if m["id"] == member_id), None)
    if not member:
        raise HTTPException(status_code=404, detail="Legal team member not found")
    
    # Remove from legal team list
    legal_team = [m for m in legal_team if m["id"] != member_id]
    save_json(LEGAL_TEAM_FILE, legal_team)
    
    # Remove user account
    users = [u for u in users if u["id"] != member_id]
    save_json(USERS_FILE, users)
    
    return {
        "message": "Legal team member deleted successfully",
        "member": member
    }

@app.get("/api/clients/list")
def list_clients(current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view clients")
    
    clients = load_json(CLIENTS_FILE)
    return {"clients": clients}

@app.delete("/api/clients/delete/{client_id}")
def delete_client(client_id: str, current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete clients")
    
    # Load data
    clients = load_json(CLIENTS_FILE)
    users = load_json(USERS_FILE)
    documents = load_json(DOCUMENTS_FILE)
    
    # Find client
    client = next((c for c in clients if c["id"] == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Remove client from clients list
    clients = [c for c in clients if c["id"] != client_id]
    save_json(CLIENTS_FILE, clients)
    
    # Remove user account
    users = [u for u in users if u["id"] != client_id]
    save_json(USERS_FILE, users)
    
    # Remove client's documents
    client_docs = [d for d in documents if d["user_id"] == client_id]
    for doc in client_docs:
        # Delete physical file
        try:
            file_path = Path(doc["file_path"])
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Error deleting file: {e}")
            
        # Delete from S3
        try:
            s3_key = doc.get("s3_key")
            if s3_key:
                print(f"☁️ Deleting {s3_key} from S3...")
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
                print(f"✅ Successfully deleted from S3")
        except ClientError as e:
            print(f"❌ S3 Delete Error: {e}")
    
    # Remove documents from list
    documents = [d for d in documents if d["user_id"] != client_id]
    save_json(DOCUMENTS_FILE, documents)
    
    return {
        "message": "Client deleted successfully",
        "client": client,
        "documents_deleted": len(client_docs)
    }


def trigger_extraction(file_name: str):
    """Background task: call extraction service with adequate timeout."""
    try:
        extract_url = f"http://localhost:5000/extract_s3/{file_name}"
        print(f"⚡ [Background] Triggering extraction for {file_name}...")
        response = requests.get(extract_url, timeout=120)  # 2-min timeout
        result = response.json()
        if result.get("status") == "success":
            print(f"✅ [Background] Extraction complete: {result.get('clauses_found', 0)} clauses found")
        else:
            print(f"⚠️ [Background] Extraction returned: {result.get('message', 'unknown error')}")
    except Exception as e:
        print(f"❌ [Background] Extraction failed for {file_name}: {e}")


@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = "Others",
    shared_with: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    # All document types are allowed without restriction
    print(f"📄 User {current_user['user_id']} uploading {document_type}")
    
    # Save file
    file_name = f"{current_user['user_id']}_{file.filename}"
    file_path = UPLOADS_DIR / file_name
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Upload to S3
    try:
        print(f"☁️ Uploading {file_name} to S3 bucket: {BUCKET_NAME}...")
        s3_client.upload_file(str(file_path), BUCKET_NAME, file_name)
        print(f"✅ Successfully uploaded to S3")
        s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
    except ClientError as e:
        print(f"❌ S3 Upload Error: {e}")
        s3_url = None
    
    # Save document metadata
    documents = load_json(DOCUMENTS_FILE)
    
    # Determine status based on document type
    status = "pending" if document_type == "NDA" else "uploaded"
    
    new_doc = {
        "id": f"doc-{len(documents) + 1}",
        "filename": file.filename,
        "document_type": document_type,
        "user_id": current_user["user_id"],
        "user_email": current_user["email"],
        "user_role": current_user["role"],
        "size": len(content),
        "status": status,  # pending, approved, rejected, uploaded
        "shared_with": shared_with if shared_with else [],
        "uploaded_at": datetime.now().isoformat(),
        "file_path": str(file_path),
        "s3_url": s3_url,
        "s3_key": file_name
    }
    
    documents.append(new_doc)
    save_json(DOCUMENTS_FILE, documents)
    
    # Trigger automated extraction in background only for NDAs
    if s3_url and document_type == "NDA":
        background_tasks.add_task(trigger_extraction, file_name)
        print(f"⚡ Queued background extraction for {file_name}")

    # Notify admin if client uploaded NDA
    if document_type == "NDA" and current_user["role"] == "client":
        # In production, send email notification to admin
        pass
    
    return {
        "message": "Document uploaded successfully and queued for extraction",
        "document": new_doc
    }

@app.get("/api/documents/analysis/{document_id}")
def get_document_analysis(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    documents = load_json(DOCUMENTS_FILE)
    doc = next((d for d in documents if d["id"] == document_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    s3_key = doc.get("s3_key")
    if not s3_key:
        raise HTTPException(status_code=400, detail="Document analysis not available")
        
    # The extraction results are saved as .json in extracter/extracted_texts/
    # From backend/main.py, the path is ../extracter/extracted_texts/
    json_filename = str(Path(s3_key).with_suffix('.json'))
    analysis_path = Path(__file__).parent.parent / "extracter" / "extracted_texts" / json_filename
    
    if not analysis_path.exists():
        # Maybe it's still being processed or failed
        print(f"⚠️ Analysis file not found at: {analysis_path}")
        return {"document": doc, "clauses": [], "status": "processing"}
        
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            clauses = json.load(f)
        return {"document": doc, "clauses": clauses, "status": "complete"}
    except Exception as e:
        print(f"❌ Error reading analysis file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading analysis: {str(e)}")

@app.get("/api/documents/download/{document_id}")
def download_document(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    documents = load_json(DOCUMENTS_FILE)
    doc = next((d for d in documents if d["id"] == document_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    s3_key = doc.get("s3_key")
    if not s3_key:
        raise HTTPException(status_code=400, detail="Document not available on S3")
        
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        return {"download_url": url}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 Error: {str(e)}")

@app.post("/api/documents/share")
def share_document(
    share_request: DocumentShare,
    current_user: dict = Depends(verify_token)
):
    documents = load_json(DOCUMENTS_FILE)
    
    # Find document
    doc = next((d for d in documents if d["id"] == share_request.document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permission
    if current_user["role"] != "admin" and doc["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to share this document")
    
    # Update shared_with
    if isinstance(doc["shared_with"], list):
        if share_request.share_with not in doc["shared_with"]:
            doc["shared_with"].append(share_request.share_with)
    else:
        doc["shared_with"] = [share_request.share_with]
    
    # Update document in list
    for i, d in enumerate(documents):
        if d["id"] == share_request.document_id:
            documents[i] = doc
            break
    
    save_json(DOCUMENTS_FILE, documents)
    
    # Send notification email
    users = load_json(USERS_FILE)
    recipient = next((u for u in users if u["id"] == share_request.share_with or u["role"] == share_request.share_with), None)
    
    if recipient:
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Document Shared with You</h2>
            <p>A document has been shared with you on LACCIS.</p>
            <p><strong>Document:</strong> {doc['filename']}</p>
            <p><strong>Type:</strong> {doc['document_type']}</p>
            <p><strong>Shared by:</strong> {current_user['email']}</p>
            <p><a href="http://localhost:5173" style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;">View Document</a></p>
        </body>
        </html>
        """
        send_email(recipient["email"], "Document Shared - LACCIS", email_body)
    
    return {
        "message": "Document shared successfully",
        "document": doc
    }

@app.post("/api/documents/approve/{document_id}")
def approve_document(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve documents")
    
    documents = load_json(DOCUMENTS_FILE)
    
    # Find and update document
    for i, doc in enumerate(documents):
        if doc["id"] == document_id:
            documents[i]["status"] = "approved"
            documents[i]["approved_at"] = datetime.now().isoformat()
            documents[i]["approved_by"] = current_user["user_id"]
            
            save_json(DOCUMENTS_FILE, documents)
            
            # Notify client
            users = load_json(USERS_FILE)
            client = next((u for u in users if u["id"] == doc["user_id"]), None)
            
            if client:
                email_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #10b981;">Document Approved</h2>
                    <p>Your {doc['document_type']} has been approved!</p>
                    <p><strong>Document:</strong> {doc['filename']}</p>
                    <p>You can now upload other documents.</p>
                    <p><a href="http://localhost:5173" style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 10px;">Go to LACCIS</a></p>
                </body>
                </html>
                """
                result = send_email(client["email"], f"{doc['document_type']} Approved - LACCIS", email_body)
                print(f"Approval email result: {result}")
            
            return {
                "message": "Document approved successfully",
                "document": documents[i]
            }
    
    raise HTTPException(status_code=404, detail="Document not found")

@app.post("/api/documents/reject/{document_id}")
def reject_document(
    document_id: str,
    current_user: dict = Depends(verify_token)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reject documents")
    
    documents = load_json(DOCUMENTS_FILE)
    
    for i, doc in enumerate(documents):
        if doc["id"] == document_id:
            documents[i]["status"] = "rejected"
            documents[i]["rejected_at"] = datetime.now().isoformat()
            documents[i]["rejected_by"] = current_user["user_id"]
            
            save_json(DOCUMENTS_FILE, documents)
            
            # Notify client
            users = load_json(USERS_FILE)
            client = next((u for u in users if u["id"] == doc["user_id"]), None)
            
            if client:
                email_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #ef4444;">Document Rejected</h2>
                    <p>Your {doc['document_type']} was not approved.</p>
                    <p><strong>Document:</strong> {doc['filename']}</p>
                    <p>Please check the requirements and upload again if necessary.</p>
                </body>
                </html>
                """
                send_email(client["email"], f"{doc['document_type']} Update - LACCIS", email_body)
            
            return {
                "message": "Document rejected successfully",
                "document": documents[i]
            }
    
    raise HTTPException(status_code=404, detail="Document not found")

@app.get("/api/documents/list")
def list_documents(current_user: dict = Depends(verify_token)):
    documents = load_json(DOCUMENTS_FILE)
    
    # Filter documents based on role
    if current_user["role"] == "client":
        # Show own documents and documents shared with this client
        documents = [
            d for d in documents 
            if d["user_id"] == current_user["user_id"] 
            or current_user["user_id"] in d.get("shared_with", [])
            or "admin" in d.get("shared_with", [])
        ]
    else:
        # Admin sees all documents or documents shared with admin
        pass
    
    return {"documents": documents}

@app.get("/api/documents/stats")
def document_stats(current_user: dict = Depends(verify_token)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view stats")
    
    documents = load_json(DOCUMENTS_FILE)
    
    return {
        "total_documents": len(documents),
        "total_size": sum(d["size"] for d in documents)
    }

@app.post("/api/messages/send")
def send_message(msg: MessageSend, current_user: dict = Depends(verify_token)):
    try:
        messages = load_json(MESSAGES_FILE)
        
        # Log IDs for debugging
        print(f"📩 Sending message: from {current_user['user_id']} to {msg.recipient_id}")
        
        new_message = {
            "id": f"msg-{len(messages) + 1}-{secrets.token_hex(4)}",
            "sender_id": current_user["user_id"],
            "recipient_id": msg.recipient_id,
            "content": msg.content,
            "timestamp": datetime.now().isoformat()
        }
        
        messages.append(new_message)
        save_json(MESSAGES_FILE, messages)
        print(f"✅ Message saved to {MESSAGES_FILE}")
        
        return {"message": "Message sent", "data": new_message}
    except Exception as e:
        print(f"❌ Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/list/{other_user_id}")
def list_messages(other_user_id: str, current_user: dict = Depends(verify_token)):
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")

        print(f"🔍 Chat Request: {user_id} <-> {other_user_id}")
        messages = load_json(MESSAGES_FILE)
        
        # Strictly 1-on-1 private filtering
        filtered = [
            m for m in messages
            if (m.get("sender_id") == user_id and m.get("recipient_id") == other_user_id)
            or (m.get("sender_id") == other_user_id and m.get("recipient_id") == user_id)
        ]
        
        return {"messages": filtered}
    except Exception as e:
        print(f"❌ Chat List Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
def startup_event():
    load_model()
    print("✅ SBERT model loaded successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
