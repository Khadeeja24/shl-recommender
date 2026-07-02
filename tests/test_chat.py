import requests

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Health check passed")

def test_clarify():
    """Agent should ask clarifying question for vague query"""
    response = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "I need an assessment"}
        ]
    })
    data = response.json()
    assert data["recommendations"] == []
    assert data["end_of_conversation"] == False
    assert len(data["reply"]) > 0
    print("✅ Clarify test passed")
    print(f"   Agent asked: {data['reply']}")

def test_recommend():
    """Agent should recommend assessments for clear query"""
    response = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "I am hiring a mid level Java developer"},
            {"role": "assistant", "content": "What specific Java skills are you looking for?"},
            {"role": "user", "content": "Spring Boot and microservices experience"}
        ]
    })
    data = response.json()
    assert len(data["recommendations"]) > 0
    assert len(data["recommendations"]) <= 10
    for rec in data["recommendations"]:
        assert "name" in rec
        assert "url" in rec
        assert "shl.com" in rec["url"]
    print(f"✅ Recommend test passed — {len(data['recommendations'])} assessments returned")

def test_refuse_offtopic():
    """Agent should refuse off-topic questions"""
    response = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ]
    })
    data = response.json()
    assert data["recommendations"] == []
    print("✅ Refuse off-topic test passed")
    print(f"   Agent said: {data['reply']}")

def test_compare():
    """Agent should compare two assessments"""
    response = requests.post(f"{BASE_URL}/chat", json={
        "messages": [
            {"role": "user", "content": "What is the difference between OPQ32r and Verify G+?"}
        ]
    })
    data = response.json()
    assert len(data["reply"]) > 0
    print("✅ Compare test passed")
    print(f"   Agent said: {data['reply'][:100]}...")

if __name__ == "__main__":
    print("Running SHL Agent Tests...\n")
    test_health()
    test_clarify()
    test_recommend()
    test_refuse_offtopic()
    test_compare()
    print("\n✅ All tests passed!")