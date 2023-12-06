from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing_extensions import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None



while True:
    try:
        conn = psycopg2.connect(host='localhost', 
                                database='fastapi', 
                                user='postgres', 
                                password='admin', 
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB connected Sucessfull!!!")
        break
    except Exception as error:
        print("Something went wrong", error)
        time.sleep(3)


@app.get("/posts")
async def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/post", status_code=status.HTTP_201_CREATED)
async def post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post}


@app.get("/post/{id}")
async def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id:{id} was NOT FOUND")
    return {"post_detail": post}


@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with the id: {id}, was NOT FOUND")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/post/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(id: int, post: Post):
    
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING * """, 
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with the id: {id}, was NOT FOUND")
    conn.commit()
    return {'message': updated_post}