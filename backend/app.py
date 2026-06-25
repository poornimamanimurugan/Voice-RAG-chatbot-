"""
RAG Voice Chatbot Backend
A Flask-based backend that integrates Chroma DB for vector storage and RAG capabilities
"""

from flask import (
    Flask, request, jsonify, send_from_directory, session
)
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from datetime import datetime
import re
import numpy as np
import pdfplumber
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
import sqlite3
from functools import wraps
import time

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
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY environment variable is required. "
        "Generate a random secret and set it in backend/.env"
    )
# Max upload size: 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# Session security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv("FLASK_ENV", "development") != "development"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
# Enable CORS for frontend communication
CORS(app,
     supports_credentials=True,
     origins=os.getenv("CORS_ORIGINS", "http://localhost:5000").split(","))

# Rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Initialize Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
LLM_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Initialize Chroma DB client
chroma_client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_data"))

collection = chroma_client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"}
)

# Initialize embedding function for semantic chunking
_embedding_fn = None


def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = DefaultEmbeddingFunction()
    return _embedding_fn


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def cosine_similarity(a: list[float] | None, b: list[float]) -> float:
    if a is None:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _is_low_quality(chunk: str, min_chars: int = 40, min_words: int = 5) -> bool:
    stripped = chunk.strip()
    if len(stripped) < min_chars:
        return True
    words = stripped.split()
    if len(words) < min_words:
        return True
    letter_count = sum(c.isalpha() for c in stripped)
    if letter_count / max(len(stripped), 1) < 0.5:
        return True
    unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
    if unique_ratio < 0.25:
        return True
    lines = [l.strip() for l in stripped.split('\n') if l.strip()]
    if len(lines) >= 3 and len(set(lines)) == 1:
        return True
    return False


def _deduplicate_chunks(chunks: list[str]) -> list[str]:
    seen = set()
    result = []
    for chunk in chunks:
        fingerprint = chunk[:60].strip().lower()
        if fingerprint not in seen:
            seen.add(fingerprint)
            result.append(chunk)
    return result


def semantic_chunk_text(text: str, source: str, max_chunk_size: int = 800, similarity_threshold: float = 0.55) -> list[tuple[str, dict]]:
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    if not paragraphs:
        return []

    try:
        embedding_fn = get_embedding_fn()
        para_embeddings = embedding_fn(paragraphs)
    except Exception:
        return _recursive_fallback_chunking(text, source, max_chunk_size)

    def _add_chunk(chunk_list):
        if chunk_list:
            chunks.append('\n\n'.join(chunk_list))

    chunks = []
    current_chunk = [paragraphs[0]]
    current_centroid = np.array(para_embeddings[0])
    current_size = len(paragraphs[0])

    for i in range(1, len(paragraphs)):
        para = paragraphs[i]
        para_emb = np.array(para_embeddings[i])
        sim = cosine_similarity(current_centroid, para_emb) if current_centroid is not None else -1
        next_size = len(para)

        if current_size + next_size > max_chunk_size:
            _add_chunk(current_chunk)
            if next_size > max_chunk_size:
                sub_sentences = split_into_sentences(para)
                sub_buf = []
                sub_size = 0
                for s in sub_sentences:
                    if sub_size + len(s) > max_chunk_size and sub_buf:
                        chunks.append(' '.join(sub_buf))
                        sub_buf = [s]
                        sub_size = len(s)
                    else:
                        sub_buf.append(s)
                        sub_size += len(s)
                if sub_buf:
                    chunks.append(' '.join(sub_buf))
                current_chunk = []
                current_centroid = None
                current_size = 0
            else:
                current_chunk = [para]
                current_centroid = para_emb
                current_size = next_size
        elif sim < similarity_threshold and current_chunk:
            _add_chunk(current_chunk)
            current_chunk = [para]
            current_centroid = para_emb
            current_size = next_size
        else:
            current_chunk.append(para)
            n = len(current_chunk)
            current_centroid = (current_centroid * (n - 1) + para_emb) / n if current_centroid is not None else para_emb
            current_size += next_size

    _add_chunk(current_chunk)

    # Post-process: split any oversized chunks by sentence boundary
    final_chunks = []
    for raw in chunks:
        if len(raw) > max_chunk_size:
            sub = split_into_sentences(raw)
            buf = []
            buf_size = 0
            for s in sub:
                if buf_size + len(s) > max_chunk_size and buf:
                    final_chunks.append(' '.join(buf))
                    buf = [s]
                    buf_size = len(s)
                else:
                    buf.append(s)
                    buf_size += len(s)
            if buf:
                final_chunks.append(' '.join(buf))
        else:
            final_chunks.append(raw)
    chunks = final_chunks

    # Quality filters
    before = len(chunks)
    chunks = [c for c in chunks if not _is_low_quality(c)]
    chunks = _deduplicate_chunks(chunks)
    after = len(chunks)
    if before != after:
        print(f"Quality filter: removed {before - after} low-quality chunks from '{source}'")

    return [(chunk, {
        'source': source,
        'chunk': i,
        'total_chunks': len(chunks),
        'timestamp': datetime.now().isoformat()
    }) for i, chunk in enumerate(chunks)]


