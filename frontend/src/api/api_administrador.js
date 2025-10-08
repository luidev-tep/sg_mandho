import axiosInstance from "./axiosInstance";

/**
 * Obtiene la lista de usuarios propietarios (administradores, delegados, etc.).
 * 
 * @returns {Promise<Object>} - Una promesa que resuelve con los datos de los propietarios.
 * @throws {Error} - Si ocurre un error durante la petición.
 */
export const getOwners = async (data) => {
    try {
        //console.log("Obteniendo lista de propietarios...");
        //console.log(data);
        // Se asume un endpoint 'admin/get_owners/' y que no requiere payload.
        const response = await axiosInstance.post('security/admin_onwer/', data);

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }

        if (response.data.status === 'success') {
            //console.log("Propietarios recibidos:", response.data.body);
            return {
                success: true,
                data: response.data.body || []
            };
        } else {
            throw new Error(response.data.message || 'Respuesta inesperada del servidor');
        }

    } catch (error) {
        let errorMessage;

        if (error.response) {
            console.error("Error de respuesta al obtener propietarios:", error.response.data);
            errorMessage = error.response.data?.message || 
                          error.response.data?.error || 
                          `Error ${error.response.status}: ${error.response.statusText}`;
        } else if (error.request) {
            errorMessage = 'No se recibió respuesta del servidor';
        } else {
            errorMessage = error.message || 'Error al configurar la petición para obtener propietarios';
        }
        
        throw new Error(errorMessage);
    }
};

/**
 * Envía los datos de un nuevo usuario para su creación en el backend.
 * 
 * @param {Object} userData - El payload con la información del nuevo usuario.
 * @returns {Promise<Object>} - Una promesa que resuelve con la respuesta del backend (solo mensaje).
 * @throws {Error} - Si ocurre un error durante la petición.
 */
export const createOwner = async (userData) => {
    try {
        if (!userData) {
            throw new Error('No se proporcionaron datos de usuario para la creación.');
        }

        //console.log("Enviando datos para crear nuevo propietario:", userData);
        // Se asume un endpoint 'admin/create_owner/'
        const response = await axiosInstance.post('security/admin_onwer/', userData);

        if (!response.data) {
            throw new Error('No se recibió respuesta del servidor');
        }

        //console.log("Respuesta del servidor:", response.data);
        return response.data; // Devuelve el objeto completo { success, message }

    } catch (error) {
        let errorMessage;

        if (error.response) {
            console.error("Error de respuesta al crear propietario:", error.response.data);
            errorMessage = error.response.data?.message || `Error ${error.response.status}`;
        } else if (error.request) {
            errorMessage = 'No se recibió respuesta del servidor';
        } else {
            errorMessage = error.message || 'Error al configurar la petición para crear propietario';
        }
        
        throw new Error(errorMessage);
    }
};