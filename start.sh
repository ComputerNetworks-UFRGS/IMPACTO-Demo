#!/bin/bash

echo "### GT-IMPACTO Start Script ###"

# Get port from command line argument or use default 8000
PORT=${1:-8000}

# 1. Activate virtual environment
source .venv/bin/activate || {
    echo "Error: Failed to activate virtual environment"
    exit 1
}

# 2. Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# 3. Compile translations
echo "Compiling translations..."
python manage.py compilemessages

# 4. Start services
echo "Starting services..."
nohup python api/api.py &
python manage.py runserver $PORT
