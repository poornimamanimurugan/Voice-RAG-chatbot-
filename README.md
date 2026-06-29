# 🤖 RAG Voice Chatbot

A production-ready Retrieval-Augmented Generation (RAG) chatbot with voice capabilities, built with Python, React, and modern AI technologies.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **🎤 Voice Input & Output**: Speak to the chatbot using Web Speech API
- **📚 RAG (Retrieval-Augmented Generation)**: Chatbot answers based on your documents
- **🔍 Smart Search**: Semantic search using Chroma DB embeddings
- **🤖 Claude AI**: Powered by Anthropic's Claude for intelligent responses
- **💬 Chat Widget**: Sleek bottom-left corner widget that stays accessible
- **📱 Responsive Design**: Works on desktop and mobile
- **🔄 Conversation History**: Maintains context across multiple messages
- **📄 Document Management**: Upload, view, and manage your knowledge base
- **⚡ Real-time**: Instant responses with streaming support

## 🎯 What is RAG?

RAG (Retrieval-Augmented Generation) is a technique where:
1. User asks a question
2. System searches your documents for relevant information
3. AI uses that information to generate a more accurate answer

This means your chatbot knows about YOUR specific information, not just general knowledge.

## 🗂️ Project Structure

```
rag-voice-chatbot/
├── backend/
│   ├── app.py                    # Flask server with all API endpoints
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Template for secrets
│   └── chroma_data/              # Vector database storage (auto-created)
│
├── frontend/
│   └── index.html                # Complete single-page app
│
├── SETUP_INSTRUCTIONS.md         # Detailed setup guide
└── README.md                     # This file
```

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Anthropic API Key (free at console.anthropic.com)
- Modern web browser (Chrome, Edge, Safari)

### 1. Install Backend Dependencies
```bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate or Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2. Configure API Key
Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_key_here
```

### 3. Start Backend Server
```bash
python app.py
# Should show: Running on http://0.0.0.0:5000
```

### 4. Start Frontend (New Terminal)
```bash
cd frontend
python -m http.server 8000
# Or: npx http-server -p 8000
```

### 5. Open Browser
```
http://localhost:8000
```

✅ **Done!** Chatbot widget is in the bottom-left corner.

## 📋 Full Setup Instructions

For detailed setup with troubleshooting, see [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)

## 🔑 Key Components

### Backend (Python Flask)

**Core Features:**
- RESTful API endpoints for chat, document upload, and retrieval
- Chroma DB integration for semantic search
- Claude AI integration for response generation
- CORS enabled for frontend communication

**Main Endpoints:**
- `POST /api/chat` - Send message and get response
- `POST /api/upload-documents` - Add documents to knowledge base
- `GET /api/get-documents` - Retrieve all documents
- `POST /api/delete-documents` - Remove documents
- `GET /api/health` - Health check

### Frontend (HTML/CSS/JavaScript)

**Main Components:**
- Chat widget fixed to bottom-left corner
- Message display with auto-scroll
- Text input with Enter-to-send
- Voice input using Web Speech API
- Document management interface
- Responsive design for mobile

**Technologies:**
- Vanilla JavaScript (no frameworks)
- CSS Grid & Flexbox for layout
- Web Speech API for voice
- Fetch API for backend communication

## 💻 How It Works

### User sends message:
1. **Frontend**: Captures message from text input or voice
2. **Backend**: Receives message via POST /api/chat
3. **Backend**: Searches Chroma DB for relevant documents
4. **Backend**: Calls Groq with context + message
5. **Claude**: Generates intelligent response
6. **Frontend**: Displays response and reads it aloud

```
User Input
    ↓
[Frontend] 🎤📝
    ↓ (HTTP POST)
[Backend Flask] 🐍
    ↓
[Chroma DB] 🔍 (search for relevant docs)
    ↓
[Claude API] 🤖 (generate response)
    ↓ (JSON response)
[Frontend] 💬 (display & speak)
    ↓
User Reads/Hears Output
```

## 🎨 Customization

