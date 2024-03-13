from fastapi.testclient import TestClient
from src.main import app #import fast api app

client = TestClient(app) #test client instace for testing
  
def test_login_google():
    response = client.get('/login/google') #simulates client request to google login endpoint
    assert response.status_code == 302 # redirection status
    

