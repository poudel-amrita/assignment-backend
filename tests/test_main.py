from fastapi.testclient import TestClient
from src.main import app #import fast api app

client = TestClient(app) #test client instace for testing
  
# def test_login_google():
#     response = client.get('/login/google') #simulates client request to google login endpoint
#     assert response.status_code == 302 # redirection status  

# def test_auth_google():
#     response = client.get('/api/auth/callback/google') 
#     assert response.status_code == 200
    
def test_read_user():
    response = client.get("/api/user")
    assert response.status_code == 200