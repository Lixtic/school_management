import multiprocessing
import os

# Bind to Railway's PORT
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration
workers = 2  # Keep it low for Railway's resources
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased timeout
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "school_management"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for better performance
preload_app = False  # Set to False to avoid issues with DB connections