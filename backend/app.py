#!/usr/bin/env python3
"""
Urzasight Real Backend Server
OCR + Claude API for actual manga translation
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
CORS(app)

# Configuration
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class UrzasightBackend:
    def __init__(self):
        self.anthropic_api_key = ANTHROPIC_API_KEY
        print(f"🔑 Claude API Key configured: {'✅ Yes' if self.anthropic_api_key else '❌ No'}")
    
    def process_image_with_google_vision(self, image_data, api_key):
        """Extract text from image using Google Cloud Vision"""
        try:
            print("🔍 Processing image with Google Vision...")
            
            # Extract base64 image data
            if ',' in image_data:
                image_content = image_data.split(',')[1]
            else:
                image_content = image_data
            
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
            
            print(f"📡 Google Vision response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Google Vision error: {result}")
                raise Exception(f"Google Vision API error: {result}")
            
            if 'responses' in result and result['responses']:
                response_data = result['responses'][0]
                
                if 'error' in response_data:
                    raise Exception(f"Google Vision error: {response_data['error']}")
                
                annotations = response_data.get('textAnnotations', [])
                if annotations:
                    extracted_text = annotations[0]['description']
                    print(f"✅ Extracted text: {extracted_text[:100]}...")
                    return extracted_text
            
            print("⚠️ No text detected in image")
            return ""
            
        except Exception as e:
            print(f"❌ Google Vision error: {str(e)}")
            raise Exception(f"OCR failed: {str(e)}")
    
    def analyze_with_claude(self, japanese_text):
        """Analyze Japanese text with Claude"""
        try:
            print("🧠 Analyzing text with Claude...")
            
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

Focus on being educational and helpful for manga readers learning Japanese. Return ONLY the JSON, no other text."""
            
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            print(f"📡 Claude response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Claude error: {result}")
                raise Exception(f"Claude API error: {result}")
            
            if 'content' in result and result['content']:
                response_text = result['content'][0]['text']
                print(f"✅ Claude analysis received: {len(response_text)} characters")
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON in the response
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = response_text[start:end]
                        parsed_analysis = json.loads(json_str)
                        print("✅ Successfully parsed Claude analysis")
                        return parsed_analysis
                    else:
                        print("⚠️ No JSON found in Claude response")
                        # Return raw text as fallback
                        return {
                            "translation": response_text[:200] + "...",
                            "grammar_breakdown": "Could not parse structured analysis",
                            "cultural_context": "Analysis available but not structured",
                            "vocabulary": [],
                            "difficulty_level": "Unknown",
                            "tone": "Could not determine"
                        }
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON parse error: {e}")
                    # Return raw text as fallback
                    return {
                        "translation": response_text[:200] + "...",
                        "grammar_breakdown": "Could not parse structured analysis",
                        "cultural_context": "Analysis available but not structured",
                        "vocabulary": [],
                        "difficulty_level": "Unknown",
                        "tone": "Could not determine"
                    }
            
            raise Exception("No content in Claude response")
            
        except Exception as e:
            print(f"❌ Claude analysis error: {str(e)}")
            return {
                "translation": "Translation analysis failed",
                "grammar_breakdown": f"Error analyzing grammar: {str(e)}",
                "cultural_context": "Unable to provide cultural context due to API error",
                "vocabulary": [],
                "difficulty_level": "Unknown",
                "tone": "Unable to determine tone"
            }

# Initialize backend
backend = UrzasightBackend()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "urzasight-real-backend",
        "google_vision": "✅" if GOOGLE_CLOUD_API_KEY else "❌",
        "claude": "✅" if ANTHROPIC_API_KEY else "❌"
    })

@app.route('/api/process', methods=['POST'])
def process_manga_page():
    """Real manga processing pipeline: OCR + Claude analysis"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        ocr_service = data.get('ocr_service', 'google')
        llm_service = data.get('llm_service', 'claude')
        ocr_api_key = data.get('ocr_api_key')
        
        print(f"🎌 Processing manga page...")
        print(f"📸 OCR Service: {ocr_service}")
        print(f"🧠 LLM Service: {llm_service}")
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Step 1: OCR
        extracted_text = ""
        if ocr_service == 'google':
            if not ocr_api_key:
                return jsonify({"error": "Google Vision API key required"}), 400
            extracted_text = backend.process_image_with_google_vision(image_data, ocr_api_key)
        elif ocr_service == 'mock':
            extracted_text = "こんにちは！元気ですか？"  # Mock for testing
        else:
            return jsonify({"error": "Unknown OCR service"}), 400
        
        if not extracted_text.strip():
            return jsonify({"error": "No text detected in image"}), 400
        
        # Step 2: LLM Analysis
        analysis = {}
        if llm_service == 'claude':
            if not ANTHROPIC_API_KEY:
                return jsonify({"error": "Claude API key not configured"}), 400
            analysis = backend.analyze_with_claude(extracted_text)
        elif llm_service == 'mock':
            analysis = {
                "translation": "Mock translation of extracted text",
                "grammar_breakdown": "Mock grammar analysis",
                "cultural_context": "Mock cultural context",
                "vocabulary": [],
                "difficulty_level": "Mock",
                "tone": "Mock tone"
            }
        else:
            return jsonify({"error": "Unknown LLM service"}), 400
        
        print("✅ Processing complete!")
        
        return jsonify({
            "extracted_text": extracted_text,
            "analysis": analysis,
            "services_used": {
                "ocr": ocr_service,
                "llm": llm_service
            }
        })
        
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎌 Starting Urzasight REAL Backend Server...")
    print("=" * 50)
    print("📝 Available endpoints:")
    print("   GET  /health - Health check with API status")
    print("   POST /api/process - Real manga OCR + translation")
    print("")
    print("🔧 API Configuration:")
    print(f"   Google Vision: {'✅ Configured' if GOOGLE_CLOUD_API_KEY else '❌ Missing'}")
    print(f"   Claude API: {'✅ Configured' if ANTHROPIC_API_KEY else '❌ Missing'}")
    print("")
    print("🎯 Ready for REAL manga translation!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
