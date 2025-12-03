import React from 'react';
import { AppRouter } from './router';
import { AuthProvider } from './context/AuthContext';
import './App.css';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="app">
        <AppRouter />
      </div>
    </AuthProvider>
  );
};

export default App;
