import re
import math
import random
import string
import zxcvbn

class SimplePasswordAnalyzer:
    def __init__(self):
        self.common_patterns = [
            'qwerty', 'asdf', 'zxcv', '123456', 'abcdef', 'password',
            'admin', 'letmein', 'welcome', 'monkey'
        ]
    
    def calculate_entropy(self, password):
        """Calculate password entropy"""
        char_sets = 0
        if any(c.islower() for c in password):
            char_sets += 26
        if any(c.isupper() for c in password):
            char_sets += 26
        if any(c.isdigit() for c in password):
            char_sets += 10
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            char_sets += 32
        
        if char_sets == 0:
            return 0
        
        return len(password) * math.log2(char_sets)
    
    def extract_features(self, password):
        """Extract basic features"""
        features = {
            'length': len(password),
            'uppercase_count': sum(1 for c in password if c.isupper()),
            'lowercase_count': sum(1 for c in password if c.islower()),
            'digit_count': sum(1 for c in password if c.isdigit()),
            'special_count': sum(1 for c in password if not c.isalnum()),
            'unique_chars': len(set(password)),
            'has_common_pattern': any(pattern in password.lower() for pattern in self.common_patterns),
            'has_consecutive': bool(re.search(r'(.)\1{2,}', password)),
            'entropy': self.calculate_entropy(password)
        }
        return features
    
    def predict_strength(self, password):
        """Simple rule-based strength prediction"""
        features = self.extract_features(password)
        
        score = 0
        recommendations = []
        
        # Length scoring
        if features['length'] < 6:
            score += 0
            recommendations.append("Use at least 12 characters")
        elif features['length'] < 8:
            score += 1
            recommendations.append("Increase length to at least 12 characters")
        elif features['length'] < 12:
            score += 2
            recommendations.append("Consider using 12+ characters for better security")
        else:
            score += 3
        
        # Character diversity
        char_types = sum([
            features['uppercase_count'] > 0,
            features['lowercase_count'] > 0,
            features['digit_count'] > 0,
            features['special_count'] > 0
        ])
        
        if char_types == 1:
            score += 0
            recommendations.append("Use mix of character types (uppercase, lowercase, numbers, special chars)")
        elif char_types == 2:
            score += 1
            recommendations.append("Add more character types for better strength")
        elif char_types == 3:
            score += 2
            recommendations.append("Consider adding special characters")
        else:
            score += 3
        
        # Pattern penalties
        if features['has_common_pattern']:
            score = max(0, score - 2)
            recommendations.append("Avoid common patterns like 'qwerty' or 'password'")
        
        if features['has_consecutive']:
            score = max(0, score - 1)
            recommendations.append("Avoid consecutive repeated characters")
        
        # Entropy bonus
        if features['entropy'] > 50:
            score += 2
        elif features['entropy'] > 30:
            score += 1
        
        # Zxcvbn integration
        try:
            zxcvbn_result = zxcvbn.zxcvbn(password)
            zxcvbn_score = zxcvbn_result['score']  # 0-4 scale
            score = (score + zxcvbn_score) / 2
        except:
            pass
        
        # Convert to 0-4 scale
        final_score = min(4, max(0, int(score)))
        
        strength_levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
        
        return {
            'strength': strength_levels[final_score],
            'score': final_score,
            'confidence': 0.85,  # Fixed confidence for simple model
            'features': features,
            'recommendations': recommendations
        }

class SimplePasswordGenerator:
    def __init__(self):
        self.analyzer = SimplePasswordAnalyzer()
        self.word_list = [
            'apple', 'banana', 'orange', 'happy', 'smile', 'ocean', 'river',
            'coffee', 'music', 'dream', 'courage', 'spring', 'crystal'
        ]
    
    def generate_random_password(self, length=16):
        """Generate random password"""
        chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        password = ''.join(random.choices(chars, k=length))
        return password
    
    def generate_passphrase(self, word_count=4, separator='-'):
        """Generate passphrase"""
        words = random.sample(self.word_list, min(word_count, len(self.word_list)))
        return separator.join(words).capitalize()
    
    def generate_pronounceable_password(self, length=12):
        """Generate pronounceable password"""
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        password = ''
        for i in range(length):
            if i % 2 == 0:
                password += random.choice(consonants)
            else:
                password += random.choice(vowels)
        
        # Add some numbers and special characters to make it stronger
        password += str(random.randint(10, 99))
        password += random.choice('!@#$%^&*')
        
        # Shuffle to make it less predictable
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)
        
        return password
    
    def strengthen_password(self, password):
        """Simple password strengthening"""
        features = self.analyzer.extract_features(password)
        strengthened = password
        
        # Add missing character types
        if features['length'] < 12:
            needed = 12 - features['length']
            additions = []
            
            if features['uppercase_count'] == 0:
                additions.append(random.choice(string.ascii_uppercase))
                needed -= 1
            
            if features['digit_count'] < 2:
                additions.extend(random.choices(string.digits, k=min(2, needed)))
                needed -= min(2, needed)
            
            if features['special_count'] < 2:
                special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
                additions.extend(random.choices(special_chars, k=min(2, needed)))
                needed -= min(2, needed)
            
            while needed > 0:
                additions.append(random.choice(string.ascii_letters + string.digits + '!@#$%^&*'))
                needed -= 1
            
            # Insert additions randomly
            for addition in additions:
                pos = random.randint(0, len(strengthened))
                strengthened = strengthened[:pos] + addition + strengthened[pos:]
        
        return strengthened
