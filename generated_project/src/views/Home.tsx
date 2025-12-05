import React from 'react';
import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  return (
    <div className="home-view">
      <h1>Welcome to the User Management System</h1>
      <div className="quick-links">
        <Link to="/users//list">Manage Users</Link>
      </div>
    </div>
  );
};