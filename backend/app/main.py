from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class News(BaseModel):
    title: str
    text: str | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/news/add/")
def show_one_news(news: News):
    # TODO: получение данных от пользователя для добавления нововсти
    print(news.tile)

    return {"status": "ok"}


@app.get("/news/{news_id}/")
def show_one_news(news_id: int):
    # TODO: Запрос новости по ID в базе данных и возвращение данных пользователю

    return {"news_id": news_id}


@app.get("/news/{news_id}/change/")
def change_news(news_id):
    # TODO: Возвращение данных для редактирования новости

    news = News(title="asdasd", text="2123123")

    return {"news": news}


@app.post("/news/{news_id}/change/")
def save_news(news_id: int, news: News):
    # TODO: Сохранения изменений для новости и вывод ок если всё сохранилось
    print(news)

    return {"status": "ok"}


@app.get("/news/{news_id}/delete/")
def save_news(news_id):
    # TODO: удаление

    return {"status": "ok"}
