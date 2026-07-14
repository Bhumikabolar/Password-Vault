import pandas as pd
import numpy as np
import random
import string
from password_strength_analyzer import PasswordStrengthAnalyzer
import zxcvbn
import joblib
import os

class PasswordDataGenerator:
    def __init__(self):
        self.common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'password1',
            'qwerty123', 'admin123', 'root', 'toor', 'pass', 'test', 'guest',
            'user', 'login', 'default', 'changeme', 'master', 'shadow', 'dragon'
        ]
        
        self.common_words = [
            'apple', 'banana', 'orange', 'grape', 'lemon', 'peach', 'berry',
            'happy', 'smile', 'laugh', 'joy', 'cheer', 'bright', 'sunny',
            'ocean', 'river', 'mountain', 'forest', 'desert', 'island',
            'tiger', 'elephant', 'giraffe', 'monkey', 'dolphin', 'eagle',
            'coffee', 'tea', 'water', 'juice', 'milk', 'honey', 'sugar',
            'music', 'dance', 'rhythm', 'melody', 'harmony', 'beat', 'song',
            'book', 'story', 'novel', 'poem', 'letter', 'page', 'chapter',
            'dream', 'wonder', 'magic', 'mystery', 'adventure', 'journey',
            'courage', 'wisdom', 'strength', 'hope', 'faith', 'love', 'kindness'
        ]
    
    def generate_weak_passwords(self, count=1000):
        """Generate weak passwords for training"""
        passwords = []
        
        for _ in range(count):
            password_type = random.choice(['short', 'common', 'simple', 'pattern'])
            
            if password_type == 'short':
                # Short passwords (4-6 characters)
                length = random.randint(4, 6)
                password = ''.join(random.choices(string.ascii_lowercase, k=length))
            
            elif password_type == 'common':
                # Common passwords with variations
                base = random.choice(self.common_passwords)
                if random.random() < 0.3:
                    base += str(random.randint(0, 999))
                if random.random() < 0.2:
                    base = base.capitalize()
                password = base
            
            elif password_type == 'simple':
                # Only lowercase or only numbers
                if random.random() < 0.5:
                    length = random.randint(6, 10)
                    password = ''.join(random.choices(string.ascii_lowercase, k=length))
                else:
                    length = random.randint(6, 12)
                    password = ''.join(random.choices(string.digits, k=length))
            
            else:  # pattern
                # Keyboard patterns or sequences
                patterns = ['qwerty', 'asdf', 'zxcv', '123456', 'abcdef']
                pattern = random.choice(patterns)
                if random.random() < 0.3:
                    pattern += str(random.randint(0, 99))
                password = pattern
            
            passwords.append(password)
        
        return passwords
    
    def generate_moderate_passwords(self, count=1000):
        """Generate moderate strength passwords"""
        passwords = []
        
        for _ in range(count):
            password_type = random.choice(['mixed', 'word_number', 'basic_complex'])
            
            if password_type == 'mixed':
                # Mix of character types but predictable
                length = random.randint(8, 12)
                password = ''
                password += random.choice(string.ascii_lowercase)
                password += random.choice(string.ascii_uppercase)
                password += ''.join(random.choices(string.ascii_lowercase, k=length-2))
                if random.random() < 0.5:
                    password += str(random.randint(0, 99))
            
            elif password_type == 'word_number':
                # Word + number combination
                word = random.choice(self.common_words)
                number = str(random.randint(0, 9999))
                if random.random() < 0.5:
                    password = word + number
                else:
                    password = number + word
            
            else:  # basic_complex
                # Has different character types but weak patterns
                length = random.randint(8, 10)
                chars = string.ascii_lowercase + string.digits
                password = ''.join(random.choices(chars, k=length))
                # Add one uppercase at the beginning
                password = password[0].upper() + password[1:]
            
            passwords.append(password)
        
        return passwords
    
    def generate_strong_passwords(self, count=1000):
        """Generate strong passwords"""
        passwords = []
        
        for _ in range(count):
            password_type = random.choice(['random', 'passphrase', 'complex'])
            
            if password_type == 'random':
                # Truly random with good length
                length = random.randint(12, 20)
                chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
                password = ''.join(random.choices(chars, k=length))
            
            elif password_type == 'passphrase':
                # Multiple random words with separators
                word_count = random.randint(3, 5)
                words = random.sample(self.common_words, word_count)
                separator = random.choice(['-', '_', '.', ''])
                password = separator.join(words)
                if random.random() < 0.5:
                    password += str(random.randint(0, 999))
                if random.random() < 0.3:
                    password += random.choice('!@#$%^&*')
            
            else:  # complex
                # Complex with good entropy
                length = random.randint(14, 18)
                # Ensure good mix of character types
                password = ''
                password += ''.join(random.choices(string.ascii_lowercase, k=length//4))
                password += ''.join(random.choices(string.ascii_uppercase, k=length//4))
                password += ''.join(random.choices(string.digits, k=length//4))
                password += ''.join(random.choices('!@#$%^&*()_+-=[]{}|;:,.<>?', k=length//4))
                # Shuffle
                password = ''.join(random.sample(password, len(password)))
            
            passwords.append(password)
        
        return passwords
    
    def generate_training_data(self, samples_per_class=1000):
        """Generate complete training dataset"""
        print("Generating training data...")
        
        # Generate passwords for each strength level
        weak_passwords = self.generate_weak_passwords(samples_per_class)
        moderate_passwords = self.generate_moderate_passwords(samples_per_class)
        strong_passwords = self.generate_strong_passwords(samples_per_class)
        
        # Create labels (0=Very Weak, 1=Weak, 2=Fair, 3=Good, 4=Strong)
        passwords = []
        labels = []
        
        # Very Weak (0) - first half of weak passwords
        passwords.extend(weak_passwords[:samples_per_class//2])
        labels.extend([0] * (samples_per_class//2))
        
        # Weak (1) - second half of weak passwords
        passwords.extend(weak_passwords[samples_per_class//2:])
        labels.extend([1] * (samples_per_class//2))
        
        # Fair (2) - first half of moderate passwords
        passwords.extend(moderate_passwords[:samples_per_class//2])
        labels.extend([2] * (samples_per_class//2))
        
        # Good (3) - second half of moderate passwords
        passwords.extend(moderate_passwords[samples_per_class//2:])
        labels.extend([3] * (samples_per_class//2))
        
        # Strong (4) - all strong passwords
        passwords.extend(strong_passwords)
        labels.extend([4] * samples_per_class)
        
        # Shuffle the dataset
        combined = list(zip(passwords, labels))
        random.shuffle(combined)
        passwords, labels = zip(*combined)
        
        print(f"Generated {len(passwords)} training samples")
        return list(passwords), list(labels)

def train_and_save_models():
    """Train and save the ML models"""
    print("Starting model training...")
    
    # Initialize components
    analyzer = PasswordStrengthAnalyzer()
    data_generator = PasswordDataGenerator()
    
    # Generate training data
    passwords, labels = data_generator.generate_training_data(samples_per_class=2000)
    
    # Prepare features
    print("Extracting features...")
    X, y = analyzer.prepare_training_data(passwords, labels)
    
    # Train models
    print("Training ML models...")
    results = analyzer.train_models(X, y)
    
    print("\nTraining Results:")
    for model_name, accuracy in results.items():
        print(f"{model_name}: {accuracy:.4f}")
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save models
    print("Saving models...")
    analyzer.save_models('models')
    
    # Save training data for future use
    training_data = {
        'passwords': passwords,
        'labels': labels,
        'feature_columns': analyzer.feature_columns
    }
    joblib.dump(training_data, 'models/training_data.joblib')
    
    print("Models saved successfully!")
    
    # Test the trained models
    print("\nTesting trained models...")
    test_passwords = [
        '123456',  # Very Weak
        'password',  # Weak
        'Password123',  # Fair
        'MyP@ssw0rd!',  # Good
        'TrulyR@nd0mP@ssw0rd!123#',  # Strong
    ]
    
    for test_pwd in test_passwords:
        result = analyzer.predict_strength(test_pwd)
        print(f"Password: '{test_pwd}' -> {result['strength']} (Score: {result['score']}, Confidence: {result['confidence']:.3f})")

if __name__ == "__main__":
    train_and_save_models()
