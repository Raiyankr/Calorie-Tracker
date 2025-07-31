import React, { useState } from 'react';
import Login from './Login.react';
import HomePage from './HomePage.react';

function LandingPage() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const saveToken = (token) => {
    localStorage.setItem('token', token);
    setToken(token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    
    <div>
      {token ? (
        <HomePage token={token} logout={logout} />
      ) : (
        <Login setToken={saveToken} />
      )}
    </div>
  );
}

export default LandingPage;