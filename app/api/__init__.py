# app/api/__init__.py

from . import chatbot_routes, lead_detection_routes
# Do not import oauth here to avoid circular dependency
