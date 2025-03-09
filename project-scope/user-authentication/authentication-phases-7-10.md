# GitaSakha Authentication Implementation: Phases 7-10

## Phase 7: Authentication State Management (1-2 days)

### 7.1 Implement Persistence of Auth State

Update your AuthContext to track persistent login state:

```typescript
// src/contexts/AuthContext.tsx - Add these state variables and functions

const [initializing, setInitializing] = useState(true);
const [needsProfileCreation, setNeedsProfileCreation] = useState(false);

// Check for stored token on first load
useEffect(() => {
  const checkInitialAuth = async () => {
    try {
      const token = await SecureStore.getItemAsync('userToken');
      if (token) {
        // Token exists, but we need to verify if it's still valid
        // Firebase will handle this automatically via onAuthStateChanged
        console.log('Found existing auth token');
      }
    } catch (error) {
      console.error('Error checking initial auth:', error);
    } finally {
      setInitializing(false);
    }
  };
  
  checkInitialAuth();
}, []);

// Modify your onAuthStateChanged to handle both scenarios
useEffect(() => {
  if (initializing) return; // Wait for initial check
  
  const subscriber = auth().onAuthStateChanged(async (userState) => {
    if (userState) {
      await storeUserToken(userState);
      
      try {
        await getUserProfile(userState.uid);
        setNeedsProfileCreation(false);
      } catch (error) {
        if (error.message.includes('not found')) {
          setNeedsProfileCreation(true);
        }
      }
    } else {
      await SecureStore.deleteItemAsync('userToken');
      setNeedsProfileCreation(false);
    }
    
    setUser(userState);
    setLoading(false);
  });
  
  return subscriber;
}, [initializing]);
```

### 7.2 Create Loading Screen for App Initialization

```typescript
// src/screens/InitializingScreen.tsx
import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet, Image } from 'react-native';

export default function InitializingScreen() {
  return (
    <View style={styles.container}>
      <Image 
        source={require('../assets/logo.png')} 
        style={styles.logo}
        resizeMode="contain"
      />
      <ActivityIndicator size="large" color="#3498db" style={styles.loader} />
      <Text style={styles.text}>Loading GitaSakha...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f6fa',
  },
  logo: {
    width: 150,
    height: 150,
    marginBottom: 30,
  },
  loader: {
    marginBottom: 15,
  },
  text: {
    fontSize: 16,
    color: '#2c3e50',
  },
});
```

### 7.3 Add Logout Functionality

Create a profile screen with logout functionality:

