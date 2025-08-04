import React, { useState } from 'react';
import './Register.css'

const Register = ({ setToken , navigateLogin}) => {
    // const localRegister = 'http://localhost:5055/api/register'
    const prodRegister = 'https://calorie-tracker-xr.up.railway.app/api/register'

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const [calorie, setCalorie] = useState('');
    const [protein, setProtein] = useState('');
    const [carbs, setCarbs] = useState('');
    const [fat, setFat] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
    
        const res = await fetch(prodRegister, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, calorie, protein, carbs, fat }),
        });

        const data = await res.json();
        console.log(data)
        if (res.ok) {
            localStorage.setItem("token", data.access_token);
            setToken(data.access_token); // Save token in parent
            alert('Register Success');
            navigateLogin()
        } else {
            alert(data.error || 'Register failed');
        }
  };

  return (
    <div class="background">
        <div class="registerForm">
            <form className="register-form">
                <div class="text registerTitle">Register</div>
                <div class="registerFieldTable">
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Username"
                        required
                        class="registerField"
                    />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        required
                        class="registerField"
                    />

                    <div id="statBoxInput">
                        <div className='statBoxRow'>
                            <input
                                type="text"
                                value={calorie}
                                onChange={(e) => setCalorie(e.target.value)}
                                placeholder="Target Calorie"
                                required
                                class="statfield"
                            />
                            <input
                                type="text"
                                value={protein}
                                onChange={(e) => setProtein(e.target.value)}
                                placeholder="Target Protein"
                                required
                                class="statfield"
                            />
                        </div>
                        <div className='statBoxRow'>
                            <input
                                type="text"
                                value={carbs}
                                onChange={(e) => setCarbs(e.target.value)}
                                placeholder="Target Carbs"
                                required
                                class="statfield"/>
                            <input
                                type="text"
                                value={fat}
                                onChange={(e) => setFat(e.target.value)}
                                placeholder="Target Fat"
                                required
                            class="statfield"/>
                        </div>
                    </div>

                    <button class="submit" type="submit" onClick={handleRegister}>Register</button>
                    <button class="register" onClick={() => navigateLogin()}>Log in</button>

                </div>
               
                
            </form>
        </div>
        
    </div>
    
  );
};

export default Register;
