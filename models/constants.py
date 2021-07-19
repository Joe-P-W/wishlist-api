from pydantic import constr

USERNAME_MAX_LENGTH = 50
PASSWORD_MAX_LENGTH = 128
HTTP_LINK_MAX_LENGTH = 512
ITEM_NAME_MAX_LENGTH = 50

USERNAME_TYPE = constr(max_length=USERNAME_MAX_LENGTH, to_lower=True)
PASSWORD_TYPE = constr(max_length=PASSWORD_MAX_LENGTH)

ITEM_NAME_TYPE = constr(min_length=3, max_length=ITEM_NAME_MAX_LENGTH, to_lower=True)
