import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginComponent.css';

const LoginComponent = () => {
    const [correo, setCorreo] = useState('');
    const [contrasena, setContrasena] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Limpia el almacenamiento local al montar el componente
    useEffect(() => {
        localStorage.removeItem('role');
        localStorage.removeItem('user');
        localStorage.removeItem('correo');
    }, []);

    const handleLogin = (e) => {
        e.preventDefault();
        fetch('http://127.0.0.1:3200/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ correo, contrasena }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                setError(data.message); // Set the error message
                console.error('Error:', data.message);
            } else if(data.data.tipo_usuario && data.data.user && data.data.correo){
                setError(''); // Clear any previous error messages
                localStorage.setItem('role', data.data.tipo_usuario); // Almacena el rol del usuario
                localStorage.setItem('user', data.data.user); // Almacena el rol del usuario
                localStorage.setItem('correo', data.data.correo); // Almacena el rol del usuario
                navigate('/items');
            }else{
                setError('An error occurred while logging in. Please try again.');
            }
        })
        .catch((error) => {
            setError('An error occurred while logging in. Please try again.');
            console.error('Error:', error);
        });
    };

    const handleNavigateToRegister = () => {
        navigate('/register');
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <label htmlFor="correo">Email:</label>
                    <input
                        type="email"
                        id="correo"
                        value={correo}
                        onChange={(e) => setCorreo(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="contrasena">Password:</label>
                    <input
                        type="password"
                        id="contrasena"
                        value={contrasena}
                        onChange={(e) => setContrasena(e.target.value)}
                    />
                </div>
                <button type="submit">Login</button>
            </form>
            <button onClick={handleNavigateToRegister} className="navigate-button">
                Go to Register
            </button>
        </div>
    );
};

export default LoginComponent;
