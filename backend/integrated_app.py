#!/usr/bin/env python3
"""
Urzasight + Google Translate Integration
Leverages Google Translate for OCR + basic translation, adds educational layer
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class UrzasightIntegratedBackend:
    def __init__(self):
        self.google_api_key = GOOGLE_CLOUD_API_KEY
        self.claude_api_key = ANTHROPIC_API_KEY
        print(f"Google Translate API: {'✓' if self.google_api_key else '✗'}")
        print(f"Claude API: {'✓' if self.claude_api_key else '✗'}")
    
    def process_image_with_google_translate(self, image_data):
        """Use Google Cloud Translation API for OCR + translation in one step"""
        try:
            print("Processing with Google Translate API...")
            
            # Extract base64 image data
            if ',' in image_data:
                image_content = image_data.split(',')[1]
            else:
                image_content = image_data
            
            # Google Cloud Translation API with image input
            url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
            
            # For image translation, we still need Vision API for OCR, then Translate API
            # Let's use Vision API for OCR first
            vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_api_key}"
            
            vision_payload = {
                "requests": [
                    {
                        "image": {"content": image_content},
                        "features": [{"type": "TEXT_DETECTION", "maxResults": 10}]
                    }
                ]
            }
            
            # Step 1: Extract text with Vision API
            vision_response = requests.post(vision_url, json=vision_payload)
            vision_result = vision_response.json()
            
            if vision_response.status_code != 200:
                raise Exception(f"Vision API error: {vision_result}")
            
            extracted_text = ""
            if 'responses' in vision_result and vision_result['responses']:
                annotations = vision_result['responses'][0].get('textAnnotations', [])
                if annotations:
                    extracted_text = annotations[0]['description']
            
            if not extracted_text.strip():
                return "", ""
            
            # Step 2: Translate with Google Translate API
            translate_payload = {
                'q': extracted_text,
                'source': 'ja',
                'target': 'en',
                'format': 'text'
            }
            
            translate_response = requests.post(url, data=translate_payload)
            translate_result = translate_response.json()
            
            if translate_response.status_code != 200:
                raise Exception(f"Translate API error: {translate_result}")
            
            google_translation = ""
            if 'data' in translate_result and 'translations' in translate_result['data']:
                google_translation = translate_result['data']['translations'][0]['translatedText']
            
            print(f"Extracted: {extracted_text[:50]}...")
            print(f"Google translated: {google_translation[:50]}...")
            
            return extracted_text, google_translation
            
        except Exception as e:
            print(f"Google processing error: {str(e)}")
            raise Exception(f"Google processing failed: {str(e)}")
    
    def enhance_with_claude(self, japanese_text, google_translation):
        """Use Claude to add educational value on top of Google's translation"""
        try:
            print("Enhancing with Claude educational analysis...")
            
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01"
            }
            
            prompt = f"""You are a Japanese language tutor. You have:

ORIGINAL JAPANESE TEXT: "{japanese_text}"
GOOGLE'S TRANSLATION: "{google_translation}"

Your job is to enhance Google's translation with educational value for manga readers learning Japanese.

Provide analysis in this JSON format:

{{
    "improved_translation": "A more natural/contextual translation if needed, or confirm Google's is good",
    "translation_notes": "Brief explanation of why you kept Google's translation or how you improved it",
    "grammar_analysis": "Detailed breakdown of Japanese grammar patterns, particles, verb forms for JLPT N4-N3 level",
    "vocabulary_spotlight": [
        {{
            "word": "key Japanese word from text",
            "reading": "hiragana reading",
            "meaning": "definition",
            "usage_note": "how it's used in manga/casual speech"
        }}
    ],
    "cultural_context": "Manga-specific language, cultural references, or contextual notes",
    "learning_tips": "Specific tips for remembering or understanding this grammar/vocabulary",
    "difficulty_assessment": "Beginner/Intermediate/Advanced"
}}

Focus on adding educational value that Google Translate doesn't provide. Return only valid JSON."""
            
            payload = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            if response.status_code != 200:
                raise Exception(f"Claude API error: {result}")
            
            if 'content' in result and result['content']:
                response_text = result['content'][0]['text']
                
                # Clean and parse JSON
                try:
                    # Remove any markdown code blocks
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                    
                    # Find JSON boundaries
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    
                    if start != -1 and end > start:
                        json_str = response_text[start:end]
                        # Clean up any control characters that might cause issues
                        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                        parsed_analysis = json.loads(json_str)
                        print("Claude enhancement successful")
                        return parsed_analysis
                        
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    print(f"Raw response: {response_text[:200]}...")
                    
                # Fallback: return structured response with raw text
                return {
                    "improved_translation": google_translation,
                    "translation_notes": "Could not parse structured analysis",
                    "grammar_analysis": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    "vocabulary_spotlight": [],
                    "cultural_context": "Analysis available but not structured",
                    "learning_tips": "Review the grammar analysis section for insights",
                    "difficulty_assessment": "Unknown"
                }
            
            raise Exception("No content in Claude response")
            
        except Exception as e:
            print(f"Claude enhancement error: {str(e)}")
            return {
                "improved_translation": google_translation,
                "translation_notes": f"Enhancement failed: {str(e)}",
                "grammar_analysis": "Could not generate grammar analysis",
                "vocabulary_spotlight": [],
                "cultural_context": "Could not provide cultural context",
                "learning_tips": "Try again or check API configuration",
                "difficulty_assessment": "Unknown"
            }

