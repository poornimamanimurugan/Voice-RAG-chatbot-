"""
RAG Voice Chatbot Backend
A Flask-based backend that integrates Chroma DB for vector storage and RAG capabilities
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json
import pdfplumber
from werkzeug.utils import secure_filename
from openai import OpenAI

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the frontend directory (parent of backend)
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

# Upload folder for PDF files
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load environment variables from backend/.env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Initialize Flask app
app = Flask(__name__)
# Max upload size: 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# Enable CORS for frontend communication
CORS(app)

# Initialize Groq client (uses OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Initialize Chroma DB client
# Using persistent storage to keep your data across sessions
chroma_client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_data"))

# Create or get a collection for your documents
# A collection is like a database table for storing embeddings
collection = chroma_client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"}  # Using cosine similarity for relevance
)

# ============== HELPER FUNCTIONS ==============

def get_relevant_documents(query: str, top_k: int = 3) -> list:
    """
    Search Chroma DB for documents relevant to the user's query
    
    Args:
        query: The user's question
        top_k: Number of relevant documents to retrieve
    
    Returns:
        List of relevant document chunks with their content
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Extract and format the relevant documents
        documents = []
        if results and results['documents'] and len(results['documents']) > 0:
            for doc in results['documents'][0]:  # First query's results
                documents.append(doc)
        
        return documents
    except Exception as e:
        print(f"Error querying Chroma DB: {e}")
        return []


def build_rag_context(query: str) -> str:
    """
    Build a context string from retrieved documents for the LLM
    
    Args:
        query: The user's question
    
    Returns:
        Formatted context string with retrieved documents
    """
    relevant_docs = get_relevant_documents(query)
    
    if not relevant_docs:
        return "No relevant documents found in the knowledge base."
    
    # Format documents into a context string
    context = "Here are relevant documents from our knowledge base:\n\n"
    for i, doc in enumerate(relevant_docs, 1):
        context += f"Document {i}:\n{doc}\n\n"
    
    return context


def generate_response(user_message: str, conversation_history: list) -> str:
    """
    Generate a response using Groq with RAG context
    
    Args:
        user_message: The user's input message
        conversation_history: List of previous messages in the conversation
    
    Returns:
        AI-generated response string
    """
    try:
        # Get relevant documents from Chroma DB
        rag_context = build_rag_context(user_message)
        
        # Build the system prompt with RAG context
        system_prompt = f"""You are a helpful AI assistant with access to a knowledge base.
        
{rag_context}

Please answer the user's question based on the documents provided above. 
If the information is not in the documents, you can say so and provide general knowledge if helpful.
Keep responses concise and relevant."""
        
        # Prepare messages for Groq API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limited to last 10 messages to avoid token limits)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Groq API (OpenAI-compatible)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast free model on Groq
            max_tokens=500,
            messages=messages
        )
        
        # Extract the response text
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an error while processing your request."


# ============== API ENDPOINTS ==============

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint that receives user messages and returns AI responses
    """
    try:
        # Get JSON data from request
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate response using RAG
        ai_response = generate_response(user_message, conversation_history)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-documents', methods=['POST'])
def upload_documents():
    """
    Endpoint to upload and process documents into the vector database
    Accepts JSON with documents to be stored in Chroma DB
    """
    try:
        data = request.json
        documents = data.get('documents', [])
        
        if not documents:
            return jsonify({'error': 'No documents provided'}), 400
        
        # Add documents to Chroma DB
        # Each document gets a unique ID, text content, and metadata
        doc_ids = []
        for i, doc in enumerate(documents):
            doc_id = f"doc_{datetime.now().timestamp()}_{i}"
            
            # Add to collection
            collection.add(
                ids=[doc_id],
                documents=[doc.get('content', '')],
                metadatas=[{
                    'source': doc.get('source', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }]
            )
            doc_ids.append(doc_id)
        
        return jsonify({
            'success': True,
            'message': f'Added {len(doc_ids)} documents to knowledge base',
            'document_ids': doc_ids
        })
        
    except Exception as e:
        print(f"Error uploading documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Endpoint to upload a PDF file and extract its text into the knowledge base
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are accepted'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text_pages = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)

        full_text = '\n'.join(text_pages)
        if not full_text.strip():
            return jsonify({'error': 'No text could be extracted from the PDF'}), 400

        doc_id = f"pdf_{datetime.now().timestamp()}"
        collection.add(
            ids=[doc_id],
            documents=[full_text],
            metadatas=[{
                'source': filename,
                'type': 'pdf',
                'timestamp': datetime.now().isoformat()
            }]
        )

        return jsonify({
            'success': True,
            'message': f'Extracted and stored {len(text_pages)} pages from "{filename}"',
            'document_id': doc_id,
            'pages': len(text_pages)
        })

    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-documents', methods=['GET'])
def get_documents():
    """
    Endpoint to retrieve all documents currently in the knowledge base
    """
    try:
        # Get all documents from collection
        all_docs = collection.get()
        
        return jsonify({
            'success': True,
            'count': len(all_docs['ids']) if all_docs['ids'] else 0,
            'documents': all_docs
        })
        
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-documents', methods=['POST'])
def delete_documents():
    """
    Endpoint to delete documents from the knowledge base
    """
    try:
        data = request.json
        doc_ids = data.get('doc_ids', [])
        
        if not doc_ids:
            return jsonify({'error': 'No document IDs provided'}), 400
        
        # Delete documents from collection
        collection.delete(ids=doc_ids)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {len(doc_ids)} documents'
        })
        
    except Exception as e:
        print(f"Error deleting documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint to verify the backend is running
    """
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Voice Chatbot Backend',
        'timestamp': datetime.now().isoformat()
    })


# Serve the frontend at the root URL
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')


# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create chroma_data directory if it doesn't exist
    os.makedirs('./chroma_data', exist_ok=True)
    
    # Run Flask app in debug mode (set to False in production)
    app.run(
        host='0.0.0.0',      # Listen on all network interfaces
        port=5000,            # Port number
        debug=True            # Auto-reload on code changes
    )
