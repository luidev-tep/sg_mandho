import axios from "axios";

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api/payment/'
});

export const MostrarPagos = async (data) => {
    try {
        // Validación de campos requeridos
        if (!data.serviceName) {
            throw new Error('Faltan campos requeridos para mostrar los pagos');
        }

        //console.log("Los datos llegaron correctamente a Api.js en MostrarPagos", data);
        const response = await api.post('read/', data);

        //console.log("Respuesta del servidor:", response.data);

        return {
            success: response.data.status || false,
            message: response.data.message,
            data: response.data.body || []
        }; // ← Aquí faltaba cerrar el return y agregar el punto y coma

    } catch (error) {
        let errorMessage; // ← Declarar la variable errorMessage

        if (error.response) {
            // El servidor respondió con un status fuera del rango 2xx
            console.error("Error de respuesta:", error.response.data);
            errorMessage = error.response.data?.message || 
                          error.response.data?.error || 
                          `Error ${error.response.status}: ${error.response.statusText}`;
        } else if (error.request) {
            // La petición fue hecha pero no se recibió respuesta
            //console.error("No se recibió respuesta:", error.request);
            errorMessage = 'No se recibió respuesta del servidor';
        } else {
            // Algo pasó en la configuración de la petición
            //console.error("Error de configuración:", error.message);
            errorMessage = error.message || 'Error al configurar la petición';
        }

        throw new Error(errorMessage);
    }
};
