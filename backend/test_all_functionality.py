"""
Comprehensive test for all backend functionalities
"""
import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
SAMPLE_PDF = Path(__file__).parent.parent / "sample_pdfs" / "project-I-group01.pdf"

print("="*70)
print("COMPREHENSIVE BACKEND FUNCTIONALITY TEST")
print("="*70)

results = {}
test_count = 0

# Helper function
def test(name, func):
    global test_count
    test_count += 1
    print(f"\n[{test_count}] {name}")
    print("-" * 70)
    try:
        result = func()
        results[name] = result
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
        return result
    except Exception as e:
        results[name] = False
        print(f"[FAIL] {name} - Error: {str(e)[:100]}")
        return False

# Test 1: Health Check
def test_health():
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    if r.status_code == 200:
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        return True
    return False

# Test 2: List Files (should be empty initially)
def test_list_files_empty():
    r = requests.get(f"{BASE_URL}/api/files/", timeout=5)
    if r.status_code == 200:
        files = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Files found: {len(files)}")
        return True
    return False

# Test 3: Upload PDF
def test_upload_pdf():
    if not SAMPLE_PDF.exists():
        print(f"   [SKIP] Sample PDF not found at {SAMPLE_PDF}")
        return False
    
    with open(SAMPLE_PDF, 'rb') as f:
        files = {'file': (SAMPLE_PDF.name, f, 'application/pdf')}
        r = requests.post(f"{BASE_URL}/api/files/upload", files=files, timeout=60)
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Chunks added: {data.get('chunks_added')}")
        return True
    else:
        print(f"   Status: {r.status_code}")
        print(f"   Error: {r.text[:200]}")
        return False

# Test 4: List Files (should have the uploaded file)
def test_list_files_after_upload():
    r = requests.get(f"{BASE_URL}/api/files/", timeout=5)
    if r.status_code == 200:
        files = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Files found: {len(files)}")
        if files:
            for f in files:
                print(f"   - {f.get('filename')}: {f.get('chunk_count')} chunks")
        return len(files) > 0
    return False

