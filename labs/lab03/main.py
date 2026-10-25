from fastapi import FastAPI

from labs.lab03.routers import categories

# from labs.lab03.routers import records # розкоментуємо пізніше

app = FastAPI(
    title="Реєстр вразливостей мережевих сервісів",
    description="Сервіс обліку результатів навчальної перевірки мережевих сервісів. Одиниця вимірювання - score (оцінка небезпеки).",
)

app.include_router(categories.router)


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/student")
def get_student():
    return {
        "student_name": "Олексій Денис Олегович",
        "group_name": "КБ-104",
        "variant_number": 2,
    }
