# GitaSakha Authentication Implementation: Phases 1-3

## Phase 1: Firebase Authentication Setup (1-2 days)

### 1.1 Create Firebase Project
- Go to [Firebase Console](https://console.firebase.google.com/)
- Click "Add project"
- Name it "GitaSakha"
- Enable Google Analytics (recommended)
- Create project

### 1.2 Register Apps
- In Firebase console, add both Android and iOS apps
- For Android:
  - Package name: Your app's package name from app.json
  - Download `google-services.json` → place in `android/app/`
- For iOS:
  - Bundle ID: From app.json
  - Download `GoogleService-Info.plist` → place in `ios/{YourProjectName}/`

### 1.3 Enable Authentication Methods
- Go to Authentication → Sign-in method
- Enable Phone Authentication:
  - Add your test phone number
  - Add SHA-1 certificate for Android
- Enable Google Sign-in:
  - Configure authorized domains

### 1.4 Install Firebase SDK
```bash
# Install dependencies
npm install @react-native-firebase/app @react-native-firebase/auth
npm install @react-native-google-signin/google-signin
```

### 1.5 Configure Firebase in App
```javascript
// App.tsx
import React, { useEffect } from 'react';
import { StyleSheet } from 'react-native';
import firebase from '@react-native-firebase/app';
import '@react-native-firebase/auth';
import { GoogleSignin } from '@react-native-google-signin/google-signin';

export default function App() {
  useEffect(() => {
    // Initialize Firebase
    if (!firebase.apps.length) {
      firebase.initializeApp();
    }
    
    // Configure Google Sign-in
    GoogleSignin.configure({
      webClientId: 'YOUR_WEB_CLIENT_ID_FROM_FIREBASE_CONSOLE', // Get from Firebase Auth settings
    });
  }, []);

  return (
    // Your existing app code
  );
}
```

## Phase 2: Authentication UI Creation (2-3 days)

### 2.1 Install Navigation Dependencies
```bash
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install expo-secure-store
```

### 2.2 Create Authentication Context
Create file: `src/contexts/AuthContext.tsx`

```javascript
import React, { createContext, useState, useEffect, useContext } from 'react';
import auth from '@react-native-firebase/auth';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import * as SecureStore from 'expo-secure-store';

// Context interface
interface AuthContextProps {
  user: any | null;
  loading: boolean;
  signInWithPhone: (phoneNumber: string) => Promise<any>;
  confirmOtp: (otp: string, confirmation: any) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Initialize auth state listener
  useEffect(() => {
    const subscriber = auth().onAuthStateChanged((userState) => {
      setUser(userState);
      setLoading(false);
    });
    
    return subscriber; // Unsubscribe on unmount
  }, []);

  // Phone auth methods
  const signInWithPhone = async (phoneNumber: string) => {
    try {
      return await auth().signInWithPhoneNumber(phoneNumber);
    } catch (error) {
      console.error('Phone auth error:', error);
      throw error;
    }
  };

  const confirmOtp = async (otp: string, confirmation: any) => {
    try {
      await confirmation.confirm(otp);
    } catch (error) {
      console.error('OTP confirmation error:', error);
      throw error;
    }
  };

  // Google auth method
  const signInWithGoogle = async () => {
    try {
      await GoogleSignin.hasPlayServices();
      const { idToken } = await GoogleSignin.signIn();
      const googleCredential = auth.GoogleAuthProvider.credential(idToken);
      return auth().signInWithCredential(googleCredential);
    } catch (error) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  };

  // Sign out
  const signOut = async () => {
    try {
      await auth().signOut();
      await SecureStore.deleteItemAsync('userToken');
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      signInWithPhone,
      confirmOtp,
      signInWithGoogle,
      signOut
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 2.3 Create Required Authentication Screens

**1. WelcomeScreen.tsx**
```javascript
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';

export default function WelcomeScreen() {
  const navigation = useNavigation();
  const { signInWithGoogle } = useAuth();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to GitaSakha</Text>
      
      <TouchableOpacity 
        style={styles.phoneButton} 
        onPress={() => navigation.navigate('PhoneLogin')}
      >
        <Text style={styles.buttonText}>Sign in with Phone</Text>
      </TouchableOpacity>

      <TouchableOpacity 
        style={styles.googleButton} 
        onPress={() => signInWithGoogle()}
      >
        <Text style={styles.buttonText}>Sign in with Google</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 40,
    textAlign: 'center',
  },
  phoneButton: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    alignItems: 'center',
  },
  googleButton: {
    backgroundColor: '#e74c3c',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

**2. PhoneLoginScreen.tsx**
```javascript
import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';

export default function PhoneLoginScreen() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation();
  const { signInWithPhone } = useAuth();
  
  const handleSendOtp = async () => {
    if (!phoneNumber || phoneNumber.length < 10) {
      Alert.alert('Error', 'Please enter a valid phone number');
      return;
    }
    
    try {
      setLoading(true);
      // Format number with country code if needed
      const formattedNumber = phoneNumber.startsWith('+') ? phoneNumber : `+91${phoneNumber}`;
      const confirmation = await signInWithPhone(formattedNumber);
      navigation.navigate('OtpVerification', { confirmation });
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Enter your phone number</Text>
      
      <TextInput
        style={styles.input}
        placeholder="+91 9876543210"
        keyboardType="phone-pad"
        value={phoneNumber}
        onChangeText={setPhoneNumber}
      />
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={handleSendOtp}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Send OTP</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

**3. OtpVerificationScreen.tsx**
```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useAuth } from '../contexts/AuthContext';

