# LACCIS React Application

Modern React + Vite frontend for the Legal Clause Classification Intelligence System.

## 🚀 Quick Start

### Prerequisites
- Node.js v18+ installed
- Python 3.8+ installed
- Backend running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
```bash
cd frontend-react
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 📁 Project Structure

```
frontend-react/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Navbar.jsx       # Navigation bar
│   │   ├── ClientForm.jsx   # Client creation form
│   │   ├── ClientsTable.jsx # Clients list table
│   │   ├── StatsCard.jsx    # Statistics card
│   │   ├── UploadArea.jsx   # File upload with drag-and-drop
│   │   ├── DocumentsTable.jsx # Documents list table
│   │   └── Modal.jsx        # Modal dialog
│   ├── pages/               # Page components
│   │   ├── Login.jsx        # Login page
│   │   ├── Dashboard.jsx    # Admin dashboard
│   │   └── Upload.jsx       # Document upload page
│   ├── App.jsx              # Main app component with routing
│   ├── App.css              # Global styles
│   └── main.jsx             # Entry point
├── package.json
└── vite.config.js
```

## 🎨 Features

### ✨ Modern UI/UX
- **Glassmorphism Design** - Beautiful frosted glass effects
- **Smooth Animations** - Micro-interactions and transitions
- **Responsive Layout** - Works on all screen sizes
- **Dark Theme** - Easy on the eyes

### 🔐 Authentication
- JWT-based authentication
- Role-based routing (Admin/Client)
- Persistent login sessions

### 👥 Client Management (Admin)
- Create new clients
- Auto-generate credentials
- Send credentials via SMTP email
- View all clients in real-time

### 📄 Document Upload (Client)
- Drag-and-drop file upload
- Multiple file support
- Upload progress tracking
- File type validation (PDF, DOC, DOCX, TXT)

### 📊 Dashboard Statistics
- Total documents count
- Active clients count
- Real-time updates

## 🛠️ Technology Stack

- **React 19** - UI library
- **Vite 7** - Build tool and dev server
- **React Router** - Client-side routing
- **CSS3** - Styling with custom properties
- **Fetch API** - HTTP requests

## 🔧 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🌐 API Integration

The app connects to the FastAPI backend at `http://localhost:8000`

### Endpoints Used:
- `POST /api/auth/login` - User authentication
- `POST /api/clients/create` - Create new client (admin)
- `GET /api/clients/list` - List all clients (admin)
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/list` - List documents
- `GET /api/documents/stats` - Get statistics (admin)

## 🔑 Default Credentials

**Admin Account:**
- Email: `admin@laccis.com`
- Password: `admin123`

## 🎯 Usage Flow

### For Legal Team (Admin):
1. Login with admin credentials
2. Navigate to Dashboard
3. Fill in client name and email
4. Click "Send Credentials via Email"
5. System generates password and emails it to client
6. View clients and statistics

### For Clients:
1. Receive email with credentials
2. Login with provided credentials
3. Upload contract documents via drag-and-drop
4. View uploaded documents

## 🚀 Deployment

### Build for Production:
```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

### Deploy Options:
- **Vercel** - `vercel deploy`
- **Netlify** - Drag & drop `dist` folder
- **GitHub Pages** - Use `gh-pages` package
- **Docker** - Use provided Dockerfile

## 🔒 Security Notes

⚠️ **For Production:**
- Enable HTTPS
- Update CORS settings in backend
- Use environment variables for API URL
- Implement rate limiting
- Add input sanitization
- Enable CSP headers

## 📝 Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

Update API calls to use:
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

## 🐛 Troubleshooting

**Issue: "Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check CORS settings in FastAPI
- Verify API_URL in components

**Issue: "Module not found"**
- Run `npm install`
- Delete `node_modules` and reinstall

**Issue: "Port 5173 already in use"**
- Change port in `vite.config.js`:
```javascript
export default defineConfig({
  server: { port: 3000 }
})
```

## 📄 License

MIT License

---

Built with ❤️ using React + Vite
