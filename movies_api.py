import sqlite3

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from movies_db import (
    get_db,
    add_genre,
    get_all_genres,
    add_movie,
    get_all_movies,
    add_genre_to_movie,
    delete_movie,
    get_movie_with_genres,
    update_movie,
    get_movies_by_genre,
    count_all_movies,
    count_movies_by_genre,
)

app = FastAPI(title="Каталог фильмов")


class GenreCreate(BaseModel):
    name: str


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API Каталога фильмов!"}


@app.post("/genres/")
async def create_genre(genre: GenreCreate, db=Depends(get_db)):
    try:
        result = await add_genre(db, genre.name)
        return result
    except sqlite3.IntegrityError:
        # если такой уже есть
        raise HTTPException(status_code=400, detail="Такой жанр уже существует!")


@app.get("/genres/")
async def read_genres(db=Depends(get_db)):
    result = await get_all_genres(db)
    return result


class MovieCreate(BaseModel):
    title: str
    release_year: int
    rating: float


@app.post("/movies/")
async def create_movie(movie: MovieCreate, db=Depends(get_db)):
    try:
        result = await add_movie(db, movie.title, movie.release_year, movie.rating)
        return result
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Такой фильм уже существует")


@app.get("/movies/")
async def read_movies(
    skip: int = 0, limit: int = 100, genre: str = None, db=Depends(get_db)
):
    if genre:
        result = await get_movies_by_genre(db, genre, skip, limit)
        total = await count_movies_by_genre(db, genre)
    else:
        result = await get_all_movies(db, skip, limit)
        total = await count_all_movies(db)
    return {"total": total, "skip": skip, "limit": limit, "movies": result}


@app.get("/movies/{movie_id}")
async def get_movie(movie_id: int, db=Depends(get_db)):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="ID должен быть положительным")
    qwery = "SELECT * FROM movies WHERE id = ?"
    cursor = await db.execute(qwery, (movie_id,))
    movie = await cursor.fetchone()

    if movie is None:
        raise HTTPException(status_code=404, detail="Фильм не найден!")
    return movie


@app.post("/movies/{movie_id}/genres/{genre_id}")
async def link_genre_to_movie(movie_id: int, genre_id: int, db=Depends(get_db)):
    try:
        await add_genre_to_movie(db, movie_id, genre_id)
        return {"message": f"Жанр {genre_id} добавлен к фильму {movie_id}"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=404, detail="Фильм или жанр не найден!")


@app.delete("/movies/{movie_id}")
async def delete_movies_endpoint(movie_id: int, db=Depends(get_db)):
    is_delete = await delete_movie(db, movie_id)
    if not is_delete:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return {"message": "Фильм успешно удален"}


@app.get("/movies/{movie_id}")
async def get_movies_details(movie_id: int, db=Depends(get_db)):
    movie = await get_movie_with_genres(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Фильм не найден!")
    return movie


class MovieUpdate(BaseModel):
    title: str
    release_year: int
    rating: float


@app.put("/movies/{movie_id}")
async def update_movie_endpoint(movie_id: int, movie: MovieUpdate, db=Depends(get_db)):
    is_updated = await update_movie(
        db, movie_id, movie.title, movie.release_year, movie.rating
    )
    if not is_updated:
        raise HTTPException(status_code=404, detail="Фильм не найден!")

    return {"message": "Фильм успешно обновлён"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
