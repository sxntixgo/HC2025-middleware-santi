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
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip.strip() == "127.0.0.1":
        return FLAG
    return "Access Denied: Your IP is not allowed. Only local hosts are allowed.", 403

@app.route("/debug")
def debug():
    return "\n".join(f"{k}: {v}" for k, v in request.headers.items())
