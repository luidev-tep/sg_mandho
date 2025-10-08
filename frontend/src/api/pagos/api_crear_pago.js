//src/api/pagos/api_crear_pago.js
import axiosInstance from "./axiosInstance";

export const crearRegistroPago = async (data) => {
    try {
        // Si 'data' es un array y está vacío, no hacemos la petición.
        if (Array.isArray(data) && data.length === 0) {
            return { success: true, message: "No hay registros para crear.", data: [] };
        }

        // El backend ahora maneja tanto un objeto como una lista,
        // así que enviamos 'data' directamente.
        //console.log("Payload enviado a api/payment/create:", data);
        const response = await axiosInstance.post('payment/create/', data);
        
        //console.log("Respuesta del servidor al crear pago(s):", response.data);
        
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

export const CorteDeCaja = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data) {
            throw new Error('Faltan datos requeridos para generar el corte de caja');
        }

        //console.log("Datos enviados a CorteDeCaja:", data);
        const response = await axiosInstance.post('payment/cash_cut/', data);
        
        //console.log("Respuesta del servidor al crear corte de caja:", response.data);
        
        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }
        
        return {
            status: response.status, // Devolvemos el status HTTP
            success: response.data.status === 'success',
            message: response.data.message,
            data: response.data.body
        };
        
    } catch (error) {
        // Manejo mejorado de errores
        let errorMessage;
        
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
        
        // Retornamos el error en el formato esperado, sin lanzar excepción
        return {
            success: false,
            message: errorMessage,
            data: null,
            status: error.response?.status || 500
        };
    }
};