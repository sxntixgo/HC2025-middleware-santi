from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load flag from environment variable
FLAG = os.getenv('FLAG', 'HC{default_flag}')

@app.route("/")
def index():
    return "Try to access /admin to get the flag! Also check /debug for request info."

@app.route("/debug")
def debug():
    return "\n".join(f"{k}: {v}" for k, v in request.headers.items())

@app.route("/admin", methods=["GET"])
def get_admin():
    """Protected GET endpoint - requires admin authorization"""
    return jsonify({"error": "Unauthorized - admin access required."}), 403

@app.route("/admin", methods=["POST"])
def handle_post_admin():
    """Handle POST requests to admin with potential method override"""
    # Check for method override header
    override_method = request.headers.get("X-HTTP-Method-Override", "").upper()
    
    if override_method == "GET":
        # Process as GET request - vulnerable bypass!
        return get_admin_logic()
    else:
        # Regular POST - not implemented
        return jsonify({"message": "Authorized. POST to /admin not fully implemented yet. Try GET."}), 501


def get_admin_logic():
    """Actual admin GET logic - vulnerable when called via method override"""
    return jsonify({
        "message": "Admin access granted.",
        "flag": FLAG,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)