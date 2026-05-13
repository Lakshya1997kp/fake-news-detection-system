from db import db
from Models.users import Users
from Service.check_token_version import check_token_version

def delete_user(id, version):
    user = Users.query.get(id)

    if not user:
        return -1

    if not check_token_version(user, version):
        return 0

    db.session.delete(user)
    db.session.commit()
    return 1
