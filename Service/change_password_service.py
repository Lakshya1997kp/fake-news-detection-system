from Service.check_user import check_user_by_id
from werkzeug.security import check_password_hash, generate_password_hash
from Service.check_token_version import check_token_version
from db import db

def change_password_service(id, password , new_password , confirm_new_password , version):
   user = check_user_by_id(id, password)
   if not user:
      return -1
   
   valid = check_token_version(user , version)

   if not valid:
      return 0
   
   if new_password==confirm_new_password:
       hashed_password=generate_password_hash(new_password)
       user.password=hashed_password
       user.token_version +=1
       db.session.commit()
       return 1