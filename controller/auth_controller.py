
from flask import jsonify, Blueprint , request
from werkzeug.security import generate_password_hash , check_password_hash
from Service.user_creation import user_creation
from Service.check_user import check_user
from flask_jwt_extended import create_access_token

auth_bp=Blueprint("auth", __name__)


def error(message, status=400, ):
      return({"message":message, "status":status, })

def success(message, status=200):
      return ({"message":message,"status":status, })






@auth_bp.route("/auth/signup", methods=['POST'])
def signup():
        data=request.get_json()
        if not data:
              return error("data must be  in json")
        
        name = data.get("name")
        email = data.get("email")

        if not name or not email:
              return error("name and email must be filled")
        
        password=data.get("password")
        confirm_password=data.get("confirm_password")


        if len(password)<=5:
              return error("password length must be greater than 5")
        
        if not confirm_password:
              return error(" confirm password must be filled ")

        if password!=confirm_password:
              return error("password and confirm password must be matched")


       

        status= user_creation(name, email, password)

        if status==0:
              return error("user already exists!")
        
        return success("User created ")








@auth_bp.route("/auth/login" , methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password :
        return error(" email and password must be filled")
        

    user=check_user(email, password)

    if user: 
      access_token= create_access_token(identity=str(user.id),
                                          additional_claims={
                                                "ver" :user.token_version
                                            } )
      return ({"message": "user successfully logged in " ,"status":200, "token": access_token })
    

    return error("email or password did not matched")
    