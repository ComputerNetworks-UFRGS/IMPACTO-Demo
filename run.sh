#!/bin/bash

echo "### GT-IMPACTO Setup Script ###"
echo "Required: Python 3.11.x"

# Function to check if files have default passwords
check_default_passwords() {
    if grep -q "sua_senha_segura" .env || \
       grep -q "sua_senha_segura" postgres_setup.sql || \
       grep -q "sua_senha_segura" reset_db.sql; then
        return 0
    fi
    return 1
}

# Copy example files if they don't exist
if [ ! -f ".env" ] || [ ! -f "postgres_setup.sql" ] || [ ! -f "reset_db.sql" ]; then
    echo "Criando arquivos de configuração..."
    cp -n .env.example .env
    cp -n postgres_setup_example.sql postgres_setup.sql
    cp -n reset_db_example.sql reset_db.sql
    
    echo -e "\nPor favor, modifique os seguintes arquivos com sua senha:"
    echo "1. .env:"
    echo "   - DB_PASSWORD=sua_senha_segura"
    echo "   - ADMIN_PASSWORD=sua_senha_segura"
    echo "2. postgres_setup.sql:"
    echo "   - CREATE USER gt_impacto WITH PASSWORD 'sua_senha_segura'"
    echo "3. reset_db.sql:"
    echo "   - CREATE USER gt_impacto WITH PASSWORD 'sua_senha_segura'"
    echo -e "\nDepois de modificar os arquivos, execute este script novamente.\n"
    exit 0
fi

# Check if passwords were changed
if check_default_passwords; then
    echo "Erro: Por favor, modifique as senhas nos arquivos de configuração primeiro."
    exit 1
fi

# Check Python version
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 not found. Installing..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv
fi

python_version=$(python3.11 -V 2>&1 | grep -Po '(?<=Python )([0-9]+.[0-9]+)')
if [[ "$python_version" != "3.11" ]]; then
    echo "Error: Python 3.11.x is required"
    exit 1
fi

# Create and activate venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate || {
    echo "Error: Failed to activate virtual environment"
    exit 1
}

# Install requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Database setup
echo "Setting up database..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Configure PostgreSQL
echo "Configuring PostgreSQL..."
sudo -u postgres psql -f postgres_setup.sql
sudo -u postgres psql -f reset_db.sql

# Django setup
echo "Running Django migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages

# Static files setup
echo "Setting up static files..."
rm -rf staticfiles/
mkdir -p staticfiles
chmod 755 staticfiles
python manage.py collectstatic --noinput --clear

# Data population
echo "Populating data..."
python manage.py clear_db
python ./data_populator/delete_sectors_and_reports.py
python ./data_populator/import_reports.py
python ./data_populator/import_cyber_security_data.py
python manage.py populate_db

# Start API and server
echo "Starting services..."
nohup python api/api.py &
PORT=${1:-8000}
python manage.py runserver $PORT

echo "Setup complete! Access the admin interface at http://localhost:$PORT/admin"