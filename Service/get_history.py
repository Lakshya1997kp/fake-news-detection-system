from Models.predictions import Predictions
 
 
def get_history(user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    records = (
        Predictions.query
        .filter_by(user_id=user_id)
        .order_by(Predictions.Time.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return [
        {
            "id":           r.id,
            "result":       r.result,
            "confidence":   round(r.confidence, 4) if r.confidence else None,
            "text_preview": r.text[:120] + ("..." if len(r.text) > 120 else ""),
            "created_at":   r.Time.isoformat() if r.Time else None,
        }
        for r in records
    ]
 