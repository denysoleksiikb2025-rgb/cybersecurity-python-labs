import sqlite3

from fastapi import APIRouter, Body, HTTPException, Query

from labs.lab03 import repository, schemas

router = APIRouter(prefix="/records", tags=["Records"])

@router.get("", response_model=list[schemas.RecordRead])
def read_records(
    category_id: int | None = Query(None, gt=0),
    status: str | None = None,
    min_value: float | None = Query(None, ge=0, le=10),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return repository.get_records(category_id, status, min_value, q, limit, offset)

@router.get("/{record_id}", response_model=schemas.RecordRead)
def read_record(record_id: int):
    record = repository.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    return record

@router.post("", response_model=schemas.RecordRead, status_code=201)
def create_record(record: schemas.RecordCreate):
    try:
        return repository.create_record(record.model_dump())
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=404, detail="Категорія не існує")
        raise HTTPException(status_code=409, detail="Дублікат унікального значення")

@router.put("/{record_id}", response_model=schemas.RecordRead)
def update_record(record_id: int, record: schemas.RecordReplace):
    try:
        updated = repository.update_record(record_id, record.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Запис не знайдено")
        return updated
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=404, detail="Категорія не існує")
        raise HTTPException(status_code=409, detail="Конфлікт даних")

@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int):
    if not repository.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Запис не знайдено")

@router.post("/bulk", response_model=list[schemas.RecordRead], status_code=201)
def create_records_bulk(
    records: list[schemas.RecordCreate] = Body(..., min_length=1, max_length=100),  # noqa: B008
):
    try:
        records_data = [record.model_dump() for record in records]
        return repository.bulk_create_records(records_data)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=404, detail="Одна з категорій не існує")
        raise HTTPException(status_code=409, detail="Дублікат унікального значення")