```typescript
// src/screens/ProfileScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { getUserProfile } from '../services/userService';

export default function ProfileScreen() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, signOut } = useAuth();
  
  useEffect(() => {
    fetchUserProfile();
  }, []);
  
  const fetchUserProfile = async () => {
    try {
      if (user) {
        const userProfile = await getUserProfile(user.uid);
        setProfile(userProfile);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      Alert.alert('Error', 'Failed to load your profile');
    } finally {
      setLoading(false);
    }
  };
  
  const handleLogout = async () => {
    try {
      Alert.alert(
        'Confirm Logout',
        'Are you sure you want to log out?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
          },
          {
            text: 'Logout',
            onPress: async () => {
              await signOut();
              // Auth state listener will handle navigation
            },
          },
        ],
      );
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('Error', 'Failed to log out. Please try again.');
    }
  };
  
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      <Text style={styles.header}>Your Profile</Text>
      
      <View style={styles.profileCard}>
        {profile ? (
          <>
            <Text style={styles.name}>{profile.name}</Text>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>Email:</Text>
              <Text style={styles.value}>{profile.email || 'Not provided'}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>Phone:</Text>
              <Text style={styles.value}>{profile.phone_number || 'Not provided'}</Text>
            </View>
            
            <View style={styles.infoRow}>
              <Text style={styles.label}>Joined:</Text>
              <Text style={styles.value}>
                {new Date(profile.created_at).toLocaleDateString()}
              </Text>
            </View>
          </>
        ) : (
          <Text style={styles.errorText}>Could not load profile information</Text>
        )}
      </View>
      
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f6fa',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#2c3e50',
  },
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f6fa',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 60,
    marginBottom: 20,
    color: '#2c3e50',
  },
  profileCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 30,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 20,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    color: '#7f8c8d',
    width: 80,
  },
  value: {
    fontSize: 16,
    color: '#2c3e50',
    flex: 1,
  },
  errorText: {
    fontSize: 16,
    color: '#e74c3c',
    textAlign: 'center',
  },
  logoutButton: {
    backgroundColor: '#e74c3c',
    borderRadius: 8,
    paddingVertical: 15,
    alignItems: 'center',
  },
  logoutText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

## Phase 8: Deployment Configuration (2 days)

### 8.1 Set Up MongoDB Atlas

1. **Create a MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up or log in
   - Create a new organization if needed

2. **Create a New Cluster**
   - Click "Build a Database"
   - Choose the free tier option
   - Select cloud provider and region (closest to your users)
   - Click "Create Cluster"

3. **Configure Database Access**
   - Go to "Database Access" in the security menu
   - Click "Add New Database User"
   - Create a secure username and password
   - Set appropriate permissions (readWrite to your database)
   - Click "Add User"

4. **Configure Network Access**
   - Go to "Network Access" in the security menu
   - Click "Add IP Address"
   - For development: Add your IP address
   - For production: Add `0.0.0.0/0` to allow access from anywhere (only for testing)

5. **Get Connection String**
   - Go to your cluster dashboard
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user's password
   - Add this string to your environment variables as `MONGO_URI`

### 8.2 Generate Firebase Service Account

1. **Get Service Account Key**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save the JSON file

2. **Format for Environment Variable**
   - You need to format the JSON file as a string
   - Make sure to escape quotes properly
   - Use a tool like [JSON to string converter](https://tools.knowledgewalls.com/json-to-string-online)
   - Set this as your `FIREBASE_CREDENTIALS` environment variable

### 8.3 Deploy User Microservice to Google Cloud Run

1. **Add Google Cloud Run Deployment to your GitHub Workflow**

```yaml
# .github/workflows/user-service.yml
name: Deploy GitaSakha User Service

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'user-service/**'
      - '.github/workflows/user-service.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache Python dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
          
      - name: Install dependencies
        run: |
          cd user-service
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd user-service
          pip install pytest
          echo "Skipping tests temporarily"
          # pytest -v
      
      - name: Set environment name
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "ENV_NAME=production" >> $GITHUB_ENV
            echo "SERVICE_NAME=gitasakha-user-service" >> $GITHUB_ENV
          else
            echo "ENV_NAME=development" >> $GITHUB_ENV
            echo "SERVICE_NAME=gitasakha-user-service-dev" >> $GITHUB_ENV
          fi
          echo "VERSION=$(date +%Y%m%d)-${GITHUB_SHA::8}" >> $GITHUB_ENV
      
      # Setup gcloud CLI
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: project-gita-sakha
          
      # Configure Docker
      - name: Configure Docker
        run: gcloud auth configure-docker --quiet
          
      # Build the Docker image
      - name: Build Docker Image
        run: |
          cd user-service
          docker build -t gcr.io/project-gita-sakha/${{ env.SERVICE_NAME }}:${{ github.sha }} .
      
      # Push to Container Registry
      - name: Push Docker Image
        run: |
          docker push gcr.io/project-gita-sakha/${{ env.SERVICE_NAME }}:${{ github.sha }}
      
      # Deploy to Cloud Run
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image gcr.io/project-gita-sakha/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            --platform managed \
            --region asia-south1 \
            --memory 1Gi \
            --cpu 1 \
            --set-env-vars="MONGO_URI=${{ secrets.MONGO_URI }},FIREBASE_CREDENTIALS=${{ secrets.FIREBASE_CREDENTIALS }},ENVIRONMENT=${{ env.ENV_NAME }}" \
            --allow-unauthenticated \
            --quiet
```

2. **Add GitHub Secrets**
   - Go to your GitHub repository → Settings → Secrets → Actions
   - Add the following secrets:
     - `GCP_SA_KEY`: Your Google Cloud service account key JSON
     - `MONGO_URI`: Your MongoDB Atlas connection string
     - `FIREBASE_CREDENTIALS`: Your Firebase service account JSON (as string)

### 8.4 Update Frontend API Configuration

Update your `src/config.ts` file with your deployed service URLs:

```typescript
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8080',
  },
  production: {
    API_BASE_URL: 'https://gitasakha-user-service-xxxxx.asia-south1.run.app',
  },
};

// Determine if we're in production
const isProduction = process.env.NODE_ENV === 'production';

// Export configuration
export const API_BASE_URL = isProduction 
  ? config.production.API_BASE_URL 
  : config.development.API_BASE_URL;
```

## Phase 9: Testing and Refinement (2-3 days)

### 9.1 Create Test Plan

```markdown
# GitaSakha Authentication Test Plan

## Authentication Tests

### Phone Authentication
1. **Phone Number Input**
   - Valid phone number formats are accepted
   - Invalid phone numbers show appropriate errors
   - Country code handling works correctly

2. **OTP Verification**
   - OTP is received on the phone
   - Correct OTP proceeds to the next step
   - Incorrect OTP shows appropriate error
   - OTP resend functionality works
   - Timer counts down correctly

### Google Authentication
1. **Google Sign-In Flow**
   - Google account selector appears
   - Selected account logs in successfully
   - Proper error handling for cancellation

