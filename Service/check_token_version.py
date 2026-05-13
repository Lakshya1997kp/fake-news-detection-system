from db import db
from Models.users import Users


def check_token_version(user , version):
    if user.token_version != version:
        return 0
    return 1