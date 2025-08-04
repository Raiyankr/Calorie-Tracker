import React, { useState } from 'react';
import './Login.css'

const Login = ({ setToken, navigateRegister}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    // const localLogin = 'http://localhost:5055/api/login'
    const prodLogin = 'https://calorie-tracker-xr.up.railway.app/api/login'

    const res = await fetch(prodLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (res.ok) {
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token); // Save token in parent
    } else {
        alert(data.error || 'Login failed');
    }
  };

  return (
    <div class="background">
        <div class="form">
            <form className="login-form">
                <div class="text login">Log in</div>
                <div class="loginFieldTable">
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Username"
                        required
                        class="loginField"
                    />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                        class="loginField"
                    />
                    <button class="submit" type="submit" onClick={handleLogin}>Log In</button>
                    <button class="register" onClick={() => navigateRegister()}>Register</button>

                </div>
               
                
            </form>
        </div>
        
    </div>
    
  );
};

export default Login;
