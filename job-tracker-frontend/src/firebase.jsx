// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import {getAuth} from 'firebase/auth'
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAGWZcs0EUdeZkD5qTWYtSdyUUNJtrEl04",
  authDomain: "applicationtracker-5a0a5.firebaseapp.com",
  projectId: "applicationtracker-5a0a5",
  storageBucket: "applicationtracker-5a0a5.firebasestorage.app",
  messagingSenderId: "541558579581",
  appId: "1:541558579581:web:c0f24e0434d1504a636c14",
  measurementId: "G-NGWF4XTN69"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth=getAuth(app);
export const analytics = getAnalytics(app);