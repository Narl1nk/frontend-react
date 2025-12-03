import React from 'react';
import { UserList, UserForm } from '../components';

export const UserListView: React.FC = () => {
  const [showForm, setShowForm] = React.useState(false);

  return (
    <div className="user-list-view">
      <div className="view-header">
        <h1>User Management</h1>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Show List' : 'Create New'}
        </button>
      </div>
      {showForm ? (
        <UserForm onSubmit={() => setShowForm(false)} />
      ) : (
        <UserList />
      )}
    </div>
  );
};
