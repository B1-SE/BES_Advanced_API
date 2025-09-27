#!/bin/bash
echo "Starting application..."
gunicorn "flask_app:app"