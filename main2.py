#Imports
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import os
import secrets 

user_admin = "admin"
password_admin = "admin"

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
def get_books(credentials: HTTPBasicCredentials = Depends(user_authentication)):
    if not dictionary_2:
        return{"No book found!"}
    else:
        return{"books":dictionary_2}
    
#Usar .model_dump() ao invés de .dict()
@app.post("/add")
def post_books(id_book: int, book:Book, credentials: HTTPBasicCredentials = Depends(user_authentication)):
    if id_book in dictionary_2:
        raise HTTPException(status_code=400, detail="This book already exists!")
    else:
        dictionary_2[id_book] = book.model_dump()


@app.put("/update/{id_book}")
def put_books(id_book: int, book:Book, credentials: HTTPBasicCredentials = Depends(user_authentication)):
    book_item = dictionary_2.get(id_book)

    if not book_item:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        dictionary_2[id_book] = book.model_dump()
        return {"message": "Book updated successfully!"}
    
@app.patch("/edit/{id_book}")
def patch_books(id_book: int, data:Book_Patch, credentials: HTTPBasicCredentials = Depends(user_authentication)):
    book_item = dictionary_2.get(id_book)
    if not book_item:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            book_item[k] = v

@app.delete("/delete/{id_book}")
def delete_books(id_book: int, credentials: HTTPBasicCredentials = Depends(user_authentication)):
    if id_book not in dictionary_2:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        del dictionary_2[id_book]
        return {"message": "Book deleted successfully!"} 