# Test 5: Get File Info
def test_get_file_info():
    filename = SAMPLE_PDF.name
    r = requests.get(f"{BASE_URL}/api/files/{filename}/info", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Chunks: {data.get('chunk_count')}")
        return True
    else:
        print(f"   Status: {r.status_code}")
        return False

# Test 6: Chat without context
def test_chat_no_context():
    payload = {
        "message": "Hello, can you introduce yourself?",
        "conversation_id": "test_conv_1",
        "use_context": False
    }
    r = requests.post(f"{BASE_URL}/api/chat/", json=payload, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Response length: {len(data.get('response', ''))}")
        print(f"   Response preview: {data.get('response', '')[:100]}...")
        print(f"   Citations: {len(data.get('citations', []))}")
        return True
    else:
        print(f"   Status: {r.status_code}")
        print(f"   Error: {r.text[:200]}")
        return False

# Test 7: Chat with context (using uploaded PDF)
def test_chat_with_context():
    payload = {
        "message": "What is this document about?",
        "conversation_id": "test_conv_2",
        "use_context": True
    }
    r = requests.post(f"{BASE_URL}/api/chat/", json=payload, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Response length: {len(data.get('response', ''))}")
        print(f"   Response preview: {data.get('response', '')[:150]}...")
        citations = data.get('citations', [])
        print(f"   Citations: {len(citations)}")
        if citations:
            print(f"   Citation sources: {[c.get('source') for c in citations]}")
        return len(citations) > 0  # Should have citations when using context
    else:
        print(f"   Status: {r.status_code}")
        print(f"   Error: {r.text[:200]}")
        return False

# Test 8: Multi-turn conversation
def test_multi_turn_conversation():
    conv_id = "test_conv_3"
    
    # First message
    payload1 = {
        "message": "My name is Alice and I'm working on a project.",
        "conversation_id": conv_id,
        "use_context": False
    }
    r1 = requests.post(f"{BASE_URL}/api/chat/", json=payload1, timeout=30)
    
    if r1.status_code != 200:
        print(f"   First message failed: {r1.status_code}")
        return False
    
    # Second message (should remember the name)
    payload2 = {
        "message": "What is my name?",
        "conversation_id": conv_id,
        "use_context": False
    }
    r2 = requests.post(f"{BASE_URL}/api/chat/", json=payload2, timeout=30)
    
    if r2.status_code == 200:
        data = r2.json()
        response_text = data.get('response', '').lower()
        print(f"   Status: {r2.status_code}")
        print(f"   Response: {data.get('response', '')[:150]}...")
        if 'alice' in response_text:
            print("   [OK] Conversation memory working - name remembered!")
            return True
        else:
            print("   [WARN] Conversation memory may not be working")
            return False
    else:
        print(f"   Status: {r2.status_code}")
        return False

# Test 9: Chat with specific question about PDF content
def test_chat_pdf_content():
    payload = {
        "message": "What are the main topics discussed in the document?",
        "conversation_id": "test_conv_4",
        "use_context": True
    }
    r = requests.post(f"{BASE_URL}/api/chat/", json=payload, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Response length: {len(data.get('response', ''))}")
        print(f"   Response preview: {data.get('response', '')[:200]}...")
        citations = data.get('citations', [])
        print(f"   Citations: {len(citations)}")
        if citations:
            for i, cit in enumerate(citations[:3], 1):
                print(f"   Citation {i}: {cit.get('source')}")
        return len(citations) > 0
    else:
        print(f"   Status: {r.status_code}")
        return False

# Test 10: List Conversations
def test_list_conversations():
    r = requests.get(f"{BASE_URL}/api/chat/conversations", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Active conversations: {data.get('count')}")
        print(f"   Conversation IDs: {data.get('conversations', [])}")
        return True
    return False

# Test 11: Update PDF file
def test_update_pdf():
    if not SAMPLE_PDF.exists():
        return False
    
    with open(SAMPLE_PDF, 'rb') as f:
        files = {'file': (SAMPLE_PDF.name, f, 'application/pdf')}
        r = requests.put(f"{BASE_URL}/api/files/{SAMPLE_PDF.name}", files=files, timeout=60)
    
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Chunks: {data.get('chunks_added')}")
        return True
    else:
        print(f"   Status: {r.status_code}")
        return False

# Test 12: Delete PDF file
def test_delete_pdf():
    filename = SAMPLE_PDF.name
    r = requests.delete(f"{BASE_URL}/api/files/{filename}", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Filename: {data.get('filename')}")
        print(f"   Chunks deleted: {data.get('chunks_deleted')}")
        return True
    else:
        print(f"   Status: {r.status_code}")
        return False

# Test 13: Verify file deleted
def test_verify_file_deleted():
    r = requests.get(f"{BASE_URL}/api/files/", timeout=5)
    if r.status_code == 200:
        files = r.json()
        print(f"   Status: {r.status_code}")
        print(f"   Files remaining: {len(files)}")
        return len(files) == 0
    return False

# Run all tests
print("\nWaiting for server to be ready...")
time.sleep(2)

test("Health Check", test_health)
test("List Files (Initial - Empty)", test_list_files_empty)
test("Upload PDF File", test_upload_pdf)
test("List Files (After Upload)", test_list_files_after_upload)
test("Get File Info", test_get_file_info)
test("Chat Without Context", test_chat_no_context)
test("Chat With Context (PDF)", test_chat_with_context)
test("Multi-turn Conversation", test_multi_turn_conversation)
test("Chat About PDF Content", test_chat_pdf_content)
test("List Conversations", test_list_conversations)
test("Update PDF File", test_update_pdf)
test("Delete PDF File", test_delete_pdf)
test("Verify File Deleted", test_verify_file_deleted)

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for v in results.values() if v)
total = len(results)

for test_name, result in results.items():
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status}: {test_name}")

print(f"\nTotal: {passed}/{total} tests passed")

if passed == total:
    print("\n[SUCCESS] All backend functionalities are working correctly!")
elif passed >= total * 0.8:
    print(f"\n[WARNING] {total - passed} test(s) failed. Most functionality is working.")
else:
    print(f"\n[ERROR] {total - passed} test(s) failed. Please check the issues above.")

print("="*70)

