import React from 'react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../router/routes'; // Correct this import

export const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to={ROUTES.HOME}>App Name</Link>
      </div>
      <div className="navbar-links">
        <Link to={ROUTES.USER}>User</Link>
      </div>
    </nav>
  );
};