backend = UrzasightIntegratedBackend()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "urzasight-integrated",
        "google_translate": "✓" if GOOGLE_CLOUD_API_KEY else "✗",
        "claude_enhancement": "✓" if ANTHROPIC_API_KEY else "✗"
    })

@app.route('/api/process-integrated', methods=['POST'])
def process_manga_integrated():
    """Integrated manga processing: Google Translate + Claude enhancement"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        
        print("Starting integrated processing...")
        
        # Step 1: Google Translate for OCR + basic translation
        japanese_text, google_translation = backend.process_image_with_google_translate(image_data)
        
        if not japanese_text.strip():
            return jsonify({"error": "No text detected in image"}), 400
        
        # Step 2: Claude enhancement for educational value
        educational_analysis = backend.enhance_with_claude(japanese_text, google_translation)
        
        return jsonify({
            "japanese_text": japanese_text,
            "google_translation": google_translation,
            "enhanced_analysis": educational_analysis,
            "processing_method": "google_translate + claude_enhancement"
        })
        
    except Exception as e:
        print(f"Integrated processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/text-enhance', methods=['POST'])
def enhance_text_only():
    """For when user already has Japanese text and Google translation"""
    try:
        data = request.get_json()
        japanese_text = data.get('japanese_text', '')
        google_translation = data.get('google_translation', '')
        
        if not japanese_text:
            return jsonify({"error": "No Japanese text provided"}), 400
        
        # If no Google translation provided, get it
        if not google_translation:
            url = f"https://translation.googleapis.com/language/translate/v2?key={backend.google_api_key}"
            translate_payload = {
                'q': japanese_text,
                'source': 'ja', 
                'target': 'en',
                'format': 'text'
            }
            
            response = requests.post(url, data=translate_payload)
            result = response.json()
            
            if response.status_code == 200 and 'data' in result:
                google_translation = result['data']['translations'][0]['translatedText']
            else:
                google_translation = "Translation unavailable"
        
        # Enhance with Claude
        educational_analysis = backend.enhance_with_claude(japanese_text, google_translation)
        
        return jsonify({
            "japanese_text": japanese_text,
            "google_translation": google_translation,
            "enhanced_analysis": educational_analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎌 Urzasight Integrated Backend - Google Translate + Claude Enhancement")
    print("=" * 70)
    print("🔧 Services:")
    print(f"   Google Translate API: {'✓ Ready' if GOOGLE_CLOUD_API_KEY else '✗ Missing'}")  
    print(f"   Claude Enhancement: {'✓ Ready' if ANTHROPIC_API_KEY else '✗ Missing'}")
    print("")
    print("📝 Endpoints:")
    print("   GET  /health - Service status")
    print("   POST /api/process-integrated - Full image processing")
    print("   POST /api/text-enhance - Enhance existing text")
    print("")
    print("🎯 Strategy: Leverage Google's OCR expertise, add educational value")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
