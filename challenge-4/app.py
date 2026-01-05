from flask import Flask, request, jsonify
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load flag from environment variable
FLAG = os.getenv('FLAG', 'HC{default_flag}')

@app.route("/")
def index():
    return "Public area available at /public. Admin area available at /admin, but they blocked by reverse proxy. Debug info at /debug."

@app.route("/debug")
def debug():
    debug_info = "Request Headers:\n"
    for header_name, header_value in request.headers:
        debug_info += f"{header_name}: {header_value}\n"
    debug_info += f"\nRequest Path: {request.path}\n"
    debug_info += f"Request URL: {request.url}\n"
    
    # Show X-Original-URL if present (check both case variants)
    original_url = request.headers.get("X-Original-URL") or request.headers.get("X-Original-Url")
    if original_url:
        debug_info += f"X-Original-URL: {original_url}\n"
    
    return debug_info

@app.route("/public")
def public_index():
    # Check if X-Original-URL header is present (case-insensitive)
    original_url = request.headers.get("X-Original-URL") or request.headers.get("X-Original-Url")
    
    if original_url and original_url.strip():
        # Parse the original URL to get the path
        parsed_url = urlparse(original_url)
        original_path = parsed_url.path.rstrip('/')
        
        # Route to ANY defined URL in the application via X-Original-URL
        try:
            # Create a test request context with the original path
            with app.test_request_context(original_path, headers=dict(request.headers)):
                # Try to match the original path to existing routes
                adapter = app.url_map.bind('localhost')
                endpoint, values = adapter.match(original_path, request.method)
                
                # Get the view function for this endpoint
                view_function = app.view_functions[endpoint]
                
                # Call the view function with the matched values
                if values:
                    return view_function(**values)
                else:
                    return view_function()
                    
        except Exception as e:
            # If route not found or error, return bypass message
            return f"Attempted to access '{original_path}' via X-Original-URL bypass, but route not found or error occurred."
    
    return "This is the public area."

@app.route("/admin")
def admin_index():
    return jsonify({
    "message": "Accessed via X-Original-URL header bypass.",
    "flag": FLAG
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)