import axios from "axios";


const api = axios.create({   
        baseURL: 'http://127.0.0.1:5000/api/security/'
    });

export const validatePassword = async (data) => {
    try {
        // Validar que password sea una cadena no vacía
        if (typeof data.password !== 'string' || data.password.trim() === '') {
            throw new Error('El password debe ser una cadena de texto válida');
        }


        console.log("Datos validados para validatePassword:", data);
        
        const response = await api.post('validate_password/', data, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibió respuesta del servidor');
        }

        console.log("Respuesta de validación de password recibida:", response.data);
        return response.data.body;

    } catch (error) {
        let errorMessage;

        if (error.response) {
            // El servidor respondió con un status fuera del rango 2xx
            console.error("Error de respuesta:", error.response.data);
            errorMessage = error.response.data?.message || 
                          error.response.data?.error || 
                          `Error ${error.response.status}: ${error.response.statusText}`;
        } else if (error.request) {
            // La petición fue hecha pero no se recibió respuesta
            errorMessage = 'No se recibió respuesta del servidor';
        } else {
            // Error en la configuración de la petición
            errorMessage = error.message || 'Error al configurar la petición';
        }
        
        throw new Error(errorMessage);
    }
};