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
└── data/                # Auto-created data storage
    └── uploads/         # Uploaded documents
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

2. **Configure SMTP settings in `backend/main.py`:**
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-char-app-password"  # Gmail App Password
SMTP_FROM_EMAIL = "your-email@gmail.com"
```

3. **Run the FastAPI server:**
```bash
python main.py
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

### For Clients

1. Receive login credentials via email
2. Login with provided credentials
3. Upload contract documents using drag-and-drop
4. View all uploaded documents

## 🛠️ Technology Stack

**Frontend:**
- React 19 - UI library
- Vite 7 - Build tool and dev server
- React Router - Client-side routing
- CSS3 - Modern styling with glassmorphism

**Backend:**
- FastAPI - Modern Python web framework
- JWT - Authentication
- SMTP - Email delivery
- Python 3.13

## 📡 API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/clients/create` - Create new client (admin only)
- `GET /api/clients/list` - List all clients (admin only)
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/list` - List documents
- `GET /api/documents/stats` - Document statistics (admin only)

## 📧 SMTP Configuration

### For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password in `SMTP_PASSWORD`

### For Other Email Providers:
Update the SMTP settings in `backend/main.py` accordingly.

## 🔒 Security Notes

⚠️ **Important for Production:**
- Change `SECRET_KEY` in `main.py`
- Use a proper database instead of JSON files
- Implement password hashing (bcrypt)
- Use HTTPS
- Add rate limiting
- Implement proper error handling
- Add input validation
- Enable CORS properly
- Use environment variables for sensitive data

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
