from flask import Flask, request, abort
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load flag from environment variable
FLAG = os.getenv('FLAG', 'HC{default_flag}')

@app.route("/")
def index():
    return "The flag is at /admin. You can see some debug stuff at /debug."

@app.route("/admin")
def admin():
    role = request.headers.get("X-User-Role", "")
    if role == "admin":
        return FLAG
    elif role == "":
        return "User Role Not Included", 401
    else:
        return "User Role Not Authorized", 401

@app.route("/debug")
def debug():
    return "\n".join(f"{k}: {v}" for k, v in request.headers.items())
