from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os
from database.models import User, YourData
from database.data import SessionLocal
from auth.jwt_handler import signJWT,decodeJWT
from auth.jwt_bearer import jwtBearer
import io
import csv
from sqlalchemy import func
import pandas as pd


app = FastAPI()

class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    
class log_in(BaseModel):
    email:str
    password:str


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_valid_csv(file: UploadFile):
    content = file.file.read().decode('utf-8')
    csv_file = io.StringIO(content)
    try:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Read the first row as headers
        if len(headers) < 2:  # Ensure there are at least two columns
            return False
        for row in csv_reader:
            if len(row) != len(headers):
                return False
        return True
    except csv.Error:
        return False
    finally:
        file.file.seek(0)  # Reset file pointer to the beginning     
        



@app.post("/signup")
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    # 1. Check if username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash the password
   
    
    # 3. Insert the user into the database
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 4. Return a success message
    return signJWT(user.email)

@app.post("/login")
async def login(data: log_in, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.password_hash != data.password:
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return signJWT(data.email)


@app.post("/upload-csv/")
async def upload_csv(token: str = Depends(jwtBearer()),file: UploadFile = File(...), db: Session = Depends(get_db)):
    payload = decodeJWT(token)
    
    # Extract the email from the payload
    email = payload.get("userID")
    user = db.query(User).filter(User.email == email).first()
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    if not is_valid_csv(file):
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    
    highest_doc_id = db.query(func.max(YourData.document_id)).filter(YourData.email == email).scalar()
    
    # If highest_doc_id is None, it means this is the first document for this email
    new_doc_id = (highest_doc_id or 0) + 1
    folder_path=f'{email}/{new_doc_id}'
    if not os.path.exists(folder_path):
    # Create the folder
        os.makedirs(folder_path)
    
    file_location = os.path.join(folder_path,file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
        
    new_data = YourData(
        id=user.id,
        username=user.username,
        email=user.email,
        document_id=new_doc_id,
        path=file_location
    )
    
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    
    return JSONResponse(content={
        "message": f"CSV file '{file.filename}' uploaded successfully",
        "document_id": new_data.document_id
    }, status_code=200)
    
    
@app.get("/document-stats/")
async def get_document_stats( document_id: int, db: Session = Depends(get_db),token: str = Depends(jwtBearer())):
    # Find the document in the database
    payload = decodeJWT(token)
    email = payload.get("userID")
    document = db.query(YourData).filter(YourData.email == email, YourData.document_id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if the file exists
    if not os.path.exists(document.path):
        raise HTTPException(status_code=404, detail="CSV file not found on server")
    
    # Read the CSV file
    df = pd.read_csv(document.path)
    
    # Calculate statistics for each column
    stats = {}
    for column in df.columns:
        column_stats = {}
        if pd.api.types.is_numeric_dtype(df[column]):
            column_stats['mean'] = df[column].mean()
            column_stats['median'] = df[column].median()
        # elif pd.api.types.is_string_dtype(df[column]):
        #     column_stats['mode'] = df[column].mode().tolist()
        else:
            column_stats['type'] = 'unsupported'
        
        stats[column] = column_stats
    
    return JSONResponse(content={
        "message": "Statistics calculated successfully",
        "filename": os.path.basename(document.path),
        "stats": stats
    }, status_code=200)
    
    
