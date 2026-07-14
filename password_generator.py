import random
import string
import numpy as np
from collections import Counter
import re
from password_strength_analyzer import PasswordStrengthAnalyzer

class PasswordGenerator:
    def __init__(self):
        self.analyzer = PasswordStrengthAnalyzer()
        self.word_list = self._load_common_words()
        
    def _load_common_words(self):
        """Load common words for passphrase generation"""
        common_words = [
            'apple', 'banana', 'orange', 'grape', 'lemon', 'peach', 'berry', 'melon',
            'happy', 'smile', 'laugh', 'joy', 'cheer', 'bright', 'sunny', 'peace',
            'ocean', 'river', 'mountain', 'forest', 'desert', 'island', 'valley', 'meadow',
            'tiger', 'elephant', 'giraffe', 'monkey', 'dolphin', 'eagle', 'butterfly', 'rainbow',
            'coffee', 'tea', 'water', 'juice', 'milk', 'honey', 'sugar', 'spice',
            'music', 'dance', 'rhythm', 'melody', 'harmony', 'beat', 'song', 'tune',
            'book', 'story', 'novel', 'poem', 'letter', 'page', 'chapter', 'verse',
            'dream', 'wonder', 'magic', 'mystery', 'adventure', 'journey', 'quest', 'discovery',
            'courage', 'wisdom', 'strength', 'hope', 'faith', 'love', 'kindness', 'patience',
            'spring', 'summer', 'autumn', 'winter', 'morning', 'evening', 'midnight', 'dawn',
            'crystal', 'diamond', 'silver', 'golden', 'pearl', 'emerald', 'ruby', 'sapphire'
        ]
        return common_words
    
    def generate_random_password(self, length=16, include_uppercase=True, include_digits=True, 
                                include_special=True, min_special=2, min_digits=2):
        """Generate a strong random password with specified constraints"""
        if length < 8:
            raise ValueError("Password length should be at least 8 characters")
        
        password_chars = []
        
        # Start with lowercase letters
        password_chars.extend(random.choices(string.ascii_lowercase, k=length))
        
        # Ensure minimum requirements
        if include_uppercase:
            uppercase_count = max(1, length // 8)
            for _ in range(uppercase_count):
                idx = random.randint(0, len(password_chars) - 1)
                password_chars[idx] = random.choice(string.ascii_uppercase)
        
        if include_digits:
            digit_count = max(min_digits, length // 8)
            for _ in range(digit_count):
                idx = random.randint(0, len(password_chars) - 1)
                password_chars[idx] = random.choice(string.digits)
        
        if include_special:
            special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            special_count = max(min_special, length // 10)
            for _ in range(special_count):
                idx = random.randint(0, len(password_chars) - 1)
                password_chars[idx] = random.choice(special_chars)
        
        # Shuffle the password
        random.shuffle(password_chars)
        
        password = ''.join(password_chars)
        
        # Check if password meets strength requirements
        strength_result = self.analyzer.predict_strength(password)
        if strength_result['score'] < 3:  # If not strong enough, regenerate
            return self.generate_random_password(length, include_uppercase, include_digits, 
                                               include_special, min_special, min_digits)
        
        return password
    
    def generate_passphrase(self, word_count=4, separator='-', capitalize=True, include_numbers=True, 
                           include_special=False):
        """Generate a memorable passphrase"""
        if word_count < 3:
            raise ValueError("Passphrase should have at least 3 words")
        
        words = random.sample(self.word_list, word_count)
        
        if capitalize:
            words = [word.capitalize() for word in words]
        
        passphrase = separator.join(words)
        
        if include_numbers:
            # Add random numbers to make it stronger
            num_count = random.randint(1, 3)
            for _ in range(num_count):
                position = random.randint(0, len(passphrase))
                passphrase = passphrase[:position] + str(random.randint(0, 9)) + passphrase[position:]
        
        if include_special:
            # Add special characters
            special_chars = '!@#$%^&*'
            special_count = random.randint(1, 2)
            for _ in range(special_count):
                position = random.randint(0, len(passphrase))
                passphrase = passphrase[:position] + random.choice(special_chars) + passphrase[position:]
        
        return passphrase
    
    def strengthen_existing_password(self, password, target_strength=4):
        """Strengthen an existing password while maintaining memorability"""
        current_analysis = self.analyzer.predict_strength(password)
        
        if current_analysis['score'] >= target_strength:
            return password, current_analysis['recommendations']
        
        strengthened = password
        recommendations_applied = []
        
        # Get features
        features = current_analysis['features']
        
        # Add missing character types
        if features['length'] < 12:
            # Add random characters to increase length
            chars_to_add = 12 - features['length']
            additions = []
            
            if features['uppercase_count'] == 0:
                additions.append(random.choice(string.ascii_uppercase))
                recommendations_applied.append("Added uppercase letter")
                chars_to_add -= 1
            
            if features['digit_count'] < 2:
                additions.extend(random.choices(string.digits, k=min(2, chars_to_add)))
                recommendations_applied.append("Added numbers")
                chars_to_add -= min(2, chars_to_add)
            
            if features['special_count'] < 2:
                special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
                additions.extend(random.choices(special_chars, k=min(2, chars_to_add)))
                recommendations_applied.append("Added special characters")
                chars_to_add -= min(2, chars_to_add)
            
            # Fill remaining with random characters
            while chars_to_add > 0:
                additions.append(random.choice(string.ascii_letters + string.digits + '!@#$%^&*'))
                chars_to_add -= 1
            
            # Insert additions at random positions
            for addition in additions:
                position = random.randint(0, len(strengthened))
                strengthened = strengthened[:position] + addition + strengthened[position:]
            
            recommendations_applied.append(f"Increased length to {len(strengthened)} characters")
        
        # Replace common patterns
        if features['has_keyboard_pattern']:
            # Replace common patterns with random characters
            patterns = ['qwerty', 'asdf', 'zxcv', '123', 'abc', 'password']
            for pattern in patterns:
                if pattern in strengthened.lower():
                    replacement = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=len(pattern)))
                    strengthened = strengthened.lower().replace(pattern, replacement, 1)
                    recommendations_applied.append(f"Replaced common pattern '{pattern}'")
                    break
        
        # Add character diversity if needed
        if features['char_diversity'] < 0.7:
            # Replace some repeated characters
            char_counts = Counter(strengthened)
            for char, count in char_counts.items():
                if count > 2 and char.isalnum():
                    # Replace some instances with different characters
                    positions = [i for i, c in enumerate(strengthened) if c == char]
                    replace_count = min(count // 2, len(positions) - 1)
                    replace_positions = random.sample(positions, replace_count)
                    
                    for pos in replace_positions:
                        new_char = random.choice([c for c in string.ascii_letters + string.digits + '!@#$%^&*' if c != char])
                        strengthened = strengthened[:pos] + new_char + strengthened[pos+1:]
                    
                    recommendations_applied.append(f"Reduced repetition of '{char}'")
                    break
        
        # Final check
        final_analysis = self.analyzer.predict_strength(strengthened)
        
        return strengthened, recommendations_applied
    
    def generate_pronounceable_password(self, length=12):
        """Generate a password that's easier to pronounce but still strong"""
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        password = ''
        for i in range(length):
            if i % 2 == 0:
                password += random.choice(consonants)
            else:
                password += random.choice(vowels)
        
        # Add some numbers and special characters
        password += str(random.randint(10, 99))
        password += random.choice('!@#$%^&*')
        
        # Shuffle to make it less predictable
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)
        
        # Ensure it meets strength requirements
        strength_result = self.analyzer.predict_strength(password)
        if strength_result['score'] < 3:
            return self.generate_pronounceable_password(length)
        
        return password
    
    def get_password_variations(self, base_password, count=5):
        """Generate variations of a base password"""
        variations = []
        
        for _ in range(count):
            variation = base_password
            
            # Apply random transformations
            transformations = [
                lambda s: s.replace('a', '@').replace('A', '@'),
                lambda s: s.replace('s', '$').replace('S', '$'),
                lambda s: s.replace('i', '!').replace('I', '!'),
                lambda s: s.replace('o', '0').replace('O', '0'),
                lambda s: s + str(random.randint(0, 999)),
                lambda s: s.capitalize(),
                lambda s: s + random.choice('!@#$%^&*'),
            ]
            
            # Apply 1-3 random transformations
            num_transformations = random.randint(1, 3)
            selected_transformations = random.sample(transformations, num_transformations)
            
            for transform in selected_transformations:
                variation = transform(variation)
            
            # Add some random characters
            for _ in range(random.randint(1, 3)):
                pos = random.randint(0, len(variation))
                char = random.choice(string.ascii_letters + string.digits + '!@#$%^&*')
                variation = variation[:pos] + char + variation[pos:]
            
            if variation not in variations:
                variations.append(variation)
        
        return variations[:count]
