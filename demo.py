#!/usr/bin/env python3
"""
Demo script for ML Password Strength Analyzer
This script demonstrates the key features of the password analysis system.
"""

import sys
import os
from password_strength_analyzer import PasswordStrengthAnalyzer
from password_generator import PasswordGenerator

def demo_password_analysis():
    """Demonstrate password analysis functionality"""
    print("=" * 60)
    print("PASSWORD STRENGTH ANALYSIS DEMO")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = PasswordStrengthAnalyzer()
    
    # Test passwords with different strength levels
    test_passwords = [
        ('123456', 'Very Weak - Common pattern'),
        ('password', 'Weak - Common word'),
        ('Password123', 'Fair - Basic complexity'),
        ('MyP@ssw0rd!', 'Good - Good mix of characters'),
        ('TrulyR@nd0mP@ssw0rd!123#', 'Strong - High entropy'),
        ('CorrectHorseBatteryStaple', 'Strong - Passphrase style')
    ]
    
    print("\nAnalyzing test passwords:\n")
    
    for password, description in test_passwords:
        print(f"Password: '{password}' ({description})")
        
        try:
            result = analyzer.predict_strength(password)
            
            print(f"  Strength: {result['strength']}")
            print(f"  Score: {result['score']}/4")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  Length: {result['features']['length']}")
            print(f"  Entropy: {result['features']['entropy']:.2f}")
            
            if result['recommendations']:
                print("  Recommendations:")
                for rec in result['recommendations']:
                    print(f"    - {rec}")
            else:
                print("  Recommendations: None - Password is strong!")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        print("-" * 40)

def demo_password_generation():
    """Demonstrate password generation functionality"""
    print("\n" + "=" * 60)
    print("PASSWORD GENERATION DEMO")
    print("=" * 60)
    
    generator = PasswordGenerator()
    
    # Generate different types of passwords
    print("\n1. Random Passwords:")
    for length in [12, 16, 20]:
        try:
            password = generator.generate_random_password(length=length)
            print(f"  Length {length}: {password}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n2. Passphrases:")
    for word_count in [3, 4, 5]:
        try:
            passphrase = generator.generate_passphrase(word_count=word_count)
            print(f"  {word_count} words: {passphrase}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n3. Pronounceable Passwords:")
    for length in [12, 16]:
        try:
            password = generator.generate_pronounceable_password(length)
            print(f"  Length {length}: {password}")
        except Exception as e:
            print(f"  Error: {e}")

def demo_password_strengthening():
    """Demonstrate password strengthening functionality"""
    print("\n" + "=" * 60)
    print("PASSWORD STRENGTHENING DEMO")
    print("=" * 60)
    
    analyzer = PasswordStrengthAnalyzer()
    generator = PasswordGenerator()
    
    weak_passwords = [
        'password',
        '123456',
        'qwerty',
        'abc123',
        'letmein'
    ]
    
    print("\nStrengthening weak passwords:\n")
    
    for weak_pwd in weak_passwords:
        print(f"Original: '{weak_pwd}'")
        
        try:
            # Analyze original
            original_analysis = analyzer.predict_strength(weak_pwd)
            print(f"  Original Strength: {original_analysis['strength']} (Score: {original_analysis['score']})")
            
            # Strengthen
            strengthened, recommendations = generator.strengthen_existing_password(weak_pwd, target_strength=4)
            print(f"  Strengthened: '{strengthened}'")
            
            # Analyze strengthened
            strengthened_analysis = analyzer.predict_strength(strengthened)
            print(f"  New Strength: {strengthened_analysis['strength']} (Score: {strengthened_analysis['score']})")
            
            if recommendations:
                print("  Improvements applied:")
                for rec in recommendations:
                    print(f"    - {rec}")
        
        except Exception as e:
            print(f"  Error: {e}")
        
        print("-" * 40)

