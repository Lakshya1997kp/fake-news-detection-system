from db import db
from Service.check_user import check_user_by_id_only
from Service.check_token_version import check_token_version

def change_email_service(id , email, version):
    user = check_user_by_id_only(id)

    if not user:
        return -1
    valid = check_token_version(user, version)

    if valid:
        user.email= email
        user.token_version +=1
        db.session.commit()
        return 1
    return 0

    
