from db import db
from Models.users import Users
from werkzeug.security import check_password_hash, generate_password_hash

def user_creation(name, email, password):
        
        check=Users.query.filter_by(email=email).first()
        
        if check is not None:
                return 0
        

        hashed_password = generate_password_hash(password)

        user=Users(name= name , email=email, password= hashed_password )


        db.session.add(user)
        db.session.commit()

        return 1
    
        