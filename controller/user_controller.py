from flask import jsonify, Blueprint, request
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask_jwt_extended import jwt_required
from Service.get_user import get_user
from Service.delete_user import delete_user
from Service.check_user import check_user, check_user_by_id,check_password_hash
from Service.change_password_service import change_password_service
from Service.change_name_service import change_name_service
from Service.check_token_version import check_token_version

user_bp=Blueprint("user",  __name__)





def error(message, status=400, ):
      return({"message":message, "status":status, })

def success(message, status=200):
      return ({"message":message,"status":status, })





@user_bp.route("/users/profile", methods=['GET'])
@jwt_required()
def profile():
    userid=get_jwt_identity()
    claims=get_jwt()
    version=claims.get("ver")


    user=get_user(int(userid), version)
    if user==-1:
        return error("User not found")
    if user == 0:
        return error("session expired ", 401)
    return ({"id": user.id, "email": user.email, "name": user.name}),200



@user_bp.route("/users/profile", methods=['PUT'])
@jwt_required()
def change_email():
    userid=get_jwt_identity()
    claims=get_jwt()
    version= claims.get("ver")

    data= request.get_json()
    email=data.get("new_email")
    result = change_email_service(int(userid), email, version)

    if result==-1:
        return error("user not found")
    if result==0:
        return error("session was expired", 401)
    return success("email chnaged successfully")



@user_bp.route("/users/profile/change_name", methods=['PUT'])
@jwt_required()
def change_name():
    userid=get_jwt_identity()
    claims=get_jwt()
    version=claims.get("ver")


    data= request.get_json()
    name= data.get("new_name")
    result = change_name_service(int(userid), name, version)
    if result==1:
        return success("Name chnaged succesful")
    if result==0:
        return error("session was expired", 401)
    return error("user not found")




@user_bp.route("/users/profile/change_password", methods=["PUT"])
@jwt_required()
def change_password():
    userid=get_jwt_identity()
    claims=get_jwt()
    version=claims.get("ver")


    data= request.get_json()
    old_password =data.get("old_password")
    new_password = data.get("new_password")
    confirm_new_password= data.get("confirm_new_password")

    change = change_password_service(int(userid), old_password, new_password, confirm_new_password, version)
    if change==-1:
        return error("user not found")
    if change==0:
        return error ("session was expired ", 401)
    return success("Password successfully changed")


@user_bp.route("/users/profile/Delete", methods=['DELETE'])
@jwt_required()
def delete_profile():
    userid=get_jwt_identity()
    claims=get_jwt()
    version=claims.get("ver")
   
    user=delete_user(int(userid), version)
    
    if user==1:
        return success("User successfully deleted")
    if user==-1:
        return error("User not found")
    if user==0:
        return error("User session is expired")