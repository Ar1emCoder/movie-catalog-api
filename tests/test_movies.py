import pytest
import asyncio
from fastapi.testclient import TestClient

# импорты приложения и создания бд
from movies_api import app
from init_movies_db import init_db


# Создаем "работника сцены" (фикстуру)
# scope = "session" означает: запустить 1 раз перед всеми тестами
# autouse = True означает: запустить автоматически, нам не нужно вызывать его вручную
@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    asyncio.run(init_db())


# Фикстура для чистки БД между вызовами
@pytest.fixture(autouse=True)
def clean_database():
    yield
    asyncio.run(clean_db())


async def clean_db():
    from movies_db import get_db

    async for db in get_db():
        await db.execute("DELETE FROM movies")
        await db.commit()


# создаем "робота-тестировщика"
client = TestClient(app)


# Пишем тест 1!
def test_get_all_movies():
    response = client.get("/movies/")  # робот делает get-запрос по адресу /movies/
    # Проверка 1: Мы ожидаем, что сервер ответит кодом 200 (ок)
    assert response.status_code == 200  # (assert - утверждать)

    data = response.json()
    # Проверка 2: Мы ожидаем, что в ответе придет список (list), даже если он пока пустой []
    assert isinstance(data, dict)
    assert "movies" in data
    assert isinstance(data["movies"], list)

    assert "total" in data
    assert "skip" in data
    assert "limit" in data


# Пишем тест 2!
def test_get_movie_not_found():
    # Робот запрашивает фильм с заведомо несуществующим айди
    response = client.get("/movies/99999")

    # Проверка 1: Мы ожидаем код 404 (Not Found)
    assert response.status_code == 404

    # Проверка 2: Мы проверяем, что текст ошибки именно такой, как мы написали
    assert response.json()["detail"] == "Фильм не найден!"


# Тест 3!
def test_get_create_movie():
    import time

    unique_title = f"Начало_{time.time()}"

    response = client.post(
        "/movies/", json={"title": unique_title, "release_year": 2010, "rating": 8.8}
    )

    print("\nStatus: ", response.status_code)
    print("Response: ", response.json())
    print("---")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == unique_title


def test_delete_movie():
    response = client.post(
        "/movies/",
        json={"title": "Фильм на удаление", "release_year": 2024, "rating": 5.0},
    )
    movie_id = response.json()["id"]
    # удаляем фильм
    delete_response = client.delete(f"/movies/{movie_id}")

    assert delete_response.status_code == 200
    # проверяем, точно ли удалилось
    get_response = client.get(f"/movies/{movie_id}")
    assert get_response.status_code == 404
