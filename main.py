from fastapi import  Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import settings
import requests
import models
import database
from sqlalchemy.orm import Session

models.database.Base.metadata.create_all(bind=database.engine) #create database tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


google_client_id = settings.GOOGLE_CLIENT_ID
google_client_secret = settings.GOOGLE_CLIENT_SECRET
google_redirect_uri = settings.GOOGLE_REDIRECT_URI
jwt_secret_key = settings.JWT_SECRET_KEY
algorithm =settings.ALGORITHM
access_token_expire_minutes = 10

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def remove_expired_tokens(db: Session):
    current_time = datetime.datetime.utcnow()
    db.query(models.RefreshToken).filter(models.RefreshToken.expires_at < current_time).delete()
    db.commit()

@app.get("/login/google")
async def login_google():
   return RedirectResponse(f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={google_client_id}&redirect_uri={google_redirect_uri}&scope=openid%20profile%20email&access_type=offline")


@app.get("/api/auth/callback/google")
async def auth_google(code: str, db: Session = Depends(get_db)):
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
    jwt_token = create_jwt_token(data=jwt_token_data, expire_minutes=datetime.utcnow() + timedelta(minutes=access_token_expire_minutes))
     # Create JWT refresh token (new functionality)
    jwt_refresh_token = create_jwt_token(data={"sub": users["email"],"name": users["name"],
        "email": users["email"],"picture": users["picture"]}, expire_minutes=datetime.utcnow() + timedelta(minutes=1440))  # 1440 minutes = 1 day
    db.add(models.RefreshToken(token=jwt_refresh_token, user_email=users["email"], user_name=users["name"], user_img=users["picture"]))
    db.commit()

    redirect_response = RedirectResponse(url='http://localhost:3000/profile')
    redirect_response.set_cookie(key="jwt", value=jwt_token, httponly=True, secure=False)
    redirect_response.set_cookie(key="jwt_refresh", value=jwt_refresh_token, httponly=True, secure=False)
    return redirect_response

def create_jwt_token(data: dict, expire_minutes):
    to_encode = data.copy()
    to_encode.update({"exp": expire_minutes}) #Adds expire time
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


# @app.get("/api/token/refresh")
# async def refresh_token(request: Request, db: Session = Depends(get_db)):
#     remove_expired_tokens(db)
#     jwt_refresh_token = request.cookies.get('jwt_refresh')
#     if jwt_refresh_token:
#         db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == jwt_refresh_token).first()
#         if db_token and not db_token.is_blacklisted and db_token.expires_at > datetime.datetime.utcnow():
#             new_token_payload = {
#                     "sub": db_token.user_email,
#                     "name": db_token.user_name,
#                     "email":db_token.user_email,
#                     "picture":db_token.user_img,
#                     "exp": datetime.utcnow() + timedelta(minutes=1440),
#                 }
#             new_access_token = jwt.encode(new_token_payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
#             return {"access_token": new_access_token, "token_type": "bearer"}
    
#     else:
#         raise HTTPException(status_code=403, detail="Refresh token is invalid or expired")


@app.get('/logout')
async def logout(request: Request, db: Session = Depends(get_db)):
    jwt_refresh_token = request.cookies.get('jwt_refresh')
    if jwt_refresh_token:
        db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == jwt_refresh_token).first()
        if db_token:
            db_token.is_blacklisted = True
            db.commit()
        
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key='jwt', path='/')
    response.delete_cookie(key='jwt_refresh', path='/')
    return response



