# 📡 API Usage Examples

This document shows how to use the chatbot API with curl, Python, and JavaScript.

---

## 🔗 Base URL
```
http://localhost:5000
```

---

## 💬 Chat API

### Send a Message and Get Response

**Using cURL:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about the company",
    "history": []
  }'
```

**Using Python:**
```python
import requests
import json

url = "http://localhost:5000/api/chat"

# First message (empty history)
payload = {
    "message": "Tell me about the company",
    "history": []
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Bot: {data['response']}")
```

**Using JavaScript/Fetch:**
```javascript
const message = "Tell me about the company";
const history = [];

fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: message,
        history: history
    })
})
.then(response => response.json())
.then(data => {
    console.log('Bot:', data.response);
})
.catch(error => console.error('Error:', error));
```

**Response:**
```json
{
  "success": true,
  "response": "The company specializes in AI-powered customer service solutions...",
  "timestamp": "2024-01-20T10:30:00"
}
```

---

## 📚 Upload Documents API

### Add Documents to Knowledge Base

**Using cURL:**
```bash
curl -X POST http://localhost:5000/api/upload-documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "Our company was founded in 2020 and specializes in AI chatbots.",
        "source": "Company Overview"
      },
      {
        "content": "We offer 24/7 customer support through our AI platform.",
        "source": "Services"
      }
    ]
  }'
```

**Using Python:**
```python
import requests

url = "http://localhost:5000/api/upload-documents"

documents = [
    {
        "content": "Our company was founded in 2020 and specializes in AI chatbots.",
        "source": "Company Overview"
    },
    {
        "content": "We offer 24/7 customer support through our AI platform.",
        "source": "Services"
    }
]

response = requests.post(url, json={"documents": documents})
data = response.json()

if data['success']:
    print(f"✓ {data['message']}")
    print(f"Document IDs: {data['document_ids']}")
else:
    print(f"✗ Error: {data['error']}")
```

**Using JavaScript/Fetch:**
```javascript
const documents = [
    {
        content: "Our company was founded in 2020 and specializes in AI chatbots.",
        source: "Company Overview"
    },
    {
        content: "We offer 24/7 customer support through our AI platform.",
        source: "Services"
    }
];

fetch('http://localhost:5000/api/upload-documents', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ documents })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('✓', data.message);
        console.log('IDs:', data.document_ids);
    }
})
.catch(error => console.error('Error:', error));
```

**Response:**
```json
{
  "success": true,
  "message": "Added 2 documents to knowledge base",
  "document_ids": ["doc_1704700200.5_0", "doc_1704700200.5_1"]
}
```

---

## 📖 Get Documents API

### Retrieve All Documents from Knowledge Base

**Using cURL:**
```bash
curl -X GET http://localhost:5000/api/get-documents
```

**Using Python:**
```python
import requests

url = "http://localhost:5000/api/get-documents"

response = requests.get(url)
data = response.json()

if data['success']:
    print(f"Total documents: {data['count']}")
    for i, doc_id in enumerate(data['documents']['ids']):
        print(f"\nDocument {i+1}:")
        print(f"  ID: {doc_id}")
        print(f"  Content: {data['documents']['documents'][i][:100]}...")
        print(f"  Source: {data['documents']['metadatas'][i]['source']}")
else:
    print(f"Error: {data['error']}")
```

**Using JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/api/get-documents')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Total documents: ${data.count}`);
            data.documents.ids.forEach((id, i) => {
                console.log(`\nDocument ${i+1}:`);
                console.log(`  ID: ${id}`);
                console.log(`  Content: ${data.documents.documents[i].substring(0, 100)}...`);
            });
        }
    })
    .catch(error => console.error('Error:', error));
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "documents": {
    "ids": ["doc_1704700200.5_0", "doc_1704700200.5_1"],
    "documents": [
      "Our company was founded in 2020...",
      "We offer 24/7 customer support..."
    ],
    "metadatas": [
      {
        "source": "Company Overview",
        "timestamp": "2024-01-20T10:30:00"
      },
      {
        "source": "Services",
        "timestamp": "2024-01-20T10:30:00"
      }
    ]
  }
}
```

---

## 🗑️ Delete Documents API

### Remove Documents from Knowledge Base

**Using cURL:**
```bash
curl -X POST http://localhost:5000/api/delete-documents \
  -H "Content-Type: application/json" \
  -d '{
    "doc_ids": ["doc_1704700200.5_0", "doc_1704700200.5_1"]
  }'
