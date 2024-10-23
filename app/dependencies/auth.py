# from models.users import Admin
# from fastapi import Depends
# from datetime import timedelta, timezone, datetime
# import jwt

# def authenticate_user(email: str, password: str, db):
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         return False
#     if not bcrypt_context.verify(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(username: str, user_id: int, expires_date: timedelta):
#     encode = {"sub": username, "id": user_id}

#     expires = datetime.now(timezone.utc) + expires_date
#     encode.update({"exp": expires})
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)