export default function OtpVerificationScreen() {
  const route = useRoute();
  const { confirmation } = route.params || {};
  const { confirmOtp } = useAuth();
  
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [timer, setTimer] = useState(60);
  
  // Countdown timer
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);
  
  const handleVerifyOtp = async () => {
    if (!otp || otp.length < 6) {
      Alert.alert('Error', 'Please enter a valid 6-digit OTP');
      return;
    }
    
    try {
      setLoading(true);
      await confirmOtp(otp, confirmation);
      // Auth state listener will handle navigation after successful verification
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Enter verification code</Text>
      
      <TextInput
        style={styles.input}
        placeholder="6-digit code"
        keyboardType="number-pad"
        value={otp}
        onChangeText={setOtp}
        maxLength={6}
      />
      
      <Text style={styles.timer}>Resend in: {timer}s</Text>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={handleVerifyOtp}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Verify</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
    letterSpacing: 5,
  },
  timer: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#555',
  },
  button: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

**4. LoadingScreen.tsx**
```javascript
import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';

export default function LoadingScreen() {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#3498db" />
      <Text style={styles.text}>Loading...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    marginTop: 10,
    fontSize: 16,
  }
});
```

### 2.4 Set Up Navigation
Update your App.tsx:

```javascript
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import firebase from '@react-native-firebase/app';
import { GoogleSignin } from '@react-native-google-signin/google-signin';

// Import screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import PhoneLoginScreen from './src/screens/PhoneLoginScreen';
import OtpVerificationScreen from './src/screens/OtpVerificationScreen';
import LoadingScreen from './src/screens/LoadingScreen';

// Import your app's main screen component
import MainAppScreen from './src/screens/MainAppScreen';

// Import auth provider
import { AuthProvider, useAuth } from './src/contexts/AuthContext';

const Stack = createStackNavigator();

function AppNavigator() {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user ? (
        <Stack.Screen name="Main" component={MainAppScreen} />
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

export default function App() {
  useEffect(() => {
    if (!firebase.apps.length) {
      firebase.initializeApp();
    }
    
    GoogleSignin.configure({
      webClientId: 'YOUR_WEB_CLIENT_ID_FROM_FIREBASE_CONSOLE',
    });
  }, []);

  return (
    <AuthProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}
```

## Phase 3: Phone Authentication Implementation (2 days)

### 3.1 Testing Phone Authentication
Test your implementation by following these steps:

1. Run your app using `npx expo start`
2. Navigate to the phone login screen
3. Enter a valid phone number (use your own or a test phone number)
4. Receive SMS with verification code
5. Enter the code in the OTP screen
6. Upon successful verification, you should be redirected to the main app screen

### 3.2 Common Issues and Solutions

**Issue: OTP not delivered**
- Solution: Ensure Firebase Phone Auth is properly configured
- Check if the phone number format is correct (include country code)
- Verify SHA-1 certificate is added to Firebase project

**Issue: Invalid OTP error**
- Solution: Ensure the SMS was actually delivered
- Check if you're using the exact code received
- Verify the confirmation object is correctly passed between screens

**Issue: Authentication state not updating**
- Solution: Verify the auth state listener is properly set up
- Check for errors in the console logs
- Make sure the Firebase initialization runs before auth operations

### 3.3 Security Considerations
- Implement rate limiting (Firebase does this automatically)
- Add validation for phone numbers
- Consider adding reCAPTCHA verification for web platforms
- Store authentication tokens securely using expo-secure-store

### 3.4 Customization Options
- Add country code selector for international users
- Customize OTP input field for better user experience
- Implement auto-detection of SMS codes (Android only)
- Add alternative authentication methods as fallback