```

**Using Python:**
```python
import requests

url = "http://localhost:5000/api/delete-documents"

# Get document IDs first
response = requests.get("http://localhost:5000/api/get-documents")
docs = response.json()
doc_ids = docs['documents']['ids'][:1]  # Delete first document

# Delete documents
response = requests.post(url, json={"doc_ids": doc_ids})
data = response.json()

if data['success']:
    print(f"✓ {data['message']}")
else:
    print(f"✗ Error: {data['error']}")
```

**Using JavaScript/Fetch:**
```javascript
// Get document IDs first
fetch('http://localhost:5000/api/get-documents')
    .then(r => r.json())
    .then(docs => {
        const docIds = docs.documents.ids.slice(0, 1); // Get first ID
        
        // Delete the document
        return fetch('http://localhost:5000/api/delete-documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_ids: docIds })
        });
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✓', data.message);
        }
    })
    .catch(error => console.error('Error:', error));
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted 2 documents"
}
```

---

## 💚 Health Check API

### Check if Backend is Running

**Using cURL:**
```bash
curl http://localhost:5000/api/health
```

**Using Python:**
```python
import requests

try:
    response = requests.get("http://localhost:5000/api/health")
    data = response.json()
    print(f"✓ Backend Status: {data['status']}")
    print(f"  Service: {data['service']}")
    print(f"  Time: {data['timestamp']}")
except Exception as e:
    print(f"✗ Backend is not running: {e}")
```

**Using JavaScript/Fetch:**
```javascript
fetch('http://localhost:5000/api/health')
    .then(response => response.json())
    .then(data => {
        console.log('✓ Backend Status:', data.status);
        console.log('  Service:', data.service);
    })
    .catch(error => {
        console.error('✗ Backend is not running:', error);
    });
```

**Response:**
```json
{
  "status": "healthy",
  "service": "RAG Voice Chatbot Backend",
  "timestamp": "2024-01-20T10:30:00"
}
```

---

## 🔄 Multi-Turn Conversation Example

### Having a Conversation with Context

**Python Script:**
```python
import requests
import json

BASE_URL = "http://localhost:5000"
history = []

def chat(message):
    """Send message and maintain conversation history"""
    global history
    
    payload = {
        "message": message,
        "history": history
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    data = response.json()
    
    if data['success']:
        # Add to history for next turn
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": data['response']})
        return data['response']
    else:
        return f"Error: {data['error']}"

# Multi-turn conversation
print("You:", "What does your company do?")
response1 = chat("What does your company do?")
print("Bot:", response1)

print("\nYou:", "How many years have you been around?")
response2 = chat("How many years have you been around?")
print("Bot:", response2)

print("\nYou:", "Tell me more about your services")
response3 = chat("Tell me more about your services")
print("Bot:", response3)
```

---

## 🔐 Authentication Example (for Production)

If you add authentication, here's how to use it:

**With API Key:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "message": "Hello",
    "history": []
  }'
```

**With Bearer Token (JWT):**
```javascript
const token = localStorage.getItem('authToken');

fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        message: 'Hello',
        history: []
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 📊 Batch Upload Example

Upload multiple documents from a file:

**Python:**
```python
import requests
import os

BASE_URL = "http://localhost:5000"

def upload_documents_from_folder(folder_path):
    """Upload all text files from a folder"""
    documents = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                documents.append({
                    "content": content,
                    "source": filename
                })
    
    if documents:
        response = requests.post(
            f"{BASE_URL}/api/upload-documents",
            json={"documents": documents}
        )
        data = response.json()
        print(f"✓ Uploaded {len(documents)} documents")
        return data['document_ids']
    else:
        print("No .txt files found in folder")
        return []

# Usage
doc_ids = upload_documents_from_folder("./documents")
print(f"Document IDs: {doc_ids}")
```

---

## 🚀 Advanced: Streaming Response (Future Feature)

Here's how streaming might look once implemented:

```python
import requests

url = "http://localhost:5000/api/chat-stream"

payload = {
    "message": "Tell me a long story",
    "history": []
}

response = requests.post(url, json=payload, stream=True)

for line in response.iter_lines():
    if line:
        # Process streamed content as it arrives
        print(line.decode(), end='', flush=True)
```

---

## 🧪 Testing All Endpoints

**Complete Test Script (Python):**
```python
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"✓ Status: {response.status_code}")
    return response.json()

