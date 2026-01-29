"""
Simple test script to verify the backend setup
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_chat():
    """Test chat endpoint"""
    print("\n💬 Testing chat endpoint...")
    
    payload = {
        "question": "What are the common symptoms of diabetes?",
        "use_expansion": True,
        "use_reranking": True
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse: {data['response'][:200]}...")
        print(f"Confidence: {data['confidence']}")
        print(f"Agent Path: {' -> '.join(data['agent_path'])}")
        print(f"Processing Time: {data['processing_time']:.2f}s")
        print(f"Sources: {len(data['sources'])}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200


def test_collection_info():
    """Test collection info endpoint"""
    print("\n📚 Testing collection info endpoint...")
    response = requests.get(f"{BASE_URL}/documents/collection-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Medical Assistant Backend - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Collection Info", test_collection_info),
        ("Chat", test_chat)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "✅ PASSED" if passed else "❌ FAILED"))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results.append((test_name, "❌ ERROR"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    for test_name, result in results:
        print(f"{test_name:.<40} {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
