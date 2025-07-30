#!/bin/bash
# Test that everything is set up correctly

echo "🧪 Testing Urzasight setup..."

# Test backend
echo "🐍 Testing backend..."
cd backend
if [ -f app.py ]; then
    echo "✅ Backend app.py exists"
else
    echo "❌ Backend app.py missing"
fi

if [ -f requirements.txt ]; then
    echo "✅ Backend requirements.txt exists"
else
    echo "❌ Backend requirements.txt missing"
fi

# Test frontend
echo "🌐 Testing frontend..."
cd ../frontend
if [ -f index.html ]; then
    echo "✅ Frontend index.html exists"
else
    echo "❌ Frontend index.html missing"
fi

echo "📁 Project structure:"
cd ..
find . -name "*.py" -o -name "*.html" -o -name "*.md" | head -10

echo "🎉 Setup test complete!"
