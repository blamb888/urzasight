#!/bin/bash
# Quick backend setup script

cd "$(dirname "$0")/../backend"

echo "🐍 Setting up Urzasight backend..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📝 Created .env file - please edit with your API keys"
else
    echo "📝 .env file already exists"
fi

echo "✅ Backend setup complete!"
echo "🔧 Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: cd backend && source venv/bin/activate && python app.py"
