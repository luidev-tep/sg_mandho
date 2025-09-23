import axios from "axios";

const api = axios.create({   
    baseURL: 'http://127.0.0.1:5000/api/security/'
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
        console.log("Datos recibidos del backend:", response.data.body);
        return { data: response.data.body.data,
            tokens: response.data.body.tokens // ← Tokens incluidos
         };
    } catch (error) {
        console.error("Error en la petición:", error);
        throw error; // Propaga el error para manejarlo en el componente
    }
}