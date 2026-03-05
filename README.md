# LACCIS - Legal Clause Classification Intelligence System

A modern web application for legal document management with intelligent clause classification.

## 🎯 Features

- 🔐 **Secure Authentication** - JWT-based authentication for legal teams and clients
- 📧 **SMTP Email Integration** - Automatically send login credentials to clients via Gmail
- 📄 **Document Upload** - Drag-and-drop interface for contract documents
- 👥 **Client Management** - Legal team dashboard for managing client access
- 🎨 **Beautiful UI** - Modern React app with glassmorphism design and smooth animations
- 📱 **Responsive** - Works seamlessly on all devices

## 📁 Project Structure

```
LACCIS/
├── frontend/              # React + Vite application
│   ├── src/
│   │   ├── components/   # Reusable React components
│   │   ├── pages/        # Page components (Login, Dashboard, Upload)
│   │   ├── App.jsx       # Main app with routing
│   │   └── main.jsx      # Entry point
│   └── package.json
├── backend/              # FastAPI backend
│   ├── main.py          # API server
│   └── requirements.txt
    └── extracted_texts/ # Auto-created directory for transient text extractions from PDFs
```

## 🚀 Quick Start

### Prerequisites
- Node.js v18+ 
- Python 3.8+

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Environment Configuration** Create a `.env` file in the backend matching the `.env.ex` structure. Provide database connectivity, AWS S3 keys, and your EmailJS configuration.

3. **Run the FastAPI server:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 🔑 Default Credentials

**Admin Account:**
- Email: `admin@laccis.com`
- Password: `admin123`

## 📖 Usage

### For Legal Team (Admin)

1. Login with admin credentials
2. Navigate to the dashboard
3. Add new clients by entering their name and email
4. System automatically generates credentials and sends them via email
5. View all clients and uploaded documents statistics
6. Review client-uploaded agreements against **Standard Templates** (which the legal team provisions) using the AI clause extraction and risk assessment pipeline.

### For Clients

1. Receive login credentials via email
2. Login with provided credentials
3. Upload contract documents using drag-and-drop
4. View all uploaded documents and safely share fully reviewed documents back.

## 🛠️ Technology Stack

**Frontend:**
- React 19 - UI library
- Vite 7 - Build tool and dev server
- React Router - Client-side routing
- CSS3 - Modern styling with glassmorphism

**Backend:**
- FastAPI - Modern Python web framework
- PostgreSQL - Robust relational database for users, documents, and derived clauses
- AWS S3 - Secure object storage for the actual PDF/Word documents
- ChromaDB - Vector database for SBERT-based semantic similarity checking of clauses
- Mistral AI & Langchain - For complex text extraction, OCR, and document summarization
- PyJWT - Secure Authentication

## 📡 API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/clients/create` - Create new client (admin only)
- `GET /api/clients/list` - List all clients (admin only)
- `POST /api/documents/upload` - Upload document directly to S3 and trigger NLP Extraction
- `GET /api/documents/list` - List documents available to the requesting user
- `GET /api/documents/stats` - Document statistics (admin only)
- `GET /api/documents/review/{doc_id}` - Fetch AI clause-by-clause review for a document

## ⚙️ Configuration (.env)

Make sure you configure your backend `.env` file correctly with these exact keys:

```ini
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET_KEY=your_secure_random_string
AWS_ACCESS_KEY="aws_key"
AWS_SECRET_KEY="aws_secret"
REGION="aws_region"
BUCKET_NAME="aws_s3_bucket"
MISTRAL_API_KEY="mistral_key"

# EmailJS settings
EMAILJS_SERVICE_ID=your_service
EMAILJS_TEMPLATE_ID=your_template
EMAILJS_PUBLIC_KEY=your_pub
EMAILJS_PRIVATE_KEY=your_priv
```

## 🚀 Production Build

### Frontend:
```bash
cd frontend
npm run build
```

This creates an optimized build in the `dist/` folder.

### Deployment Options:
- **Vercel** - For frontend
- **Heroku** - For backend
- **Docker** - Containerize both services
- **AWS/Azure/GCP** - Cloud deployment

## 📝 Development Scripts

**Frontend:**
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Lint code
```

**Backend:**
```bash
python main.py   # Start FastAPI server
```

## 🐛 Troubleshooting

**Issue: "Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check CORS settings in FastAPI
- Verify API_URL in frontend components

**Issue: "Email not sending"**
- Verify SMTP credentials
- Check Gmail App Password is correct
- Ensure 2FA is enabled on Gmail account

**Issue: "Port already in use"**
- Change port in `vite.config.js` or `main.py`
- Kill existing processes on the port

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using React + Vite + FastAPI
