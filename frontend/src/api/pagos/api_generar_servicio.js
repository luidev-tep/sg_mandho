import axiosInstance from "./axiosInstance";

// Función para generar servicio - Completamente funcional

//api
export const generarServicio = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data || !data.serviceDetailesType || !data.amount || !data.year || !data.ServiceName) {
            throw new Error('Faltan datos requeridos: ServiceDetailesType, amount y Year son obligatorios');
        }

        // Validar que amount sea un número positivo
        if (typeof data.amount !== 'number' || data.amount <= 0) {
            throw new Error('El amount debe ser un número positivo');
        }

        // Validar que Year sea un número válido
        if (typeof data.year !== 'number' || data.year < 2000 || data.year > 2100) {
            throw new Error('El Year debe ser un número válido entre 2000 y 2100');
        }

        console.log("Datos enviados a generarServicio:", data);
        const response = await axiosInstance.post('payment/generar_servicio/', data);

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }

        console.log('Servicio generado exitosamente:', response.data);
        return response.data;

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
}
