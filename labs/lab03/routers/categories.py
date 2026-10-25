import sqlite3

from fastapi import APIRouter, HTTPException

from labs.lab03 import repository, schemas

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[schemas.CategoryRead])
def read_categories():
    return repository.get_categories()


@router.post("", response_model=schemas.CategoryRead, status_code=201)
def create_category(category: schemas.CategoryCreate):
    try:
        return repository.create_category(category.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409, detail="Категорія з такою назвою вже існує"
        )


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int):
    try:
        if not repository.delete_category(category_id):
            raise HTTPException(status_code=404, detail="Категорію не знайдено")
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409, detail="Неможливо видалити непорожню категорію"
        )
