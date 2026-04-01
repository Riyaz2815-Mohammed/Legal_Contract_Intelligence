# LACCIS - Legal Clause Classification Intelligence System

## Project Description
LACCIS is a modern, responsive web application designed for legal document management with intelligent clause classification. It allows legal teams to seamlessly manage clients, who can upload and evaluate their contracts against standard templates. The system leverages AI tools to extract text, classify clauses, assess risk, and perform semantic similarity checks against standard baseline documents.

## How to Run the Project (Installation & Setup)

### Prerequisites
- Node.js v18+ 
- Python 3.8+
- Neon DB (PostgreSQL database with `pgvector` extension)

### Backend Setup
1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Configuration:**
   Create a `.env` file in the `backend` directory (refer to the Environment Variables section below).
5. **Start the FastAPI server:**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup
1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## Technology Stack

**Frontend:**
- React 19 (Hooks, React-DOM, React Router DOM, React Markdown)
- Vite 7
- Modern CSS (Glassmorphism design layout)

**Backend:**
- FastAPI (Python web framework)
- Neon DB (Serverless Postgres with pgvector for Relational & Vector storage)
- AWS S3 (Document object storage)
- PyJWT (Authentication)
- Sentence-Transformers & LangChain (Supports OpenAI, Mistral, Anthropic, Google, Groq for AI Chat, Risk Analysis, and Summarization)

## Environment Variables (`.env`)
Create a `.env` file in the `backend` directory strictly with these variable names:
```ini
# Database
DATABASE_URL= # Neon DB connection string

# EmailJS Configuration
EMAILJS_SERVICE_ID=
EMAILJS_TEMPLATE_ID=
EMAILJS_PUBLIC_KEY=
EMAILJS_PRIVATE_KEY=

# Authentication
JWT_SECRET=
ADMIN_PASSWORD=

# SSO Configuration (Central Identity Integration)
SSO_ENDPOINT=
SSO_COOKIE_NAME=
CENTRAL_LOGOUT_URL=

# AWS S3 Storage
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
REGION=
BUCKET_NAME=

# AI Settings (LangChain & Embeddings)
MODEL_NAME=
LLM_PROVIDER= # e.g., openai, mistral, anthropic, google_genai, groq
LLM_MODEL=
LLM_API_KEY=
LLM_TEMPERATURE=

# Google Drive Integration
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_CLIENT_SECRET_JSON=
GOOGLE_OAUTH_TOKEN_JSON=
```

## API Endpoints

### Authentication & Users
- `POST /api/auth/login` - User authentication (Admin and Clients)
- `POST /api/clients/create` - Create new client and auto-email credentials
- `GET /api/clients/list` - List all configured clients
- `DELETE /api/clients/delete/{client_id}` - Delete a specific client
- `POST /api/legal/create` - Create a new legal team member
- `GET /api/legal/list` - List all legal team members
- `DELETE /api/legal/delete/{member_id}` - Delete a legal team member

### Documents & Files
- `POST /api/documents/upload` - Upload document to S3 and trigger NLP text extraction
- `GET /api/documents/list` - List documents assigned to the requesting user
- `GET /api/documents/stats` - Overall document statistics
- `GET /api/documents/download/{document_id}` - Download original document
- `GET /api/documents/download-redline/{document_id}` - Download redlined document locally
- `POST /api/documents/download-redline-docs/{document_id}` - Export redlined document features to docs
- `POST /api/documents/google-doc/{document_id}` - Integrate with Google Docs
- `POST /api/documents/send-redline/{document_id}` - Send redline version to client
- `POST /api/documents/approve/{document_id}` - Approve complete document
- `POST /api/documents/reject/{document_id}` - Reject complete document
- `POST /api/documents/finalize/{document_id}` - Finalize document version
- `POST /api/documents/reprocess/{document_id}` - Reprocess document text extraction and classification

### Document Review & Core Operations
- `GET /api/documents/analysis/{document_id}` - Read overall document extraction data
- `GET /api/documents/review/{document_id}` - Fetch AI clause-by-clause review
- `POST /api/documents/review/{document_id}/edit` - Edit a specific clause content
- `POST /api/documents/review/{document_id}/comment` - Leave manual comments on clauses
- `POST /api/documents/review/{document_id}/action` - Trigger review actions on clauses

