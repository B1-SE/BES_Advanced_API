#!/bin/bash
echo "Starting application..."
gunicorn "wsgi:app"