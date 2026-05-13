from db import db 
from Models.users import Users
from werkzeug.security import check_password_hash, generate_password_hash

def check_user(email , password):
    
     check=Users.query.filter_by(email=email).first()

     if not check:
          return 0
     
     if check_password_hash(check.password, password):
          return check
     
     return 0

def check_user_by_id(id, password):
     user =Users.query.filter_by(id=id).first()

     if not user:
          return 0
     
     if check_password_hash(user.password, password):
          return user
     
     return 0

def check_user_by_id_only(id):
     user =Users.query.filter_by(id=id).first()

     if not user:
          return 0
     return user