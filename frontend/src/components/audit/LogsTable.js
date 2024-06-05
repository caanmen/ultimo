import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import './LogsTable.css'; // Suponiendo que tienes un archivo CSS para estilos

const LogsTable = () => {
    const [logs, setLogs] = useState([]);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetch('http://localhost:3200/logs')
            .then(response => response.json())
            .then(data => {
                console.log("data",data);
                if (data.status === 'success') {
                    setLogs(data.data);
                } else {
                    setError(data.message);
                }
            })
            .catch(error => setError('Error fetching logs'));
    }, []);

    const handleBack = () => {
        navigate('/items');
    };

    return (
        <div className="logs-table-container">
            <div className="header-icons">
                <FontAwesomeIcon icon={faArrowLeft} className="icon" onClick={handleBack} />
            </div>
            <h2>Registro de Logs</h2>
            {error && <div className="error-message">{error}</div>}
            <table className="logs-table">
                <thead>
                    <tr>
                        <th>Acción Realizada</th>
                        <th>Fecha y Hora</th>
                        <th>Usuario Responsable</th>
                        <th>Detalle</th>
                        <th>Tabla Afectada</th>
                    </tr>
                </thead>
                <tbody>
                    {logs.map((log, index) => (
                        <tr key={index}>
                            <td>{log.accion_realizada}</td>
                            <td>{new Date(log.fecha_hora).toLocaleString()}</td>
                            <td>{log.usuario_responsable_correo}</td>
                            <td>{log.detalle}</td>
                            <td>{log.tabla_afectada}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default LogsTable;
