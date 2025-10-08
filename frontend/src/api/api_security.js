import axiosInstance from "./axiosInstance";

export const validatePassword = async (data) => {
    try {
        // Validar que password sea una cadena no vacía
        if (typeof data.password !== 'string' || data.password.trim() === '') {
            throw new Error('El password debe ser una cadena de texto válida');
        }

        //console.log("Datos validados para validatePassword:", data);
        
        const response = await axiosInstance.post('security/validate_password/', data);
        
        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibió respuesta del servidor');
        }

        //console.log("Respuesta de validación de password recibida:", response.data);
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


// ESTA FUNCION SERVIRA PARA QUE SE VALIDE LA CONTRASENIA DEL USUARIO EN PETICIONES SENSIBLES, COMO LO PODRIA SER ELIMINAR A 
// PERSONA, O HACER UNA ACCION SENSIBLE EN PAGOS (COMO LO PODRIA SER AGREGAR A CIENTOS DE USUARIOS CON UN PAGO DE 0)
export const ValidatePasswordOnwer = async (data) => {
    try {
        // Validar que password sea una cadena no vacía
        if (typeof data.password !== 'string' || data.password.trim() === '') {
            throw new Error('El password debe ser una cadena de texto válida');
        }

        //console.log("Datos validados para ValidatePasswordOnwer:", data);
        
        const response = await axiosInstance.post('security/validate_password_service/', data);
        
        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibió respuesta del servidor');
        }

        //console.log("Respuesta de validación de password recibida:", response.data);
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