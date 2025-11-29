SECRET_KEY = "a_secure_random_flask_secret"
USERNAME = "liujifu"

# bcrypt hash; HINT: OLD SCHOOL'S MEMORY
PASSWORD_HASH = "$2b$12$uaWd6GtCFgYjMbQqEawY6uX7ZyryfqhE/hsVHZBrZjN1UN/R3WMJ6"


# GENERATE THE PASSWORD USING:
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt()
# print(bcrypt.generate_password_hash("the pass word").decode())