def _recursive_fallback_chunking(text: str, source: str, max_chunk_size: int = 800) -> list[tuple[str, dict]]:
    sentences = split_into_sentences(text)
    chunks = []
    current = []
    current_size = 0

    for s in sentences:
        if current_size + len(s) > max_chunk_size and current:
            chunks.append(' '.join(current))
            current = [s]
            current_size = len(s)
        else:
            current.append(s)
            current_size += len(s)

    if current:
        chunks.append(' '.join(current))

    return [(chunk, {
        'source': source,
        'chunk': i,
        'total_chunks': len(chunks),
        'timestamp': datetime.now().isoformat()
    }) for i, chunk in enumerate(chunks)]


# ============== DATABASE SETUP ==============

DB_PATH = os.path.join(BASE_DIR, "users.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    admin_password = os.getenv("ADMIN_PASSWORD")
    user_password = os.getenv("USER_PASSWORD")
    if not admin_password or not user_password:
        raise RuntimeError(
            "ADMIN_PASSWORD and USER_PASSWORD environment variables must be set. "
            "Configure them in backend/.env"
        )
    default_users = [
        ("admin", admin_password, "admin"),
        ("user", user_password, "user"),
    ]
    for username, password, role in default_users:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), role, datetime.now().isoformat())
            )
    conn.commit()
    conn.close()


init_db()


# ============== AUTH DECORATORS ==============

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


# ============== AUTH ENDPOINTS ==============


@app.route("/api/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return jsonify({
        "success": True,
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 200
    return jsonify({
        "authenticated": True,
        "user": {
            "username": session["username"],
            "role": session["role"]
        }
    })


# ============== COST OPTIMIZATION: Q&A Semantic Cache ==============

_qa_cache: list[tuple[list[float], str, str]] = []
MAX_CACHE_SIZE = 100
CACHE_SIMILARITY_THRESHOLD = 0.92


def _get_cached_response(query: str) -> str | None:
    if not _qa_cache:
        return None
    try:
        fn = get_embedding_fn()
        query_emb = fn([query])[0]
        for cached_emb, cached_query, cached_response in _qa_cache:
            sim = cosine_similarity(query_emb, cached_emb)
            if sim >= CACHE_SIMILARITY_THRESHOLD:
                print(f"[CACHE] Hit (sim={sim:.3f}) for: '{query[:50]}...' -> '{cached_query[:50]}...'")
                return cached_response
    except Exception:
        pass
    return None


def _cache_response(query: str, response: str):
    try:
        fn = get_embedding_fn()
        query_emb = fn([query])[0]
        _qa_cache.append((query_emb, query, response))
        if len(_qa_cache) > MAX_CACHE_SIZE:
            _qa_cache.pop(0)
    except Exception:
        pass


# ============== HELPER FUNCTIONS ==============


RETRIEVAL_COUNT = 10
RERANK_TOP_K = 3
_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _reranker


def _rerank(query: str, documents: list[str], top_k: int = RERANK_TOP_K) -> list[tuple[str, float]]:
    if not documents:
        return []
    try:
        reranker = _get_reranker()
        pairs = [[query, doc] for doc in documents]
        scores = reranker.predict(pairs, show_progress_bar=False)
        scored = list(zip(documents, scores.tolist()))
        scored.sort(key=lambda x: x[1], reverse=True)
        print(f"[RERANK] Top {top_k} of {len(scored)}:")
        for i, (doc, score) in enumerate(scored[:top_k]):
            print(f"  [{i}] score={score:.4f} | \"{doc[:80]}...\"")
        return scored[:top_k]
    except Exception as e:
        print(f"[RERANK] Failed ({e}), using original order")
        return [(doc, 0.0) for doc in documents[:top_k]]


def get_relevant_documents(query: str) -> tuple[list, list[float]]:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=RETRIEVAL_COUNT
        )
        documents = []
        if results and results['documents'] and len(results['documents']) > 0:
            documents = results['documents'][0]

        if not documents:
            return [], []

        reranked = _rerank(query, documents, RERANK_TOP_K)
        docs = [d for d, s in reranked]
        scores = [round(s, 4) for d, s in reranked]
        print(f"[RETRIEVAL] Initial: {len(documents)} → Reranked: {len(docs)} chunks")
        return docs, scores
    except Exception as e:
        print(f"Error querying Chroma DB: {e}")
        return [], []


