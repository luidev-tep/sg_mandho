import axios from 'axios';
import { RefrescarToken } from './api_auth';
import { AuthProvider } from '../utils/AuthContext';

// 1. Crear la instancia de Axios
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:5000/api/', // URL base de tu API
});

// 2. Crear un interceptor de peticiones
axiosInstance.interceptors.request.use(
  (config) => {
    // 1. Recuperar la cadena de texto JSON de localStorage
    const tokensString = localStorage.getItem('tokens');

    if (tokensString) {
      try {
        // 2. Parsear la cadena para convertirla en un objeto
        const storedData = JSON.parse(tokensString);

        // 4. Si el accessToken existe, añadirlo a la cabecera
        if (storedData?.tokens?.access_token) {
          config.headers['Authorization'] = `Bearer ${storedData.tokens.access_token}`;
        }
      } catch (error) {
        console.error("Error al parsear los tokens desde localStorage:", error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Crear un interceptor de respuestas para manejar tokens expirados
export const setupInterceptors = (store) => {
  axiosInstance.interceptors.response.use(
    (response) => response, // Si la respuesta es exitosa, la devuelve sin más.
    async (error) => {
        const originalRequest = error.config;
        
        // Si el error es 401 (No autorizado) y no hemos reintentado ya esta petición
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true; // Marcamos la petición para evitar bucles infinitos
            
            // Obtenemos el estado actual para acceder al refresh token
            const tokensString = localStorage.getItem('tokens');
            if (!tokensString) {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(error);
            }
            const storedData = JSON.parse(tokensString);
            const refreshToken = storedData?.tokens?.refresh_token;

            if (!refreshToken) {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(error);
            }

            try {
                // Intentamos refrescar el token, pasándole el refresh token
                const newAccessToken = await RefrescarToken(refreshToken);
                
                // Actualizamos los tokens en el estado global
                const newTokens = { ...storedData.tokens, access_token: newAccessToken };
                store.dispatch({ type: 'SET_TOKENS', payload: newTokens });

                // Reintentamos la petición original con el nuevo token
                // El interceptor de peticiones se encargará de añadir el nuevo token
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                // Si el refresco falla (ej. refresh token también expiró), cerramos sesión.
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error); // Para cualquier otro error, lo propagamos
    }
  );
};

export default axiosInstance;