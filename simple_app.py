from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from simple_analyzer import SimplePasswordAnalyzer, SimplePasswordGenerator

app = Flask(__name__)
CORS(app)

# Initialize components
analyzer = SimplePasswordAnalyzer()
generator = SimplePasswordGenerator()

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
            password = generator.generate_random_password(length=length)
        elif password_type == 'passphrase':
            word_count = data.get('word_count', 4)
            separator = data.get('separator', '-')
            password = generator.generate_passphrase(word_count=word_count, separator=separator)
        elif password_type == 'pronounceable':
            length = data.get('length', 12)
            password = generator.generate_pronounceable_password(length=length)
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
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        strengthened_password = generator.strengthen_password(password)
        
        # Analyze both passwords
        original_analysis = analyzer.predict_strength(password)
        strengthened_analysis = analyzer.predict_strength(strengthened_password)
        
        return jsonify({
            'original_password': password,
            'strengthened_password': strengthened_password,
            'original_analysis': original_analysis,
            'strengthened_analysis': strengthened_analysis,
            'recommendations_applied': ['Added missing character types', 'Increased length if needed']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Simple Password Analyzer (Python 3.14 Compatible)")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
