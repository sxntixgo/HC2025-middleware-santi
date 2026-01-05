from flask import Flask, request, abort
import ssl
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load flag from environment variable
FLAG = os.getenv('FLAG', 'HC{default_flag}')

# Load expected hostname from environment variable
EXPECTED_HOSTNAME = os.getenv('EXPECTED_HOST', 'localhost')

@app.route("/")
def index():
    return "The flag is at /admin. You can see some debug stuff at /debug."

@app.route("/debug")
def debug():
    debug_info = "Request Headers:\n"
    for header_name, header_value in request.headers:
        debug_info += f"{header_name}: {header_value}\n"
    return debug_info

@app.route("/admin")
def admin():
    # Get Host header - when duplicate headers are sent, Flask receives them comma-separated
    host_header = request.headers.get("Host", "")
    
    # Check for multiple Host header values
    if "," in host_header:
        host_values = [h.strip() for h in host_header.split(",")]
        
        # Return error if more than 2 Host headers are used
        if len(host_values) > 2:
            return "Error: Too many Host headers detected. Maximum of 2 allowed.", 400
        
        # The challenge: need exactly 2 comma-separated Host values
        # First one must match expected hostname (SNI), second one must be "admin.local"
        if len(host_values) == 2:
            first_host = host_values[0].strip()
            second_host = host_values[1].strip()
            
            if first_host != EXPECTED_HOSTNAME:
                return f"Invalid hostname. Server name indication (SNI) mismatch.", 421
            elif second_host == "admin.local":
                return FLAG
    else:
        # Single Host header case - check for Host/SNI mismatch
        if host_header.strip() and host_header.strip() != EXPECTED_HOSTNAME:
            return "Invalid hostname. Server name indication (SNI) mismatch.", 421

    return "HTTP request domain verification failed. Expected: admin.local", 403

if __name__ == '__main__':
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('/app/cert.pem', '/app/key.pem')
    
    # Run Flask app with HTTPS
    app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False)
