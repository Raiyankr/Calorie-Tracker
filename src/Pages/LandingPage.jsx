import React, { useState } from 'react';
import Login from './Login.react';
import HomePage from './HomePage.react';
import Register from './Register.react';

function LandingPage() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [register, setRegister] = useState(false);

  const saveToken = (token) => {
    localStorage.setItem('token', token);
    setToken(token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  const navigateRegister = () => {
    setRegister(true);
  };

  const navigateLogin = () => {
    setRegister(false);
  };


  return (
    
    <div>

      {register ? (
        <Register setToken={saveToken} navigateLogin={navigateLogin}/>
      ) : (token ? (
        <HomePage token={token} logout={logout} />
      ) : (
        <Login setToken={saveToken} navigateRegister={navigateRegister} />
      ))}
    </div>
  );
}

export default LandingPage;