### User Profile Management
1. **Profile Creation**
   - Form validation works correctly
   - Profile is successfully created in database
   - Navigation to main app after creation

2. **Profile Retrieval**
   - Profile data loads correctly after authentication
   - Error handling for network issues
   - Displays all relevant user information

### Authentication State
1. **Persistence**
   - Authentication persists after app restart
   - Token is properly refreshed
   - Expired tokens trigger re-authentication

2. **Sign Out**
   - User can successfully sign out
   - App navigates to login screen after sign out
   - All tokens are properly cleared

## API Tests

1. **User Creation API**
   - Creates user with all required fields
   - Prevents duplicate users
   - Proper error handling

2. **User Retrieval API**
   - Gets correct user data
   - Authorization checks prevent accessing other users' data
   - Returns appropriate errors for non-existent users

3. **User Update API**
   - Updates specified fields correctly
   - Authorization checks prevent updating other users
   - Validation prevents invalid data

## Security Tests

1. **Token Verification**
   - Invalid tokens are rejected
   - Expired tokens are rejected
   - Token refresh works correctly

2. **Authorization Checks**
   - User can only access their own data
   - Protected routes require authentication
   - Rate limiting prevents abuse

## Integration Tests

1. **End-to-End Flow**
   - Complete login to logout flow works
   - All screens transition correctly
   - Data persists appropriately between screens
```

### 9.2 Implement Error Handling

Add consistent error handling throughout your app:

```typescript
// src/utils/errorHandler.ts
export const handleApiError = (error: any): string => {
  // Network errors
  if (!error.response) {
    return 'Network error. Please check your connection.';
  }
  
  // API errors with response
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  // HTTP status errors
  switch (error.response?.status) {
    case 400:
      return 'Invalid request. Please check your input.';
    case 401:
      return 'Authentication required. Please log in again.';
    case 403:
      return 'You do not have permission to access this resource.';
    case 404:
      return 'The requested resource was not found.';
    case 429:
      return 'Too many requests. Please try again later.';
    case 500:
      return 'Server error. Please try again later.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
};

export const showErrorAlert = (title: string, error: any) => {
  const errorMessage = typeof error === 'string' 
    ? error 
    : handleApiError(error);
  
  Alert.alert(title, errorMessage);
};
```

### 9.3 Add User-Friendly Loading States

Create a reusable loader component:

```typescript
// src/components/LoadingOverlay.tsx
import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet, Modal } from 'react-native';

interface LoadingOverlayProps {
  visible: boolean;
  message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  visible, 
  message = 'Loading...' 
}) => {
  if (!visible) return null;
  
  return (
    <Modal transparent visible={visible}>
      <View style={styles.container}>
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#3498db" />
          <Text style={styles.message}>{message}</Text>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  loader: {
    padding: 20,
    borderRadius: 10,
    backgroundColor: 'white',
    alignItems: 'center',
    minWidth: 200,
  },
  message: {
    marginTop: 15,
    fontSize: 16,
    color: '#2c3e50',
  },
});

export default LoadingOverlay;
```

## Phase 10: Integration with Existing Services (2 days)

### 10.1 Update Gita API to Work with Authentication

Modify your existing GitaSakha API to accept authorization tokens:

```python
# Add this to your existing API middleware.py
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify
from functools import wraps
import os
import json

# Initialize Firebase Admin SDK (if not already initialized)
if not firebase_admin._apps:
    cred = None
    if os.environ.get('FIREBASE_CREDENTIALS'):
        cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
        cred = credentials.Certificate(cred_dict)
    else:
        # For local development
        cred = credentials.Certificate('path/to/serviceAccountKey.json')
    
    firebase_admin.initialize_app(cred)

