# 🚀 Quick Reference Guide

## ⚡ Super Quick Start

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
# Create .env with: GROQ_API_KEY=your_key
python app.py

# Terminal 2: Frontend (NEW TERMINAL!)
cd frontend
python -m http.server 8000

# Browser: http://localhost:8000
```

---

## 📋 Common Commands

### Setup Commands

| Command | Purpose |
|---------|---------|
| `python -m venv venv` | Create virtual environment |
| `venv\Scripts\activate` | Activate venv (Windows) |
| `source venv/bin/activate` | Activate venv (Mac/Linux) |
| `pip install -r requirements.txt` | Install dependencies |
| `python app.py` | Start backend server |
| `python -m http.server 8000` | Start frontend server |

### Virtual Environment (Windows)

```bash
# Create
python -m venv venv

# Activate
venv\Scripts\activate

# Deactivate
deactivate
```

### Virtual Environment (Mac/Linux)

```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate

# Deactivate
deactivate
```

### Check Installation

```bash
# Check Python
python --version

# Check pip
pip --version

# List installed packages
pip list

# Check backend is running
curl http://localhost:5000/api/health

# Check frontend is accessible
curl http://localhost:8000
```

---

## 🔧 Configuration Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `requirements.txt` installed
- [ ] `.env` file created in `backend/` folder
- [ ] `GROQ_API_KEY` set in `.env`
- [ ] Backend started with `python app.py`
- [ ] Frontend started with `python -m http.server 8000`
- [ ] Browser opened to `http://localhost:8000`
- [ ] Chatbot widget visible in bottom-left corner

---

## 🚨 Troubleshooting Quick Fixes

### Backend Won't Start

```bash
# Check if port 5000 is in use
netstat -an | grep 5000  # Mac/Linux
netstat -ano | findstr 5000  # Windows

# Kill the process using port 5000
# Windows: taskkill /PID [PID] /F
# Mac/Linux: kill -9 [PID]

# Or change port in app.py (last line):
# app.run(port=5001)  # Use port 5001 instead
```

### Virtual Environment Not Activating

**Windows:**
```bash
# If you get "cannot be loaded" error, try:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activate again
venv\Scripts\activate
```

**Mac/Linux:**
```bash
# Make sure you're in the right directory
pwd  # Check current directory
cd /path/to/backend
source venv/bin/activate
```

### API Key Not Working

```bash
# Check if .env file exists
ls backend/.env  # Mac/Linux
dir backend\.env  # Windows

# Check contents (should have GROQ_API_KEY=...)
cat backend/.env  # Mac/Linux
type backend\.env  # Windows

# If using Windows PowerShell with special characters, try:
$env:GROQ_API_KEY="your_key_here"
```

### Import Errors

```bash
# Make sure virtual environment is activated
# Then reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Backend port 5000
lsof -i :5000  # Check what's using it
kill -9 <PID>  # Kill the process

# Or use different port
# Edit app.py, change: app.run(port=5001)
```

---

## 🌐 URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `http://localhost:8000` | Chat interface |
| Backend | `http://localhost:5000` | API server |
| Health Check | `http://localhost:5000/api/health` | Backend status |
| API Chat | `http://localhost:5000/api/chat` | Chat endpoint |
| API Docs | `http://localhost:5000/api` | API info |

---

## 📱 Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Chat | ✅ | ✅ | ✅ | ✅ |
| Voice Input | ✅ | ❌ | ✅ | ✅ |
| Voice Output | ✅ | ✅ | ✅ | ✅ |
| Overall | Best | Good | Good | Best |

**Recommendation:** Use Chrome or Edge for full functionality

---

## 🎯 API Endpoints Quick Reference

### Chat
```bash
POST http://localhost:5000/api/chat
Content-Type: application/json

{
  "message": "Your question",
  "history": []
}
```

### Upload Documents
```bash
POST http://localhost:5000/api/upload-documents
Content-Type: application/json

{
  "documents": [
    {
      "content": "Document text",
      "source": "Document name"
    }
  ]
}
```

### Get Documents
```bash
GET http://localhost:5000/api/get-documents
```

### Delete Document
```bash
POST http://localhost:5000/api/delete-documents
Content-Type: application/json

{
  "doc_ids": ["doc_id_1", "doc_id_2"]
}
```

### Health Check
```bash
GET http://localhost:5000/api/health
```

---

## 🔍 Debugging Tips

### Browser Console Errors (Press F12)

