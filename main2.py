#Imports
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic import BaseModel
from typing import Optional
import secrets 

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base   
from sqlalchemy.orm import sessionmaker, Session

user_admin = "admin"
password_admin = "admin"

DATABASE_URL = "sqlite:///./books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

security = HTTPBasic()
app = FastAPI()
dictionary_2 = {}


#Constructor
class Book(BaseModel):
    book_name: str
    book_author: str 
    book_year: int

class Book_Patch(BaseModel):
    book_name: Optional[str] = None
    book_author: Optional[str] = None
    book_year: Optional[int] = None

class BookDB(Base):
    __tablename__ = "Book_Table"

    id = Column(Integer, primary_key = True, index=True) 
    book_name = Column(String, index = True) 
    book_author = Column(String, index = True)
    book_year = Column(Integer) 

Base.metadata.create_all(bind = engine)    

def get_session_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def user_authentication(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, user_admin)
    is_password_correct = secrets.compare_digest(credentials.password, password_admin)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="username or password incorrect.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials

@app.get("/books")
def get_books(page:int = 1, limit: int = 10, db: Session = Depends(get_session_db) ,credentials: HTTPBasicCredentials = Depends(user_authentication)):
    
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid command.")
    
    books = db.query(BookDB).offset((page -1)* limit).limit(limit).all()

    if not books:
        return{"No book found!"}
    
    book_total = db.query(BookDB).count()

    return{
        "page": page,
        "limit": limit,
        "total": len(dictionary_2),
        "books": [{"id": book.id, "book_name": book.book_name, "book_author": book.book_author, "book_year": book.book_year} for book in books]
    }
#Usar .model_dump() ao invés de .dict()
@app.post("/add")
def post_books(book:Book, db: Session = Depends(get_session_db) ,credentials: HTTPBasicCredentials = Depends(user_authentication)):
    db_book = db.query(BookDB).filter(BookDB.book_name == book.book_name, book.book_author == book.book_author).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists!")
    else: 
        new_book = BookDB(
            book_name=book.book_name,
            book_author=book.book_author,
            book_year=book.book_year
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        return {"message": "Book added successfully!", "book_id": new_book.id}


@app.put("/update/{id_book}")
def put_books(id_book: int, book:Book,db: Session = Depends(get_session_db) ,credentials: HTTPBasicCredentials = Depends(user_authentication)):
   db_book = db.query(BookDB).filter(BookDB.id == id_book).first()
   if not db_book:
        raise HTTPException(status_code=404, detail="Book not found!")
   else:
       db_book.book_name = book.book_name  
       db_book.book_author = book.book_author
       db_book.book_year = book.book_year
       db.commit()
       db.refresh(db_book)
    
@app.patch("/edit/{id_book}")
def patch_books(
    id_book: int,
    data: Book_Patch,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(user_authentication)
):

    db_book = db.query(BookDB).filter(BookDB.id == id_book).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found!")
    update_data = data.model_dump(exclude_unset=True)

    for f, v in update_data.items():
        setattr(db_book, f, v)
    
    
    db.commit()
    db.refresh(db_book)

@app.delete("/delete/{id_book}")
def delete_books(id_book: int, db: Session = Depends(get_session_db) ,credentials: HTTPBasicCredentials = Depends(user_authentication)):
    db_book = db.query(BookDB).filter(BookDB.id == id_book).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        db.delete(db_book)
        db.commit()
        db.refresh(db_book)