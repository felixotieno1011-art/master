from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.auth import create_access_token, verify_password, get_password_hash, SECRET_KEY, ALGORITHM
from app.database import SessionLocal, engine, Base
from app.models import User
from app.schemas import UserCreate # Add this to your imports at the top
from app.models import User, GameScore
from app.schemas import UserCreate, ScoreSubmit, ScoreResponse
from fastapi.staticfiles import StaticFiles

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Master API")
app.mount("/game", StaticFiles(directory="static", html=True), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
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
    
    # 🚨 Look here! We query the real database now
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running"}

@app.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User {new_user.username} created successfully"}
@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"message": f"Welcome {current_user.username}! You accessed the secret area."}

@app.post("/scores", response_model=ScoreResponse)
def submit_score(
    score_data: ScoreSubmit, 
    current_user: Annotated[User, Depends(get_current_user)], 
    db: Session = Depends(get_db)
):
    # Create a new score linked to the logged-in user
    new_score = GameScore(score=score_data.score, user_id=current_user.id)
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    
    return {"username": current_user.username, "score": new_score.score}

@app.get("/leaderboard", response_model=list[ScoreResponse])
def get_leaderboard(db: Session = Depends(get_db)):
    # Get top 10 scores, sorted highest first
    top_scores = db.query(GameScore).order_by(GameScore.score.desc()).limit(10).all()
    
    # Format the response to show the username
    return [{"username": s.owner.username, "score": s.score} for s in top_scores]
