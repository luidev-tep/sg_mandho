//src/api/pagos/api_crear_pago.js
import axios from "axios";

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api/payment/'
});

export const crearRegistroPago = async (data) => {
    try {
        // Si 'data' es un array y está vacío, no hacemos la petición.
        if (Array.isArray(data) && data.length === 0) {
            return { success: true, message: "No hay registros para crear.", data: [] };
        }

        // El backend ahora maneja tanto un objeto como una lista,
        // así que enviamos 'data' directamente.
        console.log("Payload enviado a api/payment/create:", data);
        const response = await api.post('create/', data);
        
        console.log("Respuesta del servidor al crear pago(s):", response.data);
        
        return {
            success: response.data.status || false,
            message: response.data.message ,
            data: response.data.body
        };
        
    } catch (error) {
        // Manejo mejorado de errores
        let errorMessage = 'Error desconocido al crear el pago';
        
        if (error.response) {
            // El servidor respondió con un status fuera del rango 2xx
            console.error("Error de respuesta:", error.response.data);
            errorMessage = error.response.data?.message || 
                          error.response.data?.error || 
                          `Error ${error.response.status}: ${error.response.statusText}`;
        } else if (error.request) {
            // La petición fue hecha pero no se recibió respuesta
            console.error("No se recibió respuesta:", error.request);
            errorMessage = 'No se recibió respuesta del servidor';
        } else {
            // Algo pasó en la configuración de la petición
            console.error("Error de configuración:", error.message);
            errorMessage = error.message || 'Error al configurar la petición';
        }
        
        throw new Error(errorMessage);
    }
};
