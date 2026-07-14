from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from password_strength_analyzer import PasswordStrengthAnalyzer
from password_generator import PasswordGenerator

app = Flask(__name__)
CORS(app)

# Initialize components
analyzer = PasswordStrengthAnalyzer()
generator = PasswordGenerator()

# Load pre-trained models if available
models_path = "models"
if os.path.exists(models_path):
    try:
        analyzer.load_models(models_path)
        print("Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Using default models (will need training)")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_password():
    """Analyze password strength"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        result = analyzer.predict_strength(password)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_password():
    """Generate new password"""
    try:
        data = request.get_json()
        password_type = data.get('type', 'random')
        
        if password_type == 'random':
            length = data.get('length', 16)
            include_uppercase = data.get('include_uppercase', True)
            include_digits = data.get('include_digits', True)
            include_special = data.get('include_special', True)
            min_special = data.get('min_special', 2)
            min_digits = data.get('min_digits', 2)
            
            password = generator.generate_random_password(
                length=length,
                include_uppercase=include_uppercase,
                include_digits=include_digits,
                include_special=include_special,
                min_special=min_special,
                min_digits=min_digits
            )
        
        elif password_type == 'passphrase':
            word_count = data.get('word_count', 4)
            separator = data.get('separator', '-')
            capitalize = data.get('capitalize', True)
            include_numbers = data.get('include_numbers', True)
            include_special = data.get('include_special', False)
            
            password = generator.generate_passphrase(
                word_count=word_count,
                separator=separator,
                capitalize=capitalize,
                include_numbers=include_numbers,
                include_special=include_special
            )
        
        elif password_type == 'pronounceable':
            length = data.get('length', 12)
            password = generator.generate_pronounceable_password(length)
        
        else:
            return jsonify({'error': 'Invalid password type'}), 400
        
        # Analyze the generated password
        analysis = analyzer.predict_strength(password)
        
        return jsonify({
            'password': password,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strengthen', methods=['POST'])
def strengthen_password():
    """Strengthen existing password"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        target_strength = data.get('target_strength', 4)
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        strengthened_password, recommendations = generator.strengthen_existing_password(
            password, target_strength
        )
        
        # Analyze both original and strengthened passwords
        original_analysis = analyzer.predict_strength(password)
        strengthened_analysis = analyzer.predict_strength(strengthened_password)
        
        return jsonify({
            'original_password': password,
            'strengthened_password': strengthened_password,
            'original_analysis': original_analysis,
            'strengthened_analysis': strengthened_analysis,
            'recommendations_applied': recommendations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/variations', methods=['POST'])
def get_variations():
    """Get password variations"""
    try:
        data = request.get_json()
        base_password = data.get('password', '')
        count = data.get('count', 5)
        
        if not base_password:
            return jsonify({'error': 'Password is required'}), 400
        
        variations = generator.get_password_variations(base_password, count)
        
        # Analyze each variation
        analyzed_variations = []
        for variation in variations:
            analysis = analyzer.predict_strength(variation)
            analyzed_variations.append({
                'password': variation,
                'analysis': analysis
            })
        
        return jsonify({
            'variations': analyzed_variations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple passwords"""
    try:
        data = request.get_json()
        passwords = data.get('passwords', [])
        
        if not passwords:
            return jsonify({'error': 'Passwords list is required'}), 400
        
        results = []
        for password in passwords:
            analysis = analyzer.predict_strength(password)
            results.append({
                'password': password,
                'analysis': analysis
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
