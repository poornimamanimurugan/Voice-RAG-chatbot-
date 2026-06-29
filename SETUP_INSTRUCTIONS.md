# RAG Voice Chatbot - Complete Setup Guide

## 📋 Overview
This is a full-stack RAG (Retrieval-Augmented Generation) voice chatbot with:
- **Backend**: Python Flask server with Groq AI integration
- **Frontend**: HTML/CSS/JavaScript with a bottom-left corner widget
- **Database**: Chroma DB for vector storage and semantic search
- **Voice**: Web Speech API for voice input/output

---

## 🛠️ Prerequisites

Before you start, make sure you have:

1. **Python 3.8+** installed ([Download here](https://www.python.org/downloads/))
   - Verify: `python --version`

2. **pip** (Python package manager - comes with Python)
   - Verify: `pip --version`

3. **Groq API Key** 
   - Go to [console.groq.com](https://console.groq.com/)
   - Sign up or log in
   - Create a new API key
   - Copy it (you'll need it later)

4. **A web browser** that supports:
   - Web Speech API (Chrome, Edge, Safari)
   - Modern JavaScript features

---

## 📁 Project Structure

```
rag-voice-chatbot/
├── backend/
│   ├── app.py                 # Main Flask server (API endpoints)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Template for environment variables
│   └── .env                   # Your secret API keys (create this)
│
├── frontend/
│   └── index.html             # Single-page HTML app with embedded CSS/JS
│
└── SETUP_INSTRUCTIONS.md      # This file
```

---

## 🚀 Step-by-Step Installation

### Step 1: Download and Extract the Project

1. Download the project files
2. Extract them to a folder (e.g., `rag-voice-chatbot/`)
3. Open a terminal/command prompt in the `rag-voice-chatbot/` folder

### Step 2: Set Up the Backend

#### 2.1 Navigate to the Backend Directory
```bash
cd backend
```

#### 2.2 Create a Python Virtual Environment
A virtual environment isolates project dependencies from your system Python.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

#### 2.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (cross-origin requests)
- OpenAI SDK (Groq API - OpenAI compatible)
- Chroma DB (vector database)
- Python-dotenv (environment variables)

**Expected Output:**
```
Successfully installed openai chromadb flask ...
```

#### 2.4 Configure Your API Key

**Option A: Using .env file (Recommended)**

1. Create a new file named `.env` in the `backend/` folder
2. Copy the content from `.env.example`:
   ```
   GROQ_API_KEY=your_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   BACKEND_URL=http://localhost:5000
   ```
3. Replace `your_api_key_here` with your actual API key from console.groq.com

**Option B: Set as environment variable**

*Windows (Command Prompt):*
```bash
set GROQ_API_KEY=your_api_key_here
```

*Windows (PowerShell):*
```bash
$env:GROQ_API_KEY="your_api_key_here"
```

*macOS/Linux:*
```bash
export GROQ_API_KEY="your_api_key_here"
```

### Step 3: Start the Backend Server

Still in the `backend/` folder with virtual environment activated:

```bash
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

✅ **Your backend is running!** Keep this terminal open.

---

## 🎨 Step 4: Set Up the Frontend

### 4.1 Open the Frontend

In a **new terminal/command prompt window** (keep the backend running):

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Start a local web server:

   **Option A: Using Python (Recommended)**
   ```bash
   python -m http.server 8000
   ```

   **Option B: Using Node.js (if you have it)**
   ```bash
   npx http-server -p 8000
   ```

   **Option C: Using any HTTP server you have available**
   ```bash
   # Or use any other simple HTTP server
   ```

3. Open your browser to: **http://localhost:8000**

✅ **You should see the chatbot interface!**

---

## 📝 Step 5: Test the Application

### 5.1 Upload a Document

1. You should see the "Knowledge Base Management" section at the top
2. There's a pre-filled document. You can:
   - Keep it as is
   - Edit it
   - Or add your own document

3. Click **"Upload Document"** button
4. You should see a success message

### 5.2 Test the Chat

1. Look at the **bottom-left corner** - you'll see the chatbot widget
2. Type a message like: **"Tell me about the company"**
3. Press **Enter** or click the **📤 (send)** button
4. The AI will:
   - Search the knowledge base (Chroma DB)
   - Retrieve relevant documents
   - Generate a response using Groq AI (llama-3.1-8b-instant)
   - Speak the response using text-to-speech

### 5.3 Test Voice Input

1. Click the **🎤 (microphone)** button in the chatbot
2. The button will turn red and pulse (recording)
3. Speak your question clearly
4. When done, click the mic button again to stop recording
5. Your speech will be transcribed and sent automatically

---

## 🔧 Configuration Options

### Backend Configuration (.env file)

```ini
# Your Groq API key (required)
GROQ_API_KEY=gsk_...

# Flask settings
FLASK_ENV=development          # Use 'production' for deployment
FLASK_DEBUG=True              # Set to False in production

# Backend URL (for frontend to connect)
BACKEND_URL=http://localhost:5000
```

### Frontend Configuration (in index.html)

Look for this line in the JavaScript section:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Change it if your backend is on a different URL.

---

## 🐛 Troubleshooting

### Problem: "Backend is not running" message
**Solution:**
- Make sure you started the Flask server with `python app.py` in the backend folder
- Check that you're in the correct directory and virtual environment is activated
- Port 5000 might be in use. You can change it in app.py at the bottom

### Problem: API Key Error
**Solution:**
- Double-check your API key is correct and active in console.groq.com
- Make sure the `.env` file is in the same folder as `app.py`
- Restart the Flask server after changing the API key

### Problem: Voice input not working
**Solution:**
- Not all browsers support Web Speech API (Chrome and Edge work best)
- Check your browser's microphone permissions
- Try Chrome or Edge if using Safari or Firefox

### Problem: "CORS error" in browser console
**Solution:**
- The backend CORS is already enabled in the code
- Restart the backend server
- Make sure you're accessing via `http://localhost:8000` (not file://)

### Problem: Documents not appearing
**Solution:**
- Click "Refresh Documents" button
- Check browser console (F12) for error messages
- Make sure the backend is running

---

## 📚 Understanding the Code Structure

### Backend (app.py)

| Function | Purpose |
|----------|---------|
| `get_relevant_documents()` | Searches Chroma DB for relevant documents |
| `build_rag_context()` | Formats retrieved documents for the AI |
| `generate_response()` | Calls Groq API with RAG context |
| `/api/chat` | Main endpoint for chatting |
| `/api/upload-documents` | Endpoint for adding documents to knowledge base |
| `/api/get-documents` | Retrieve all documents |
| `/api/delete-documents` | Remove documents from knowledge base |

### Frontend (index.html)

| Component | Purpose |
|-----------|---------|
| `.chatbot-widget` | The bottom-left corner chat box |
| `sendMessage()` | Sends user message to backend |
| `toggleVoiceInput()` | Starts/stops speech recognition |
| `speakResponse()` | Reads bot response aloud |
| `uploadDocument()` | Adds document to knowledge base |
| Web Speech API | Handles voice input/output |

---

## 🚀 Deploying to Production

### Using Antigravity (Recommended)

1. **Prepare your files:**
   - Make sure `.env` has your real API key
   - Test everything locally first

2. **Upload to Antigravity:**
   - Go to [antigravity.dev](https://antigravity.dev/)
   - Upload your backend folder
   - Upload your frontend folder to a static hosting (Vercel, Netlify, etc.)

3. **Update Frontend URL:**
   - Change `API_BASE_URL` in index.html to your production backend URL

4. **Set Environment Variables:**
   - In Antigravity, set `GROQ_API_KEY` as an environment variable

### Using Other Platforms

**Heroku:**
```bash
heroku create your-app-name
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

**Railway.app:**
- Connect your GitHub repo
- Add `GROQ_API_KEY` in variables
- Deploy automatically

**Render:**
- Create new Web Service
- Connect your repo
- Add environment variables
- Deploy

---

## 📖 API Reference

### POST /api/chat
Send a message and get a response.

**Request:**
```json
{
  "message": "Tell me about the company",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "The company was founded...",
  "timestamp": "2024-01-20T10:30:00"
}
```

### POST /api/upload-documents
Add documents to the knowledge base.

**Request:**
```json
{
  "documents": [
    {
      "content": "Document text here",
      "source": "Company Manual"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added 1 documents to knowledge base",
  "document_ids": ["doc_123"]
}
```

### GET /api/get-documents
Retrieve all documents in the knowledge base.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "documents": {
    "ids": [...],
    "documents": [...],
    "metadatas": [...]
  }
}
```

### POST /api/delete-documents
Remove documents from the knowledge base.

**Request:**
```json
{
  "doc_ids": ["doc_123", "doc_456"]
}
```

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Groq API Docs**: https://console.groq.com/docs/
- **Chroma DB Docs**: https://docs.trychroma.com/
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

---

## 💡 Tips & Best Practices

1. **Large Documents**: For very large documents, split them into chunks before uploading
2. **API Costs**: Monitor your Groq API usage to avoid unexpected bills
3. **Security**: Never commit your `.env` file with real API keys
4. **Performance**: The chatbot uses Cosine similarity for fast semantic search
5. **Customization**: Edit the CSS in index.html to change colors and widget size

---

## 📞 Getting Help

If you encounter issues:

1. Check the browser console (F12 → Console tab)
2. Check the terminal running the Flask server for error messages
3. Verify all prerequisites are installed
4. Make sure API key is valid and has credits
5. Try restarting both backend and frontend

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🎉 You're All Set!

Your RAG Voice Chatbot is ready to use. 

**Next Steps:**
1. ✅ Backend running on `http://localhost:5000`
2. ✅ Frontend running on `http://localhost:8000`
3. ✅ Chatbot widget in bottom-left corner
4. ✅ Upload your own documents
5. ✅ Start chatting with voice or text!

Happy chatting! 🤖💬