def build_rag_context(query: str) -> tuple[str, list[dict]]:
    docs, scores = get_relevant_documents(query)
    if not docs:
        return "No relevant documents found in the knowledge base.", []
    context = "Here are relevant documents from our knowledge base:\n\n"
    retrieval_info = []
    for i, (doc, score) in enumerate(zip(docs, scores), 1):
        context += f"Document {i}:\n{doc}\n\n"
        retrieval_info.append({"chunk": i, "score": score, "preview": doc[:100]})
    return context, retrieval_info


MAX_HISTORY = int(os.getenv("MAX_HISTORY", "4"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "300"))


def generate_response(user_message: str, conversation_history: list) -> tuple[str, list[dict]]:
    try:
        t0 = time.time()

        cached = _get_cached_response(user_message)
        if cached is not None:
            print(f"[CACHE] Skipped LLM call, returned cached response ({len(cached)} chars)")
            return cached, []

        rag_context, retrieval_info = build_rag_context(user_message)
        t1 = time.time()
        system_prompt = f"""You are a helpful AI assistant. Answer the user's question using ONLY the documents below.

Documents:
{rag_context}

Rules:
- Answer directly from the documents above. Do NOT say the information is missing unless it truly is absent.
- If the documents contain the answer, use them. If they are only partially relevant, use what you can.
- If truly nothing matches, use general knowledge to give a helpful answer.
- Keep responses concise."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history[-MAX_HISTORY:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        last_msg = conversation_history[-1] if conversation_history else {}
        if last_msg.get("role") != "user" or last_msg.get("content") != user_message:
            messages.append({
                "role": "user",
                "content": user_message
            })

        t2 = time.time()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            messages=messages
        )
        t3 = time.time()
        result = response.choices[0].message.content

        _cache_response(user_message, result)

        print(f"[TIMING] RAG: {t1 - t0:.3f}s | LLM: {t3 - t2:.3f}s | Total: {t3 - t0:.3f}s | Tokens in: {response.usage.prompt_tokens if response.usage else '?'} | Tokens out: {response.usage.completion_tokens if response.usage else '?'}")
        return result, retrieval_info

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an error while processing your request.", []


# ============== API ENDPOINTS ==============


@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
@login_required
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        ai_response, retrieval_info = generate_response(user_message, conversation_history)

        return jsonify({
            'success': True,
            'response': ai_response,
            'retrieval': retrieval_info,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-documents', methods=['POST'])
@admin_required
def upload_documents():
    try:
        data = request.json
        documents = data.get('documents', [])

        if not documents:
            return jsonify({'error': 'No documents provided'}), 400

        all_doc_ids = []
        for i, doc in enumerate(documents):
            source = doc.get('source', f'document_{i}')
            chunks = semantic_chunk_text(doc.get('content', ''), source=source)
            for chunk_text, metadata in chunks:
                doc_id = f"doc_{datetime.now().timestamp()}_{i}_{metadata['chunk']}"
                collection.add(
                    ids=[doc_id],
                    documents=[chunk_text],
                    metadatas=[metadata]
                )
                all_doc_ids.append(doc_id)

        return jsonify({
            'success': True,
            'message': f'Added {len(all_doc_ids)} semantic chunks from {len(documents)} documents',
            'document_ids': all_doc_ids
        })

    except Exception as e:
        print(f"Error uploading documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-pdf', methods=['POST'])
@admin_required
def upload_pdf():
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

        chunks = semantic_chunk_text(full_text, source=filename)

        doc_ids = []
        for chunk_text, metadata in chunks:
            doc_id = f"pdf_{datetime.now().timestamp()}_{metadata['chunk']}"
            collection.add(
                ids=[doc_id],
                documents=[chunk_text],
                metadatas=[metadata]
            )
            doc_ids.append(doc_id)

        return jsonify({
            'success': True,
            'message': f'Extracted {len(text_pages)} pages, split into {len(chunks)} semantic chunks from "{filename}"',
            'document_ids': doc_ids,
            'pages': len(text_pages),
            'chunks': len(chunks)
        })

    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-documents', methods=['GET'])
@login_required
def get_documents():
    try:
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
@admin_required
def delete_documents():
    try:
        data = request.json
        doc_ids = data.get('doc_ids', [])

        if not doc_ids:
            return jsonify({'error': 'No document IDs provided'}), 400

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
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Voice Chatbot Backend',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 413


if __name__ == '__main__':
    os.makedirs('./chroma_data', exist_ok=True)
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode
    )
