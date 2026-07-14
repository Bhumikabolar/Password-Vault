import numpy as np
import pandas as pd
import re
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Embedding
from tensorflow.keras.utils import to_categorical
import zxcvbn
from password_strength import PasswordStats

class PasswordStrengthAnalyzer:
    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.nn_model = None
        self.lstm_model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def extract_features(self, password):
        """Extract comprehensive features from password"""
        features = {}
        
        # Basic features
        features['length'] = len(password)
        features['uppercase_count'] = sum(1 for c in password if c.isupper())
        features['lowercase_count'] = sum(1 for c in password if c.islower())
        features['digit_count'] = sum(1 for c in password if c.isdigit())
        features['special_count'] = sum(1 for c in password if not c.isalnum())
        
        # Character diversity
        features['unique_chars'] = len(set(password))
        features['char_diversity'] = features['unique_chars'] / max(len(password), 1)
        
        # Pattern features
        features['has_consecutive_letters'] = bool(re.search(r'[a-zA-Z]{3,}', password))
        features['has_consecutive_digits'] = bool(re.search(r'\d{3,}', password))
        features['has_keyboard_pattern'] = bool(re.search(r'(qwerty|asdf|zxcv|123|abc)', password.lower()))
        features['has_repeated_chars'] = len(re.findall(r'(.)\1+', password)) > 0
        
        # Entropy features
        char_types = 0
        if features['lowercase_count'] > 0:
            char_types += 1
        if features['uppercase_count'] > 0:
            char_types += 1
        if features['digit_count'] > 0:
            char_types += 1
        if features['special_count'] > 0:
            char_types += 1
        
        features['char_types'] = char_types
        features['entropy'] = len(password) * np.log2(char_types) if char_types > 0 else 0
        
        # Zxcvbn features
        zxcvbn_result = zxcvbn.zxcvbn(password)
        features['zxcvbn_score'] = zxcvbn_result['score']
        features['zxcvbn_guesses'] = np.log10(max(zxcvbn_result['guesses'], 1))
        
        # PasswordStats features
        stats = PasswordStats(password)
        features['password_stats_strength'] = stats.strength()
        
        return features
    
    def prepare_training_data(self, passwords, labels):
        """Prepare training data with feature extraction"""
        X = []
        for password in passwords:
            features = self.extract_features(password)
            X.append(list(features.values()))
        
        self.feature_columns = list(self.extract_features("dummy").keys())
        X = np.array(X)
        y = np.array(labels)
        
        return X, y
    
    def train_models(self, X, y):
        """Train multiple ML models"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_model.fit(X_train_scaled, y_train)
        
        # Train Gradient Boosting
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.gb_model.fit(X_train_scaled, y_train)
        
        # Train Neural Network
        self.nn_model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        self.nn_model.fit(X_train_scaled, y_train)
        
        # Train LSTM model (for sequence-based analysis)
        self.train_lstm_model(passwords[:len(X_train)], y_train)
        
        # Evaluate models
        models = {
            'Random Forest': (self.rf_model, X_test_scaled),
            'Gradient Boosting': (self.gb_model, X_test_scaled),
            'Neural Network': (self.nn_model, X_test_scaled)
        }
        
        results = {}
        for name, (model, X_test_data) in models.items():
            y_pred = model.predict(X_test_data)
            accuracy = accuracy_score(y_test, y_pred)
            results[name] = accuracy
            print(f"{name} Accuracy: {accuracy:.4f}")
        
        return results
    
    def train_lstm_model(self, passwords, labels):
        """Train LSTM model for sequence-based password analysis"""
        # Character to index mapping
        all_chars = set(''.join(passwords))
        char_to_idx = {char: idx + 1 for idx, char in enumerate(all_chars)}
        char_to_idx['<PAD>'] = 0
        
        # Prepare sequences
        max_len = 50
        X_seq = []
        for password in passwords:
            seq = [char_to_idx.get(char, 0) for char in password[:max_len]]
            seq += [0] * (max_len - len(seq))  # Padding
            X_seq.append(seq)
        
        X_seq = np.array(X_seq)
        y_cat = to_categorical(labels)
        
        # Build LSTM model
        self.lstm_model = Sequential([
            Embedding(len(char_to_idx), 32, input_length=max_len),
            LSTM(64, dropout=0.2, recurrent_dropout=0.2),
            Dense(32, activation='relu'),
            Dropout(0.5),
            Dense(y_cat.shape[1], activation='softmax')
        ])
        
        self.lstm_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.lstm_model.fit(X_seq, y_cat, epochs=10, batch_size=32, validation_split=0.2, verbose=0)
    
    def predict_strength(self, password):
        """Predict password strength using ensemble of models"""
        features = self.extract_features(password)
        X = np.array([list(features.values())])
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from all models
        rf_pred = self.rf_model.predict_proba(X_scaled)[0]
        gb_pred = self.gb_model.predict_proba(X_scaled)[0]
        nn_pred = self.nn_model.predict_proba(X_scaled)[0]
        
        # Ensemble prediction (weighted average)
        ensemble_pred = (rf_pred * 0.4 + gb_pred * 0.4 + nn_pred * 0.2)
        predicted_class = np.argmax(ensemble_pred)
        confidence = np.max(ensemble_pred)
        
        # Strength levels
        strength_levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
        
        return {
            'strength': strength_levels[predicted_class],
            'score': predicted_class,
            'confidence': confidence,
            'features': features,
            'recommendations': self.generate_recommendations(password, features, predicted_class)
        }
    
    def generate_recommendations(self, password, features, strength_score):
        """Generate password strengthening recommendations"""
        recommendations = []
        
        if features['length'] < 12:
            recommendations.append(f"Increase length to at least 12 characters (current: {features['length']})")
        
        if features['uppercase_count'] == 0:
            recommendations.append("Add uppercase letters")
        
        if features['lowercase_count'] == 0:
            recommendations.append("Add lowercase letters")
        
        if features['digit_count'] < 2:
            recommendations.append("Add more numbers (at least 2)")
        
        if features['special_count'] < 2:
            recommendations.append("Add more special characters (at least 2)")
        
        if features['char_diversity'] < 0.7:
            recommendations.append("Increase character diversity (avoid repeating characters)")
        
        if features['has_keyboard_pattern']:
            recommendations.append("Avoid keyboard patterns like 'qwerty' or '123'")
        
        if features['has_repeated_chars']:
            recommendations.append("Avoid consecutive repeated characters")
        
        if strength_score < 3:
            recommendations.append("Consider using a passphrase with unrelated words")
        
        return recommendations
    
    def save_models(self, path):
        """Save trained models"""
        joblib.dump({
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'nn_model': self.nn_model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, f"{path}/ml_models.joblib")
        
        self.lstm_model.save(f"{path}/lstm_model.h5")
    
    def load_models(self, path):
        """Load pre-trained models"""
        data = joblib.load(f"{path}/ml_models.joblib")
        self.rf_model = data['rf_model']
        self.gb_model = data['gb_model']
        self.nn_model = data['nn_model']
        self.scaler = data['scaler']
        self.feature_columns = data['feature_columns']
        
        self.lstm_model = tf.keras.models.load_model(f"{path}/lstm_model.h5")
