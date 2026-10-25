import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .database import get_connection

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories = [(c["id"], c["name"]) for c in data["categories"]]
    records = [
        (r["code"], r["title"], r["category_id"], r["value"], r["status"])
        for r in data["records"]
    ]

    with closing(get_connection()) as connection:
        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (?, ?)", categories
                )
                connection.executemany(
                    "INSERT INTO records (code, title, category_id, value, status) VALUES (?, ?, ?, ?, ?)",
                    records,
                )
            print("Базу успішно заповнено!")
        except sqlite3.IntegrityError:
            print("Помилка: дані вже існують або порушують обмеження. Зміни скасовано.")


if __name__ == "__main__":
    seed_database()