```javascript
// Check if backend is reachable
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(e => console.log('Backend error:', e))

// Check if messages are being sent
// Look for POST requests to /api/chat in Network tab
```

### Backend Console Logs

```python
# The terminal running Flask will show:
# - All API requests
# - Error messages
# - Database operations
# - API responses

# Example good output:
# [2024-01-20 10:30:00] Searching Chroma DB...
# [2024-01-20 10:30:01] Calling Groq API...
# [2024-01-20 10:30:02] Response generated successfully
```

### Check Database

```bash
# Documents are stored in: backend/chroma_data/
# This is a local SQLite database

# You can query it with Python:
cd backend
python
>>> import chromadb
>>> client = chromadb.PersistentClient(path="./chroma_data")
>>> collection = client.get_or_create_collection("rag_documents")
>>> docs = collection.get()
>>> print(docs)
```

---

## 🎨 CSS Variables for Customization

Edit colors in `frontend/index.html`:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to something else like: */
background: linear-gradient(135deg, #FF6B6B 0%, #FF8E72 100%);  /* Red/Orange */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);  /* Green */
background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);  /* Blue */
```

---

## 📊 File Locations Cheat Sheet

```
rag-voice-chatbot/
├── backend/
│   ├── app.py                    ← Main backend code (edit this!)
│   ├── requirements.txt          ← Python dependencies
│   ├── .env                      ← Your secrets (CREATE THIS)
│   ├── .env.example              ← Template for .env
│   ├── venv/                     ← Virtual environment (auto-created)
│   └── chroma_data/              ← Vector database (auto-created)
│
├── frontend/
│   └── index.html                ← All frontend code in one file
│
├── SETUP_INSTRUCTIONS.md         ← Detailed setup
├── README.md                     ← Project overview
└── QUICK_REFERENCE.md           ← This file
```

---

## 🔄 Deployment Checklist

Before deploying to production:

- [ ] Remove `debug=True` from `app.py`
- [ ] Change `FLASK_DEBUG=False` in `.env`
- [ ] Test with production API key
- [ ] Check all API endpoints work
- [ ] Update `API_BASE_URL` in frontend
- [ ] Test on mobile devices
- [ ] Enable HTTPS (required for voice API)
- [ ] Set up rate limiting
- [ ] Monitor API usage and costs

---

## 💰 Cost Estimates

### Groq (llama-3.1-8b-instant)
- **Free tier:** Groq offers free API usage via console.groq.com
- **Pricing:** Pay-per-token (check current rates at console.groq.com)
- **Rate limits:** 30 requests/minute on free tier

**Pro tip:** Monitor usage at [console.groq.com](https://console.groq.com/)

---

## 🎓 Learning Paths

### Beginner
1. Read README.md
2. Follow SETUP_INSTRUCTIONS.md
3. Test basic chat
4. Upload your first document

### Intermediate
1. Read through the code comments
2. Modify CSS colors and sizes
3. Customize API responses
4. Add new document types

### Advanced
1. Modify RAG logic in `app.py`
2. Change embedding models
3. Implement user authentication
4. Deploy to production

---

## 🆘 Getting Help

### Documentation
- Full setup: [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)
- Project info: [README.md](./README.md)
- Code comments: Check `app.py` and `index.html`

### Resources
- [Groq Docs](https://console.groq.com/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chroma DB Guide](https://docs.trychroma.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Quick Fixes
1. Restart backend
2. Check console errors (F12)
3. Verify API key
4. Clear browser cache
5. Try different browser

---

## ✅ Success Indicators

You'll know it's working when:

✅ Backend terminal shows: `Running on http://0.0.0.0:5000`
✅ Browser shows chatbot in bottom-left corner
✅ Can type messages and get responses
✅ Voice button records and sends input
✅ Bot speaks responses
✅ Can upload and manage documents
✅ No red errors in browser console (F12)

---

## 🎉 Quick Wins

Once setup is complete, try these quick wins:

1. **Upload 3 different documents** and ask about each
2. **Use voice input** to ask a question
3. **Upload your own data** (resume, company info, etc.)
4. **Customize colors** to match your brand
5. **Share URL** with someone to show them the bot

---

## 📝 Notes

- Save this file for quick reference
- Bookmark the documentation links
- Bookmark `console.groq.com` for API monitoring
- Keep your API key secure (never share it)

---

**Last Updated:** January 2024
**Status:** Ready to Deploy ✅
