# GitaSakha Authentication Implementation: Phases 4-6

## Phase 4: Google Authentication Implementation (1-2 days)

### 4.1 Configure Google Sign-In
Ensure you have proper configuration in your app:

```javascript
// In your App.tsx initialization
import { GoogleSignin } from '@react-native-google-signin/google-signin';

// Initialize during app startup
GoogleSignin.configure({
  webClientId: 'YOUR_WEB_CLIENT_ID_FROM_FIREBASE_CONSOLE', // Get from Firebase Console
  offlineAccess: true,
});
```

### 4.2 Get Web Client ID from Firebase
1. Go to Firebase Console → Authentication → Sign-in method → Google
2. Enable Google sign-in if not already enabled
3. Find the "Web SDK configuration" section
4. Copy the Web Client ID (format: `123456789012-abcdefghijklmnopqrst.apps.googleusercontent.com`)

### 4.3 Implement Google Sign-In Button
Add this to your WelcomeScreen.tsx:

```javascript
// In WelcomeScreen.tsx
import { useAuth } from '../contexts/AuthContext';

// Inside your component
const { signInWithGoogle } = useAuth();
  
const handleGoogleSignIn = async () => {
  try {
    await signInWithGoogle();
    // Auth state listener will handle navigation
  } catch (error) {
    console.error('Google sign-in error:', error);
    Alert.alert('Sign In Failed', 'Could not sign in with Google.');
  }
};

// In your JSX
<TouchableOpacity 
  style={styles.googleButton} 
  onPress={handleGoogleSignIn}
>
  <Text style={styles.buttonText}>Sign in with Google</Text>
</TouchableOpacity>
```

### 4.4 Testing Google Sign-In
1. Run your app on a physical device or emulator with Google Play Services
2. Tap the Google Sign-In button
3. Select a Google account from the popup
4. Upon successful authentication, you should be redirected to your main app

### 4.5 Android Configuration
To make Google Sign-In work on Android, ensure you have:

1. Added your SHA-1 fingerprint to Firebase project
2. Included the correct `google-services.json` in your project
3. Added the following to your `android/app/build.gradle`:

```gradle
dependencies {
    // ...other dependencies
    implementation 'com.google.android.gms:play-services-auth:20.5.0'
}
```

## Phase 5: User Profile Backend Setup (3-4 days)

### 5.1 Create User Service Directory Structure
Set up your microservice folders:

```
user-service/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── middleware.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── users.py
│   └── models/
│       ├── __init__.py
│       └── user.py
├── requirements.txt
├── run.py
└── Dockerfile
```

### 5.2 Set Up Requirements
Create `requirements.txt`:

```
Flask==3.0.0
Flask-PyMongo==2.3.0
Flask-Cors==4.0.0
firebase-admin==6.2.0
gunicorn==21.2.0
python-dotenv==1.0.0
```

### 5.3 Create Main App File
Create `app/__init__.py`:

```python
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from app.config import Config

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    mongo.init_app(app)
    
    # Register blueprints
    from app.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/v1')
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'environment': app.config.get('ENVIRONMENT', 'development')
        }
    
    return app
```

### 5.4 Create App Configuration
Create `app/config.py`:

```python
import os

class Config:
    DEBUG = os.environ.get('ENVIRONMENT') != 'production'
    TESTING = False
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/gitasakha')
    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', '')
```

### 5.5 Create Firebase Authentication Middleware
Create `app/middleware.py`:

```python
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify
from functools import wraps
import os
import json

# Initialize Firebase Admin SDK
cred = None
if os.environ.get('FIREBASE_CREDENTIALS'):
    cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
    cred = credentials.Certificate(cred_dict)
else:
    # For local development
    cred = credentials.Certificate('path/to/serviceAccountKey.json')

firebase_admin.initialize_app(cred)

def verify_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split('Bearer ')[1]
        try:
            # Verify token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return decorated_function
```

### 5.6 Create User Routes
Create `app/routes/users.py`:

