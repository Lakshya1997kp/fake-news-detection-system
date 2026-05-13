from db import db
from Models.users import Users
from Service.check_token_version import check_token_version

def get_user(id, version):
    user=Users.query.filter_by(id=id).first()
    valid = check_token_version(user, version)
    if valid == 0:
        return 0
    if valid and user:
        return user
    return -1
