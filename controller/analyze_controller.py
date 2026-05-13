from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from Service.check_user import check_user_by_id_only
from Service.check_token_version import check_token_version
from flask_jwt_extended import get_jwt_identity
from Service.get_history import get_history
from Service.save_analysis import save_analysis
from Service.analyze_service import analyze_text, ML_WEIGHT, WIKIPEDIA_WEIGHT, FACTCHECK_WEIGHT, KB_WEIGHT

analyze_bp = Blueprint("analyze", __name__)

def error(message, status=400):
    return ({"message": message, "status": status})

def success(message, status=200):
    return ({"message": message, "status": status})


@analyze_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    user_id = int(get_jwt_identity())
    claims  = get_jwt()
    version = claims.get("ver")

    user = check_user_by_id_only(user_id)
    if not user:
        return error("user not found")
    if not check_token_version(user, version):
        return error("Session expired", 401)

    data = request.get_json(silent=True)
    if not data:
        return error("Request body must be JSON")

    text = data.get("text", "").strip()
    if not text:
        return error("'text' field is required and cannot be empty")
    if len(text) < 20:
        return error("Text is too short to analyze (minimum 20 characters)")
    if len(text) > 10_000:
        return error("Text is too long (maximum 10,000 characters)")

    result = analyze_text(text)

    record = save_analysis(user_id, text, result)

    response = {
        "saved": record is not None,
        "result": {
            "id":         record.id if record else None,
            "label":      result["label"],
            "confidence": result["confidence"],
            "created_at": record.Time.isoformat() if record and record.Time else None,
            "breakdown": {
                "ml_model": {
                    "label":  result["ml_model"]["label"],
                    "score":  result["ml_model"]["score"],
                    "weight": ML_WEIGHT,
                },
                "wikipedia": {
                    "found":     result["wikipedia"]["found"],
                    "matched":   result["wikipedia"]["matched"],
                    "summary":   result["wikipedia"]["summary"],
                    "credible":  result["wikipedia"]["credible"],
                    "fake_prob": result["wikipedia"]["fake_prob"],
                    "weight":    WIKIPEDIA_WEIGHT,
                },
                "fact_check": {
                    "found":  result["fact_check"]["found"],
                    "label":  result["fact_check"]["label"],
                    "source": result["fact_check"]["source"],
                    "weight": FACTCHECK_WEIGHT,
                },
                "knowledge_base": {
                    "found":   result["knowledge_base"]["found"],
                    "subject": result["knowledge_base"]["subject"],
                    "claimed": result["knowledge_base"]["claimed"],
                    "actual":  result["knowledge_base"]["actual"],
                    "match":   result["knowledge_base"]["match"],
                    "weight":  KB_WEIGHT,
                },
            },
        },
    }

    if not record:
        response["warning"] = "Result could not be saved to history"

    return success(response)


@analyze_bp.route("/analyze/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    claims  = get_jwt()
    version = claims.get("ver")

    user = check_user_by_id_only(user_id)
    if not user:
        return error("user not found")
    if not check_token_version(user, version):
        return error("Session expired", 401)

    try:
        limit  = int(request.args.get("limit",  20))
        offset = int(request.args.get("offset",  0))
        limit  = max(1, min(limit, 100))
        offset = max(0, offset)
    except ValueError:
        return error("'limit' and 'offset' must be integers")

    records = get_history(user_id, limit=limit, offset=offset)

    return success({
        "count":   len(records),
        "limit":   limit,
        "offset":  offset,
        "history": records,
    })