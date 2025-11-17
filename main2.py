from fastapi import FastAPI, HTTPException

app = FastAPI()

dictionary_2 = {}

@app.get("/books")
def get_books():
    if not dictionary_2:
        return{"No book found!"}
    else:
        return{"books":dictionary_2}
    
@app.post("/add")
def post_books(id_book: int, book_name: str, book_author: str, book_year: int):
    if id_book in dictionary_2:
        raise HTTPException(status_code=400, detail="This book already exists!")
    else:
        dictionary_2[id_book] = {"book_name": book_name, "book_author": book_author, "book_year": book_year}

@app.put("/update/{id_book}")
def put_books(id_book: int, book_name: str, book_author: str, book_year: int):
    book_item = dictionary_2.get(id_book)

    if not book_item:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        if book_name:
            book_item["book_name"] = book_name
        if book_author: 
            book_item["book_author"] = book_author
        if book_year:
            book_item["book_year"] = book_year
        
        return {"message": "Book updated successfully!"}
    
@app.delete("/delete/{id_book}")
def delete_books(id_book: int):
    if id_book not in dictionary_2:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        del dictionary_2[id_book]
        return {"message": "Book deleted successfully!"}