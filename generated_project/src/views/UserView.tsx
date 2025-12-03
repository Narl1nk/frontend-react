import React from 'react';
import { UserForm, UserList } from '../components';
// Ensure imports are properly aligned

export const UserView: React.FC = () => {
  const [showForm, setShowForm] = React.useState(false);

  return (
    <div className="user-view">
      <div className="view-header">
        <h1>User Management</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Show List' : 'Create New'}
        </button>
      </div>
      {showForm ? <UserForm onSubmit={() => setShowForm(false)} /> : <UserList />}
    </div>
  );
};