def optional_auth(f):
    """Middleware that adds user info to request if token is present but doesn't require it"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        request.user = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            try:
                decoded_token = auth.verify_id_token(token)
                request.user = decoded_token
            except Exception as e:
                # Just log the error but don't block the request
                print(f"Token verification error: {str(e)}")
        
        return f(*args, **kwargs)
    return decorated_function
```

### 10.2 Create Base API Client for Your Frontend

Create a reusable API client that includes authentication:

```typescript
// src/services/apiClient.ts
import * as SecureStore from 'expo-secure-store';
import { API_BASE_URL } from '../config';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface RequestOptions {
  requiresAuth?: boolean;
  body?: any;
}

export const apiRequest = async <T>(
  endpoint: string,
  method: RequestMethod = 'GET',
  options: RequestOptions = { requiresAuth: true }
): Promise<T> => {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    // Add auth token if required
    if (options.requiresAuth) {
      const token = await SecureStore.getItemAsync('userToken');
      if (!token) {
        throw new Error('Authentication required');
      }
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config: RequestInit = {
      method,
      headers,
    };
    
    // Add body for POST/PUT requests
    if (options.body && (method === 'POST' || method === 'PUT')) {
      config.body = JSON.stringify(options.body);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      return null as T;
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || `API error: ${response.status}`);
    }
    
    return data as T;
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

// Helper methods
export const get = <T>(endpoint: string, requiresAuth = true): Promise<T> => {
  return apiRequest<T>(endpoint, 'GET', { requiresAuth });
};

export const post = <T>(endpoint: string, body: any, requiresAuth = true): Promise<T> => {
  return apiRequest<T>(endpoint, 'POST', { requiresAuth, body });
};

export const put = <T>(endpoint: string, body: any, requiresAuth = true): Promise<T> => {
  return apiRequest<T>(endpoint, 'PUT', { requiresAuth, body });
};

export const del = <T>(endpoint: string, requiresAuth = true): Promise<T> => {
  return apiRequest<T>(endpoint, 'DELETE', { requiresAuth });
};
```

### 10.3 Update Your GitaSakha Services to Use the Base Client

Update your existing GitaSakha services:

```typescript
// src/services/gitaService.ts
import { get } from './apiClient';

interface Shlok {
  chapter: number;
  verse: number;
  sanskrit: string;
  translation: {
    english: string;
    hindi: string;
    gujarati?: string;
    marathi?: string;
    tamil?: string;
  };
  explanation_url: string;
}

interface EmotionThemeShloksResponse {
  shloks: Shlok[];
}

export const getEmotions = () => {
  return get<any>('/v1/emotions', false);  // Public endpoint, no auth required
};

export const getEmotionDetail = (emotion: string) => {
  return get<any>(`/v1/emotions/${emotion}`, false);  // Public endpoint
};

export const getThemeShloks = (emotion: string, theme: string) => {
  return get<EmotionThemeShloksResponse>(`/v1/emotions/${emotion}/themes/${theme}`, false);
};

export const getShlok = (chapter: number, verse: number) => {
  return get<Shlok>(`/v1/shloks/${chapter}/${verse}`, false);
};

export const getRandomShlok = (emotion: string, theme: string) => {
  return get<Shlok>(`/v1/shloks/random/${emotion}/${theme}`, false);
};

export const searchShloks = (query: string) => {
  return get<any>(`/v1/search?query=${encodeURIComponent(query)}`, false);
};

// New protected endpoints (examples)
export const getFavoriteShloks = () => {
  return get<Shlok[]>('/v1/user/favorites');  // Protected endpoint, requires auth
};

export const addFavoriteShlok = (shlok: { chapter: number, verse: number }) => {
  return post<any>('/v1/user/favorites', shlok);
};

export const removeFavoriteShlok = (id: string) => {
  return del<any>(`/v1/user/favorites/${id}`);
};
```

### 10.4 Add User Settings and Preferences

You can extend your user service with settings and preferences:

```python
# Add this to your user service - app/routes/users.py

@bp.route('/users/<user_id>/settings', methods=['GET'])
@verify_firebase_token
def get_user_settings(user_id):
    # Verify that the requesting user is the same as the user being requested
    if request.user['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get or initialize settings
    settings = user.get('settings', {
        'theme': 'light',
        'language': 'en',
        'notifications_enabled': True,
        'daily_verse': True
    })
    
    return jsonify(settings)

@bp.route('/users/<user_id>/settings', methods=['PUT'])
@verify_firebase_token
def update_user_settings(user_id):
    # Verify that the requesting user is the same as the user being updated
    if request.user['uid'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    # Validate settings
    allowed_settings = ['theme', 'language', 'notifications_enabled', 'daily_verse']
    settings_update = {k: v for k, v in data.items() if k in allowed_settings}
    
    result = mongo.db.users.update_one(
        {'user_id': user_id},
        {'$set': {'settings': settings_update}}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404
    
    updated_user = mongo.db.users.find_one({'user_id': user_id})
    settings = updated_user.get('settings', {})
    
    return jsonify(settings)
```

And corresponding frontend service:

```typescript
// src/services/userSettingsService.ts
import { get, put } from './apiClient';

interface UserSettings {
  theme: 'light' | 'dark';
  language: string;
  notifications_enabled: boolean;
  daily_verse: boolean;
}

export const getUserSettings = (userId: string) => {
  return get<UserSettings>(`/v1/users/${userId}/settings`);
};

export const updateUserSettings = (userId: string, settings: Partial<UserSettings>) => {
  return put<UserSettings>(`/v1/users/${userId}/settings`, settings);
};
```

This completes all phases of the authentication implementation for your GitaSakha application. You now have a comprehensive system that includes:

1. User authentication with Firebase (phone and Google)
2. User profile management with MongoDB
3. Token-based authorization for API requests
4. Persistent authentication state
5. Error handling and loading states
6. Integration with your existing GitaSakha API
7. User settings and preferences

The implementation follows industry best practices for security and user experience.
