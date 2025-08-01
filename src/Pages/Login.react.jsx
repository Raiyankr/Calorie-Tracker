import React, { useState } from 'react';
import './Login.css'

const Login = ({ setToken }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    // const res = await fetch('http://localhost:5050/api/login', {
    const res = await fetch('https://calorie-tracker-xr.up.railway.app/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (res.ok) {
      setToken(data.access_token); // Save token in parent
    } else {
      alert(data.error || 'Login failed');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    // const res = await fetch('http://localhost:5050/api/register', {
    const res = await fetch('https://calorie-tracker-xr.up.railway.app/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    console.log(data)
    if (res.ok) {
        alert('Register Success');
    } else {
        alert(data.error || 'Register failed');
    }
  };

  return (
    <div class="background">
        <div class="form">
            <form className="login-form">
                <h2 class="text login">Login</h2>
                <div class="fieldTable">
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Username"
                        required
                        class="field"
                    />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                        class="field"
                    />
                    <button class="submit" type="submit" onClick={handleLogin}>Log In</button>
                    <button class="register" onClick={handleRegister}>Register</button>

                </div>
               
                
            </form>
        </div>
        
    </div>
    
  );
};

export default Login;
