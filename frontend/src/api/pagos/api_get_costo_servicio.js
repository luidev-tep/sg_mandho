import axios from "axios";

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api/payment/'
});

export const GetCostoServicio = async (DIM_CustomerId, moduleName) => {
    try {
        // Validación de campos requeridos
        if (!DIM_CustomerId && !moduleName) {
            throw new Error('Faltan campos requeridos para mostrar los pagos');
        }

        const data = {
            DIM_CustomerId: DIM_CustomerId,
            moduleName: moduleName
        };

        //console.log("Los datos llegaron correctamente a Api.js en MostrarPagos", data);
        const response = await api.post('get_cost/', data);

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

export const getAmount = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data) {
            throw new Error('Faltan datos requeridos para obtener el monto');
        }
        //console.log("Los datos llegaron correctamente a Api.js en getAmount", data);
        const response = await api.post('get_any_data/', data);

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }

        // Extraer el amount de la respuesta
        const amount = parseFloat(response.data.body || response.data);

        // Validar que el amount sea un número válido
        if (isNaN(amount)) {
            throw new Error('El monto recibido no es un número válido');
        }

        return amount;

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



export const getPagosPendientes = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data || !data.pagosPendientes || !data.pagosPendientes.DIM_CustomerId || !data.pagosPendientes.ServiceName) {
            throw new Error('Faltan datos requeridos para obtener los pagos pendientes');
        }
        console.log("Datos enviados a getPAgosPendientes:", data);
        const response = await api.post('get_any_data/', data);

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data || !response.data.body) {
            throw new Error('No se recibieron datos del servidor');
        }

        // La respuesta es un JSON, no un número.
        const pendingPayments = response.data.body;
        console.log('Pagos pendientes recibidos de la API:', pendingPayments); // Log para verificar

        return {
            data: pendingPayments
        };

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