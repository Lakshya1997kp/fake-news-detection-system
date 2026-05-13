from db import db
from Models.predictions import Predictions
 
 
def save_analysis(user_id: int, text: str, result: dict) -> Predictions | None:
    try:
        record = Predictions(
            user_id    = user_id,
            text       = text,
            result     = result["label"],
            confidence = result["confidence"],
        )
        db.session.add(record)
        db.session.commit()
        return record
    except Exception as e:
        db.session.rollback()
        print(f"[save_analysis] DB error: {e}")
        return None
 