```python
from flask import Blueprint, request, jsonify, current_app
from app.middleware import verify_firebase_token
from app import mongo
from datetime import datetime

bp = Blueprint('users', __name__)

@bp.route('/users', methods=['POST'])
@verify_firebase_token
def create_user():
    data = request.json
    user_id = request.user['uid']
    
    # Check if user already exists
    existing_user = mongo.db.users.find_one({'user_id': user_id})
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    
    # Create new user
    user_data = {
        'user_id': user_id,
        'phone_number': data.get('phone_number', request.user.get('phone_number')),
        'email': data.get('email', request.user.get('email')),
        'name': data.get('name', request.user.get('name')),
        'auth_provider': data.get('auth_provider', 'unknown'),
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow(),
        'profile_complete': False
    }
    
    result = mongo.db.users.insert_one(user_data)
    user_data['_id'] = str(result.inserted_id)
    
    return jsonify(user_data), 201

@bp.route('/users/<user_id>', methods=['GET'])
@verify_firebase_token
def get_user(user_id):
    # Verify that the requesting user is the same as the user being requested
    if request.user['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user['_id'] = str(user['_id'])
    return jsonify(user)

@bp.route('/users/<user_id>', methods=['PUT'])
@verify_firebase_token
def update_user(user_id):
    # Verify that the requesting user is the same as the user being updated
    if request.user['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    # Filter out fields that shouldn't be updated
    update_data = {
        'name': data.get('name'),
        'profile_complete': data.get('profile_complete', False),
        'last_login': datetime.utcnow()
    }
    
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    result = mongo.db.users.update_one(
        {'user_id': user_id},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404
    
    updated_user = mongo.db.users.find_one({'user_id': user_id})
    updated_user['_id'] = str(updated_user['_id'])
    
    return jsonify(updated_user)
```

### 5.7 Create Run Script
Create `run.py`:

```python
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
```

### 5.8 Create Dockerfile
Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]
```

### 5.9 Get Firebase Service Account
1. Go to Firebase console → Project settings → Service accounts
2. Click "Generate new private key"
3. Save the JSON file securely
4. For production, set the JSON content as an environment variable:
   ```
   FIREBASE_CREDENTIALS='{...json content...}'
   ```

## Phase 6: Connect Frontend to Backend (2-3 days)

### 6.1 Create API Service for User Profiles
Create `src/services/userService.ts`:

```typescript
import { API_BASE_URL } from '../config';
import * as SecureStore from 'expo-secure-store';

// User profile interface
interface UserProfile {
  user_id: string;
  name: string;
  email?: string;
  phone_number?: string;
  auth_provider: string;
  profile_complete: boolean;
  created_at: string;
  last_login: string;
}