### AI & LLM Specific Endpoints
- `POST /api/documents/review/{document_id}/ask-llm` - Query LLM directly to analyze and explain specific risky clauses
- `POST /api/documents/chat/{document_id}` - Real-time AI chat session regarding document details
- `POST /api/documents/review/{document_id}/suggest` - Ask AI structural or alternative language suggestions
- `POST /api/documents/review/{document_id}/suggestion-action` - Accept or reject AI-provided suggestions

### Messaging
- `POST /api/messages/send` - Send in-app chat message between client/admin
- `GET /api/messages/list/{other_user_id}` - Fetch chat history for users

### Contracts & Obligations
- `POST /api/contracts/share-with-client` - Share specific contracts to clients
- `GET /api/contracts/from-legal` - List contracts received from legal
- `POST /api/contracts/accept/{contract_id}` - Client accepts specific contract
- `POST /api/contracts/reject/{contract_id}` - Client rejects specific contract
- `POST /api/contracts/accept-mandate` - Mandate acceptance
- `POST /api/contracts/reject-mandate` - Mandate rejection
- `GET /api/contracts/download/{contract_id}` - Download contract file

### Templates Management
- `POST /api/templates/upload` - Admin uploads a new standard baseline template
- `GET /api/templates/analysis/{template_id}` - View clause breakdown of a template
- `GET /api/templates/download/{template_id}` - Download a template file
- `GET /api/templates/list` - List all uploaded admin templates
- `GET /api/templates/latest-nda` - Fetch the most recently added NDA format

### Activity Verification
- `GET /api/activity/list` - Complete log history of app actions

## Dependencies

**Backend (`requirements.txt`):**
- **Core APIs:** `fastapi`, `uvicorn`, `python-multipart`, `python-dotenv`, `pydantic[email]`
- **Authentication:** `PyJWT`
- **Database Support:** `psycopg2-binary`, `pgvector`
- **Cloud & Network:** `boto3`, `requests`
- **Document Extractors:** `pandas`, `pillow`, `pdfplumber`, `python-docx`, `flask`, `spacy`, `numpy`
- **Google Integration:** `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
- **AI/ML/LangChain:** `sentence-transformers`, `langchain`, `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-groq`, `langchain-mistralai`, `langchain-text-splitters`

**Frontend (`package.json`):**
- **Core Application:** `react`, `react-dom`, `react-router-dom`, `react-markdown`
- **Build/Dev:** `vite`, `eslint`, `@vitejs/plugin-react`

## Complete Project Flows

1. The legal team has its own credentials. The legal admin can add legal members, and they share a common dashboard.
2. The legal team can invite clients via email by providing a username and password. The email is sent using EmailJS.
3. Clients log in using the provided credentials.
4. The client and legal team can communicate via chat.
5. When a client logs in for the first time, an NDA uploaded by the legal team (in the standard templates section of the legal dashboard) is automatically shared with the client.
6. The client can either accept or reject the document. If the client rejects it, they can upload either a redlined document or their own contract.
7. In the case of a redlined document, the uploaded file is displayed in the legal team’s client workspace. When the legal team clicks "Review," the redlined contract opens in Google Docs, where they can manually accept or reject changes.
8. In the case of a client’s own contract:
   - The uploaded contract is processed to extract and classify clauses.
   - These clauses are compared with standard clauses using SBERT.
   - Based on similarity scores, a threshold is applied to classify risks as Low, Medium, or High, with risk tagging for each clause.
   - The legal team can review all risks in a side-by-side viewer, where standard clauses are shown on one side and the client’s clauses on the other.
   - When a specific clause is selected, the legal team can run AI analysis to understand why it is considered risky.
   - The legal team can edit and comment on the client’s clauses.
   - Finally, the edited version can be downloaded and shared with the client, who can view it as a redlined document in Google Docs.
9. The legal team can also interact with an AI assistant for general queries regarding clauses.
10. This workflow (both redlined and own contract flows) applies to all contract types such as RA, SOW, and MSA.
11. Once both the client and legal team accept the document, they can upload the final contract and mark it as finalized. The legal team makes the final decision, and the finalized document is displayed on both the legal and client dashboards.

---
