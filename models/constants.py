from pydantic import constr

USERNAME_MAX_LENGTH = 50
PASSWORD_MAX_LENGTH = 128

USERNAME_TYPE = constr(max_length=USERNAME_MAX_LENGTH, to_lower=True)
PASSWORD_TYPE = constr(max_length=PASSWORD_MAX_LENGTH)