// Create a new user profile
export const createUserProfile = async (userData: any): Promise<UserProfile> => {
  try {
    const token = await SecureStore.getItemAsync('userToken');
    
    const response = await fetch(`${API_BASE_URL}/v1/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Create user profile error:', error);
    throw error;
  }
};

// Get user profile by user ID
export const getUserProfile = async (userId: string): Promise<UserProfile> => {
  try {
    const token = await SecureStore.getItemAsync('userToken');
    
    const response = await fetch(`${API_BASE_URL}/v1/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get user profile error:', error);
    throw error;
  }
};

// Update user profile
export const updateUserProfile = async (userId: string, userData: any): Promise<UserProfile> => {
  try {
    const token = await SecureStore.getItemAsync('userToken');
    
    const response = await fetch(`${API_BASE_URL}/v1/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(userData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Update user profile error:', error);
    throw error;
  }
};
```

### 6.2 Create Config File
Create `src/config.ts`:

```typescript
// App configuration
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8080'
  },
  production: {
    API_BASE_URL: 'https://gitasakha-user-service-XXXXX.asia-south1.run.app'
  }
};

// Determine environment
const environment = process.env.NODE_ENV || 'development';

// Export appropriate configuration
export const API_BASE_URL = config[environment].API_BASE_URL;
```

### 6.3 Update AuthContext with Token Management
Update your AuthContext.tsx:

```typescript
// Add these methods to your AuthContext
const storeUserToken = async (user) => {
  try {
    // Get ID token from Firebase
    const token = await user.getIdToken();
    
    // Store token in secure storage
    await SecureStore.setItemAsync('userToken', token);
    
    // Set token refresh timer
    setupTokenRefresh(user);
  } catch (error) {
    console.error('Token storage error:', error);
  }
};

const setupTokenRefresh = (user) => {
  // Firebase tokens expire in 1 hour
  // Set a timer to refresh token every 50 minutes
  const REFRESH_INTERVAL = 50 * 60 * 1000; // 50 minutes
  
  setInterval(async () => {
    try {
      const newToken = await user.getIdToken(true);
      await SecureStore.setItemAsync('userToken', newToken);
    } catch (error) {
      console.error('Token refresh error:', error);
    }
  }, REFRESH_INTERVAL);
};

// Update the onAuthStateChanged listener
useEffect(() => {
  const subscriber = auth().onAuthStateChanged(async (userState) => {
    if (userState) {
      // Store the token when user logs in
      await storeUserToken(userState);
      
      // Check if user profile exists in the backend
      try {
        await getUserProfile(userState.uid);
        // User exists, no need for profile creation
      } catch (error) {
        // If user profile doesn't exist, set a flag to redirect to profile creation
        setNeedsProfileCreation(true);
      }
    } else {
      // Clear token when user logs out
      await SecureStore.deleteItemAsync('userToken');
    }
    
    setUser(userState);
    setLoading(false);
  });
  
  return subscriber;
}, []);
```

### 6.4 Create Profile Creation Component
Create `src/screens/ProfileCreationScreen.tsx`:

```typescript
import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';
import { createUserProfile } from '../services/userService';

export default function ProfileCreationScreen() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation();
  const { user } = useAuth();
  
  const handleCreateProfile = async () => {
    if (!name.trim()) {
      Alert.alert('Required Field', 'Please enter your name');
      return;
    }
    
    try {
      setLoading(true);
      
      // Determine auth provider
      let authProvider = 'unknown';
      if (user.phoneNumber) {
        authProvider = 'phone';
      } else if (user.providerData?.some(p => p.providerId === 'google.com')) {
        authProvider = 'google';
      }
      
      // Prepare user data
      const userData = {
        name,
        phone_number: user.phoneNumber || '',
        email: user.email || '',
        auth_provider: authProvider,
        profile_complete: true
      };
      
      // Create user profile
      await createUserProfile(userData);
      
      // Navigate to main app
      navigation.reset({
        index: 0,
        routes: [{ name: 'Main' }],
      });
    } catch (error) {
      Alert.alert('Error', error.message || 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Complete Your Profile</Text>
      <Text style={styles.subtitle}>Tell us a bit about yourself</Text>
      
      <View style={styles.form}>
        <Text style={styles.label}>Your Name</Text>
        <TextInput
          style={styles.input}
          placeholder="Full Name"
          value={name}
          onChangeText={setName}
          autoCapitalize="words"
        />
        
        {user?.email && (
          <>
            <Text style={styles.label}>Email</Text>
            <TextInput
              style={[styles.input, styles.disabledInput]}
              value={user.email}
              editable={false}
            />
          </>
        )}
        
        {user?.phoneNumber && (
          <>
            <Text style={styles.label}>Phone</Text>
            <TextInput
              style={[styles.input, styles.disabledInput]}
              value={user.phoneNumber}
              editable={false}
            />
          </>
        )}
      </View>
      
      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={handleCreateProfile}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Complete Profile</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f6fa',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 60,
    marginBottom: 10,
    color: '#2c3e50',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 30,
    color: '#7f8c8d',
  },
  form: {
    marginBottom: 30,
  },
  label: {
    fontSize: 14,
    marginBottom: 8,
    color: '#34495e',
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#dfe6e9',
    marginBottom: 20,
  },
  disabledInput: {
    backgroundColor: '#f1f2f6',
    color: '#7f8c8d',
  },
  button: {
    backgroundColor: '#3498db',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#95a5a6',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### 6.5 Update Navigation to Handle Profile Creation
Update your navigation setup to include profile creation:

```typescript
// In your navigation component
function AppNavigator() {
  const { user, loading, needsProfileCreation } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user ? (
        needsProfileCreation ? (
          <Stack.Screen name="ProfileCreation" component={ProfileCreationScreen} />
        ) : (
          <Stack.Screen name="Main" component={MainAppScreen} />
        )
      ) : (
        <>
          <Stack.Screen name="Welcome" component={WelcomeScreen} />
          <Stack.Screen name="PhoneLogin" component={PhoneLoginScreen} />
          <Stack.Screen name="OtpVerification" component={OtpVerificationScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}
```

### 6.6 Testing the Full Flow
1. Deploy your user service to Google Cloud Run or run locally for testing
2. Set up MongoDB (locally or using MongoDB Atlas)
3. Test the complete authentication flow:
   - Sign in with phone or Google
   - Create user profile
   - Verify user data is saved in MongoDB
   - Sign out and sign back in
   - Verify profile is loaded correctly

### 6.7 Security Considerations
1. Always use HTTPS for API communications
2. Store tokens in secure storage only (expo-secure-store)
3. Implement token refresh mechanism
4. Add proper error handling for API failures
5. Validate all user inputs
6. Set appropriate CORS policies on your backend