def demo_batch_analysis():
    """Demonstrate batch password analysis"""
    print("\n" + "=" * 60)
    print("BATCH ANALYSIS DEMO")
    print("=" * 60)
    
    analyzer = PasswordStrengthAnalyzer()
    
    # Sample password list
    password_list = [
        '123456',
        'password',
        'Password123',
        'MySecurePassword!',
        'SuperSecureP@ssw0rd2023!',
        'CorrectHorseBatteryStaple',
        'TrulyR@nd0m!#$%',
        'admin',
        'letmein',
        'qwerty123'
    ]
    
    print(f"\nAnalyzing {len(password_list)} passwords:\n")
    
    results = []
    for password in password_list:
        try:
            result = analyzer.predict_strength(password)
            results.append({
                'password': password,
                'strength': result['strength'],
                'score': result['score'],
                'confidence': result['confidence'],
                'length': result['features']['length'],
                'entropy': result['features']['entropy']
            })
        except Exception as e:
            print(f"Error analyzing '{password}': {e}")
    
    # Sort by strength score
    results.sort(key=lambda x: x['score'])
    
    # Display results in a table format
    print(f"{'Password':<25} {'Strength':<12} {'Score':<6} {'Confidence':<12} {'Length':<7} {'Entropy':<8}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['password']:<25} {result['strength']:<12} {result['score']:<6} "
              f"{result['confidence']:<12.3f} {result['length']:<7} {result['entropy']:<8.2f}")

def interactive_demo():
    """Interactive demo for user input"""
    print("\n" + "=" * 60)
    print("INTERACTIVE DEMO")
    print("=" * 60)
    print("\nEnter passwords to analyze (type 'quit' to exit):")
    
    analyzer = PasswordStrengthAnalyzer()
    generator = PasswordGenerator()
    
    while True:
        try:
            password = input("\nEnter password: ").strip()
            
            if password.lower() in ['quit', 'exit', 'q']:
                break
            
            if not password:
                print("Please enter a password.")
                continue
            
            # Analyze password
            result = analyzer.predict_strength(password)
            
            print(f"\nAnalysis Results:")
            print(f"  Strength: {result['strength']}")
            print(f"  Score: {result['score']}/4")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  Length: {result['features']['length']}")
            print(f"  Character Types: {result['features']['char_types']}/4")
            print(f"  Entropy: {result['features']['entropy']:.2f}")
            
            if result['recommendations']:
                print("\nRecommendations:")
                for rec in result['recommendations']:
                    print(f"  - {rec}")
                
                # Offer to strengthen
                choice = input("\nWould you like to see a strengthened version? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    try:
                        strengthened, applied = generator.strengthen_existing_password(password, target_strength=4)
                        strengthened_result = analyzer.predict_strength(strengthened)
                        
                        print(f"\nStrengthened Password: '{strengthened}'")
                        print(f"New Strength: {strengthened_result['strength']} (Score: {strengthened_result['score']})")
                        
                        if applied:
                            print("Improvements applied:")
                            for improvement in applied:
                                print(f"  - {improvement}")
                    except Exception as e:
                        print(f"Error strengthening password: {e}")
            else:
                print("\n✅ Password is strong! No recommendations needed.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nDemo completed!")

def main():
    """Main demo function"""
    print("ML Password Strength Analyzer - Demo")
    print("This demo showcases the capabilities of the password analysis system.\n")
    
    # Check if models are available
    if not os.path.exists('models'):
        print("⚠️  Warning: No pre-trained models found.")
        print("The demo will use default models which may not be as accurate.")
        print("Run 'python train_models.py' to train and save models.\n")
    
    try:
        # Run all demos
        demo_password_analysis()
        demo_password_generation()
        demo_password_strengthening()
        demo_batch_analysis()
        
        # Interactive demo
        interactive_choice = input("\nWould you like to try the interactive demo? (y/n): ").strip().lower()
        if interactive_choice in ['y', 'yes']:
            interactive_demo()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED")
        print("=" * 60)
        print("\nTo run the web application:")
        print("  python app.py")
        print("\nThen visit: http://localhost:5000")
        
    except Exception as e:
        print(f"Demo error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
