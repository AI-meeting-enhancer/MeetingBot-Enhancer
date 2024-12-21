from passlib.context import CryptContext
from dotenv import load_dotenv
import os
load_dotenv()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv('SECRET_KEY', 'b52489b12239f4d8c04e4ee37e3d9342d78dcd66c9f0829d081da30c679735d9')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

