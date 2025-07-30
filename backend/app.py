#!/usr/bin/env python3
"""
Urzasight Backend Server
A Flask API server to handle OCR and LLM requests for manga translation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class UrzasightBackend:
    def __init__(self):
        self.anthropic_api_key = ANTHROPIC_API_KEY
    
    def process_image_with_google_vision_api_key(self, image_data, api_key):
        """Use Google Cloud Vision REST API with API key"""
        try:
            # Extract base64 image data
            image_content = image_data.split(',')[1]
            
            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()
            
            if 'responses' in result and result['responses']:
                annotations = result['responses'][0].get('textAnnotations', [])
                if annotations:
                    return annotations[0]['description']
            
            return ""
            
        except Exception as e:
            print(f"Google Vision API error: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")
    
    def analyze_with_claude(self, japanese_text):
        """Analyze Japanese text with Claude for translation and grammar"""
        try:
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01"
            }
            
            prompt = f"""You are an expert Japanese language tutor helping someone read manga. 

Japanese text extracted from manga: "{japanese_text}"

Please provide a comprehensive analysis in the following JSON format:

{{
    "translation": "Natural English translation that captures the tone and context",
    "grammar_breakdown": "Detailed breakdown of grammar patterns, particles, verb forms, etc. Explain each component clearly for a JLPT N4-N3 level student",
    "cultural_context": "Any cultural references, slang, manga-specific language, or contextual notes that would help understanding",
    "vocabulary": [
        {{
            "word": "Japanese word",
            "reading": "hiragana/katakana reading",
            "meaning": "English meaning",
            "notes": "Any usage notes or difficulty level"
        }}
    ],
    "difficulty_level": "Beginner/Intermediate/Advanced",
    "tone": "Description of the emotional tone or speaking style"
}}

Focus on being educational and helpful for manga readers learning Japanese."""
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            if 'content' in result and result['content']:
                response_text = result['content'][0]['text']
                
                # Try to extract JSON from the response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            
            # Fallback response
            return {
                "translation": "Translation analysis failed",
                "grammar_breakdown": f"Error analyzing grammar: Unable to parse response",
                "cultural_context": "Unable to provide cultural context",
                "vocabulary": [],
                "difficulty_level": "Unknown",
                "tone": "Unable to determine tone"
            }
            
        except Exception as e:
            print(f"Claude analysis error: {str(e)}")
            # Return fallback response
            return {
                "translation": "Translation analysis failed",
                "grammar_breakdown": f"Error analyzing grammar: {str(e)}",
                "cultural_context": "Unable to provide cultural context",
                "vocabulary": [],
                "difficulty_level": "Unknown",
                "tone": "Unable to determine tone"
            }

# Initialize backend
backend = UrzasightBackend()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "service": "urzasight-backend"})

@app.route('/api/process', methods=['POST'])
def process_manga_page():
    """Complete pipeline: OCR + Analysis"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        ocr_service = data.get('ocr_service', 'google')
        llm_service = data.get('llm_service', 'claude')
        ocr_api_key = data.get('ocr_api_key')
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Step 1: OCR
        if ocr_service == 'google' and ocr_api_key:
            extracted_text = backend.process_image_with_google_vision_api_key(image_data, ocr_api_key)
        else:
            return jsonify({"error": "OCR service configuration missing"}), 400
        
        if not extracted_text.strip():
            return jsonify({"error": "No text detected in image"}), 400
        
        # Step 2: LLM Analysis
        if llm_service == 'claude' and ANTHROPIC_API_KEY:
            analysis = backend.analyze_with_claude(extracted_text)
        else:
            return jsonify({"error": "LLM service configuration missing"}), 400
        
        return jsonify({
            "extracted_text": extracted_text,
            "analysis": analysis,
            "services_used": {
                "ocr": ocr_service,
                "llm": llm_service
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎌 Starting Urzasight Backend Server...")
    print("📝 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /api/process - Complete OCR + Analysis pipeline")
    print("")
    print("🔧 Environment variables needed:")
    print("   GOOGLE_CLOUD_API_KEY - For Google Cloud Vision")
    print("   ANTHROPIC_API_KEY - For Claude analysis")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
