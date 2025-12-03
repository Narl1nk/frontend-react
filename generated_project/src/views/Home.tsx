import React from 'react';
import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  return (
    <div className="home-view">
      <h1>Welcome to the Application</h1>
      <div className="quick-links">
        <Link to="/user">Manage User</Link> {/* Adjusted to match existing views */}
      </div>
    </div>
  );
};
