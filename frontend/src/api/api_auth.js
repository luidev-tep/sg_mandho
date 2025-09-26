import axios from "axios";
//Se improta para poder enviar los tojkens adecuadamente
import axiosInstance from "./axiosInstance";

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


//Función unificada para refrescar token
export const RefrescarToken  = async () => {
  try {
    const tokensString = localStorage.getItem('tokens');
    if (!tokensString) throw new Error('No hay tokens disponibles');
    
    // Parseamos el objeto completo desde localStorage
    const storedData = JSON.parse(tokensString);
    console.log(storedData);
    const tokens = storedData.tokens;


    if (!tokens || !tokens.refresh_token) throw new Error('No hay refresh token');
    
    // Usamos una instancia de Axios separada para evitar dependencias circulares con el interceptor
    const response = await axios.post('http://127.0.0.1:5000/api/security/refresh_token/', {}, {
        headers: {
            'Authorization': `Bearer ${tokens.refresh_token}`
        }
    });

    // Actualizamos el access_token en nuestro objeto de tokens
    storedData.tokens.access_token = response.data.body.data;

    // Guardamos el objeto completo actualizado en localStorage
    localStorage.setItem('tokens', JSON.stringify(storedData));

    return storedData.tokens;
  } catch (error) {
      console.error("Error al refrescar token:", error);
      throw error;
  }
}

// Renovación automática cada 15 minutos
let tokenRefreshInterval = null;

export const iniciarRenovacionAutomatica = () => {
  if (tokenRefreshInterval) clearInterval(tokenRefreshInterval);
  
  tokenRefreshInterval = setInterval(async () => {
      try {
          await RefrescarToken();
          console.log('Token renovado automáticamente');
      } catch (error) {
          console.error('Error en renovación automática:', error);
      }
  }, 900000); // 15 minutos
};

export const detenerRenovacionAutomatica = () => {
  if (tokenRefreshInterval) {
      clearInterval(tokenRefreshInterval);
      tokenRefreshInterval = null;
  }
};