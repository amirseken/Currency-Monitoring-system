from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import get_db

router = APIRouter(prefix="/differences", tags=["differences"])

@router.get("/")
def get_differences(base_currency: str, target_currency: str, db: Session = Depends(get_db)):
    # Get latest API and site rates
    api_rate = (
        db.query(models.Rate)
        .filter(models.Rate.base_currency == base_currency,
                models.Rate.target_currency == target_currency)
        .order_by(models.Rate.timestamp.desc())
        .first()
    )

    site_rate = (
        db.query(models.Difference)
        .filter(models.Difference.base_currency == base_currency,
                models.Difference.target_currency == target_currency)
        .order_by(models.Difference.timestamp.desc())
        .first()
    )

    if not api_rate or not site_rate:
        raise HTTPException(status_code=404, detail="Rates not found")

    diff_percent = abs(api_rate.rate - site_rate.rate_api) / api_rate.rate * 100

    return {
        "base_currency": base_currency,
        "target_currency": target_currency,
        "api_rate": api_rate.rate,
        "site_rate": site_rate.rate_api,
        "diff_percent": round(diff_percent, 4)
    }

    
@router.post("/")
def add_difference(data: dict, db: Session = Depends(get_db)):
    new_diff = models.Difference(
        base_currency=data["base_currency"],
        target_currency=data["target_currency"],
        rate_api=data["rate_api"],
        rate_site=data["rate_site"],
        diff_percent=data["diff_percent"],
    )
    db.add(new_diff)
    db.commit()
    return {"message": "Difference added"}
