# 🚀 Urzasight Quick Start Guide

Get your manga reading assistant up and running in 5 minutes!

## 🎯 Instant Testing (No Setup Required)

1. **Open the frontend**: `firefox frontend/index.html` (or any browser)
2. **Select "Mock OCR"** and **"Mock Translation"** 
3. **Upload any manga image** and click "Analyze Manga Text"
4. **See the results!** Sample translation and analysis will appear

## 🔧 Full Setup (With Real APIs)

### Step 1: Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Get API Keys
- **Google Cloud Vision**: [Get API Key](https://console.cloud.google.com/)
- **Claude API**: [Get API Key](https://console.anthropic.com/)

### Step 3: Configure Environment
```bash
cd backend
cp .env.template .env
# Edit .env with your API keys using nano or vim
nano .env
```

### Step 4: Start Backend
```bash
python app.py
```

### Step 5: Test with Real APIs
1. Open `frontend/index.html`
2. Enter your API keys in the configuration section
3. Select "Google Cloud Vision" and "Claude API"
4. Upload your manga and analyze!

## 📱 Testing Tips

### Best Manga Images
- **Clear, well-lit photos**
- **Single panels** work better than full pages
- **Standard dialogue bubbles** (avoid handwritten text initially)

### Troubleshooting
- **CORS errors**: Make sure backend is running on `localhost:5000`
- **No text detected**: Try a clearer image or different manga page
- **API errors**: Check your API keys and internet connection

## 🎌 Your First Translation

Try uploading a manga page and see Urzasight:
- Extract the Japanese text
- Provide natural English translation
- Explain grammar patterns for learning
- Give cultural context about the dialogue

Ready to read manga like never before! 📚✨
