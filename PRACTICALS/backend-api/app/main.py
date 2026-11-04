from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from app.auth import create_access_token, verify_password, get_password_hash, SECRET_KEY, ALGORITHM

app = FastAPI(title="Master API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_user_db = {
    "felix": {
        "username": "felix",
        "hashed_password": get_password_hash("secret123")
    }
}

# 🚨 NEW: This is the real bouncer
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_user_db.get(username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running"}

@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# 🚨 NEW: /protected now uses the real bouncer
@app.get("/protected")
def protected_route(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"message": f"Welcome {current_user['username']}! You accessed the secret area."}
