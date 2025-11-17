#O codigo ta em ingles, caso isso seja ruim pra correção de tarefas porfavor avisa na correção
#alem disso eu posso misturar ingles e português de vez em quando, caso isso aconteça porfavor me avisa, acho que é um custume ruim da minha parte


#gostaria de algumas dicas de como otimizar meu codigo e como estudar ai9nda mais fora da ebac, se puder responder esse comentario eu agrade;o!
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

dictionary_2 = {}

#Constructor(eu acho)
class Book(BaseModel):
    book_name: str
    book_author: str 
    book_year: int


#método nao muda 
@app.get("/books")
def get_books():
    if not dictionary_2:
        return{"No book found!"}
    else:
        return{"books":dictionary_2}
    
#modificado (palavra chave nao é mais .dict() e sim  .model_dump(), o pydantic atualizou em 23 de junho de 2023 e  essaa palavra chave foi atulizada :p)
@app.post("/add")
def post_books(id_book: int, book:Book):
    if id_book in dictionary_2:
        raise HTTPException(status_code=400, detail="This book already exists!")
    else:
        dictionary_2[id_book] = book.model_dump()
#mesma coisa aq
@app.put("/update/{id_book}")
def put_books(id_book: int, book:Book):
    book_item = dictionary_2.get(id_book)

    if not book_item:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        book_item[id_book] = book.model_dump()
        
        return {"message": "Book updated successfully!"}
#mexendo com id
@app.delete("/delete/{id_book}")
def delete_books(id_book: int):
    if id_book not in dictionary_2:
        raise HTTPException(status_code=404, detail="Book not found!")
    else:
        del dictionary_2[id_book]
        return {"message": "Book deleted successfully!"}