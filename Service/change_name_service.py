from db import db
from Service.check_user import check_user_by_id , check_user_by_id_only
from Service.check_token_version import check_token_version
def change_name_service(id , new_name, version):
    user=check_user_by_id_only(id)
    if not user:
        return -1
    valid = check_token_version(user, version)
    if valid:
        user.name=new_name
        db.session.commit()
        return 1
    return 0