### Change Widget Position
In `frontend/index.html`, modify `.chatbot-widget`:
```css
.chatbot-widget {
    position: fixed;
    bottom: 20px;     /* Change to top: 20px */
    left: 20px;       /* Change to right: 20px */
    /* ... rest of styles */
}
```

### Change Colors
Update the gradient colors in CSS:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change #667eea and #764ba2 to your preferred colors */
```

### Change Widget Size
Modify the `.chatbot-widget` dimensions:
```css
width: 380px;   /* Change width */
height: 500px;  /* Change height */
```

## 🔐 Security Considerations

1. **Never commit your API key**
   - Use `.env` files with `.gitignore`
   - Use environment variables in production

2. **Rate Limiting** (for production)
   - Add rate limiting middleware to Flask
   - Implement user authentication
   - Monitor API usage

3. **Data Privacy**
   - Chroma DB stores locally by default
   - For cloud deployment, use encrypted storage
   - Don't store sensitive PII without encryption

## 📊 Performance Tips

1. **Document Size**: Keep documents under 10,000 words
2. **Number of Results**: Retrieve top 3-5 documents (adjust in code)
3. **Caching**: Consider caching frequent queries
4. **Async Processing**: For production, use async tasks for heavy operations

## 🐛 Common Issues & Solutions

### Backend won't start
```
Error: Port 5000 already in use
Solution: Kill process or change port in app.py
```

### Voice not working
```
Error: Speech recognition not available
Solution: Use Chrome/Edge, check microphone permissions
```

### API Key invalid
```
Error: 401 Unauthorized
Solution: Check key at console.anthropic.com, make sure it's set in .env
```

### CORS errors
```
Error: Access-Control-Allow-Origin
Solution: Backend already has CORS enabled, restart server
```

## 📚 Documentation

- [Setup Instructions](./SETUP_INSTRUCTIONS.md) - Detailed setup guide
- [Chroma DB Docs](https://docs.trychroma.com/) - Vector database guide
- [Flask Docs](https://flask.palletsprojects.com/) - Backend framework

## 🚀 Deployment

### Antigravity
```bash
# Set environment variables in Antigravity dashboard
ANTHROPIC_API_KEY=your_key

# Deploy backend
antigravity deploy

# Deploy frontend to Vercel/Netlify
```

### Heroku
```bash
heroku create app-name
heroku config:set ANTHROPIC_API_KEY=your_key
git push heroku main
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## 📈 Usage Statistics

The chatbot tracks:
- Conversation history (for context)
- Document count in knowledge base
- Message timestamps
- API health status

Monitor via:
- Browser DevTools (F12)
- Backend logs in terminal
- `/api/health` endpoint

## 🎓 Learning Resources

Perfect for learning:
- **Flask Basics**: Backend API development
- **Vector Databases**: Semantic search with embeddings
- **RAG Architecture**: Building AI systems
- **Web Speech API**: Voice input/output in browsers
- **Frontend Integration**: Connecting frontend to backend

## 💡 Future Enhancements

Potential improvements:
- [ ] User authentication & profiles
- [ ] Multiple conversation threads
- [ ] Document upload as PDF/DOCX
- [ ] Rate limiting & usage analytics
- [ ] Custom model selection
- [ ] Streaming responses
- [ ] Web search integration
- [ ] Mobile app (React Native)

## 📝 API Response Examples

### Chat Endpoint
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is your company about?",
    "history": []
  }'
```

Response:
```json
{
  "success": true,
  "response": "Based on our knowledge base, the company specializes in AI chatbots...",
  "timestamp": "2024-01-20T10:30:00"
}
```

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests
- Share your use cases

## 📄 License

MIT License - Use freely for personal and commercial projects

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [Anthropic Claude](https://www.anthropic.com/)
- Vector search by [Chroma DB](https://www.trychroma.com/)
- Voice powered by [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

## 🎉 Getting Started

Ready to build? Start with [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)

**Questions?** Check the troubleshooting section or review the code comments.

**Happy building!** 🚀
