import React from 'react';
import { AppRouter } from './router';
import { AuthProvider } from './context/AuthContext';
import './App.css';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="app">
        <AppRouter />
      </div>
    </AuthProvider>
  );
};