def test_upload():
    """Test document upload"""
    print("\nTesting /api/upload-documents...")
    documents = [{
        "content": "Test document content",
        "source": "Test"
    }]
    response = requests.post(
        f"{BASE_URL}/api/upload-documents",
        json={"documents": documents}
    )
    print(f"✓ Status: {response.status_code}")
    return response.json()

def test_get_documents():
    """Test document retrieval"""
    print("\nTesting /api/get-documents...")
    response = requests.get(f"{BASE_URL}/api/get-documents")
    print(f"✓ Status: {response.status_code}")
    return response.json()

def test_chat():
    """Test chat endpoint"""
    print("\nTesting /api/chat...")
    payload = {
        "message": "Hello",
        "history": []
    }
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    print(f"✓ Status: {response.status_code}")
    return response.json()

def test_delete():
    """Test document deletion"""
    print("\nTesting /api/delete-documents...")
    docs = test_get_documents()
    if docs['count'] > 0:
        doc_id = docs['documents']['ids'][0]
        response = requests.post(
            f"{BASE_URL}/api/delete-documents",
            json={"doc_ids": [doc_id]}
        )
        print(f"✓ Status: {response.status_code}")
        return response.json()
    else:
        print("⚠ No documents to delete")
        return None

# Run all tests
if __name__ == "__main__":
    print("=" * 50)
    print("Running API Tests")
    print("=" * 50)
    
    test_health()
    test_upload()
    test_get_documents()
    test_chat()
    test_delete()
    
    print("\n" + "=" * 50)
    print("✓ All tests completed!")
    print("=" * 50)
```

Run it:
```bash
python test_api.py
```

---

## 📝 Error Handling Best Practices

**Python:**
```python
import requests
from requests.exceptions import ConnectionError, Timeout

try:
    response = requests.post(
        "http://localhost:5000/api/chat",
        json={"message": "Hello", "history": []},
        timeout=10  # 10 second timeout
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(data['response'])
        else:
            print(f"API Error: {data['error']}")
    else:
        print(f"HTTP Error: {response.status_code}")
        
except ConnectionError:
    print("Error: Cannot connect to backend")
except Timeout:
    print("Error: Request timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**JavaScript:**
```javascript
fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello', history: [] })
})
.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
    }
    return response.json();
})
.then(data => {
    if (data.success) {
        console.log(data.response);
    } else {
        console.error('API Error:', data.error);
    }
})
.catch(error => {
    console.error('Request failed:', error);
});
```

---

## 🎯 Tips

1. **Always check `success` field** in responses
2. **Maintain conversation history** for context
3. **Use appropriate timeouts** for production
4. **Log all errors** for debugging
5. **Test endpoints** with tools like Postman or curl first
6. **Monitor API usage** to prevent unexpected costs
7. **Implement rate limiting** for production

---

For more information, see [README.md](./README.md) and [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)
