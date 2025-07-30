# 🎌 Urzasight - Live Manga Reading Assistant

An AI-powered assistant to help users read physical Japanese manga in real time, starting with an MVP that runs on mobile devices and evolving toward a hands-free wearable experience.

## ✨ Features

- **OCR Text Extraction** - Extract Japanese text from manga panels using Google Cloud Vision
- **AI Translation** - Natural English translations with cultural context
- **Grammar Analysis** - Detailed breakdown for Japanese language learners (JLPT N4-N3 level)
- **Vocabulary Learning** - Key word definitions with readings and usage notes
- **Cultural Context** - Manga-specific language and cultural references explained

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Vision API key
- Anthropic Claude API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/blamb888/urzasight.git
cd urzasight
```

2. Set up the backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
python app.py
```

3. Open the frontend:
```bash
cd ../frontend
# Open index.html in your browser
```

## 📱 Usage

1. Take a clear photo of a manga page
2. Upload the image to Urzasight
3. Get instant translation, grammar analysis, and cultural context
4. Learn Japanese through your favorite manga!

## 🗂️ Project Structure

```
urzasight/
├── backend/           # Flask API server
├── frontend/          # Web interface
├── docs/             # Documentation
├── tests/            # Test files
├── assets/           # Sample images and resources
└── scripts/          # Utility scripts
```

## 🛣️ Roadmap

- [x] **MVP Web App** - Basic photo upload and translation
- [ ] **Mobile Optimization** - Camera integration and touch interface
- [ ] **Real-time Processing** - Live camera translation
- [ ] **Speech Bubble Detection** - Automatic panel segmentation
- [ ] **Wearable Integration** - Smart glasses compatibility
- [ ] **AR Overlay** - Subtitles over manga panels

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Japanese language learning community
- Manga creators and publishers
- Open source OCR and AI projects

---

**Built with ❤️ for manga lovers and Japanese language learners**
