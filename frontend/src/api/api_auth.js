import axios from "axios";
const api = axios.create({
    baseURL: `${(import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')}/security/`,
    timeout: 30000,
});

/**
 * Esta función obtiene los datos del usuario desde el backend.
 * @param {Object} userData - Los datos del usuario para el login.
 * @param {string} userData.username - El nombre de usuario
 * @param {string} userData.password - La contraseña
 * @param {string} userData.RoleName - El rol del usuario
 * @param {string} userData.manzana - La manzana/fracción
 * @param {string} userData.recaptcha - Token de reCAPTCHA
 * @returns {Promise<Object>} - Una promesa que resuelve con los datos del usuario.
 */
export const ObtenerUsuario = async (userData) => {
    // console.log("Datos enviados al backend:", userData);
    // console.log("Obteniendo datos del usuario...");
    
    try {
        const response = await api.post(`login/`, userData, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        return { data: response.data.body.data,
            tokens: response.data.body.tokens // ← Tokens incluidos
         };
    } catch (error) {
        console.error("Error en la petición:", error);
        throw error; // Propaga el error para manejarlo en el componente
    }
}
  
/**
 * Función simplificada para refrescar el token.
 * Solo realiza la llamada a la API y devuelve el nuevo access_token.
 * @param {string} refreshToken - El token de refresco a utilizar.
 * @returns {Promise<string>} - Una promesa que resuelve con el nuevo access_token.
 */
export const RefrescarToken = async (refreshToken) => {
    try {
        if (!refreshToken) throw new Error('No se proporcionó un refresh token');

        const response = await api.post('refresh_token/', {}, {
            headers: {
                'Authorization': `Bearer ${refreshToken}`,
            }
        });
        
        // Devuelve solo el nuevo token de acceso
        return response.data.body.data;

    } catch (error) {
        console.error("Error al refrescar token:", error.response?.data || error.message);
        throw error;
    }
}