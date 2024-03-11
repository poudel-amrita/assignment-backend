from fastapi import  FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
algorithm = os.getenv('ALGORITHM')
access_token_expire_minutes = 10

@app.get("/login/google")
async def login_google():
   return RedirectResponse(f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={google_client_id}&redirect_uri={google_redirect_uri}&scope=openid%20profile%20email&access_type=offline")


@app.get("/api/auth/callback/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": google_redirect_uri,
        "grant_type": "authorization_code",
    }
    responseData = requests.post(token_url, data=data)
    access_token = responseData.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    users = user_info.json()
    jwt_token_data = {"sub": users["email"],
        "name": users["name"],
        "email": users["email"],
        "picture": users["picture"]} 
    jwt_token = create_jwt_token(data=jwt_token_data)
    redirect_response = RedirectResponse(url='http://localhost:3000/profile')
    redirect_response.set_cookie(key="jwt", value=jwt_token, httponly=True, secure=False)
    return redirect_response

def create_jwt_token(data: dict):
    expire_time = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    to_encode = data.copy()
    to_encode.update({"exp": expire_time}) #Adds expire time
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=algorithm)
    return encoded_jwt

@app.get("/api/user")
async def read_user(request: Request):
    jwt_token = request.cookies.get('jwt')
    if(jwt_token):
        try:
            payload = jwt.decode(jwt_token, jwt_secret_key, algorithms=[algorithm])
            user_data = {
                "name": payload.get("name"),
                "email": payload.get("email"),
                "picture": payload.get("picture")
            }
            return user_data
        except JWTError as e:
            print(f"JWT decode error: {e}")
            raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get('/logout')
async def logout():
    redirect_response = RedirectResponse(url='http://localhost:3000/')
    redirect_response.delete_cookie(key='jwt', path=redirect_response)
    return redirect_response



