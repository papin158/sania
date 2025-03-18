import os
from dotenv import load_dotenv

load_dotenv()

login_admin = os.getenv("LOGIN_ADMIN")
password_admin = os.getenv("PASSWORD_ADMIN")
way_selen = os.getenv("WAY_SELEN")
max_experience: list[int] = [round(float(os.getenv("MAX_EXPERIENCE")) * 12)]
max_windows = int(os.getenv("MAX_WINDOWS"))


