# app/routes/rates.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import get_db

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.post("/")
def add_rate(data: dict, db: Session = Depends(get_db)):
    base = data.get("base_code")
    rates = data.get("rates")

    if not base or not rates:
        raise HTTPException(status_code=400, detail="Missing base_code or rates")

    for target, value in rates.items():
        db.add(models.Rate(
            base_currency=base,
            target_currency=target,
            rate=value
        ))
    db.commit()

    return {"message": f"Rates for {base} added successfully."}


@router.get("/")
def get_latest_rates(db: Session = Depends(get_db)):
    rates = db.query(models.Rate).all()
    return rates
