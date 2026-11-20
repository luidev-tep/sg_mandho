import axios from 'axios';
import { RefrescarToken } from './api_auth';

// 1. Crear la instancia de Axios
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // URL base de tu API desde .env
  timeout: 30000,
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

let refreshPromise = null;

// 3. Crear un interceptor de respuestas para manejar tokens expirados
export const setupInterceptors = (store) => {
  const interceptorId = axiosInstance.interceptors.response.use(
    (response) => response, // Si la respuesta es exitosa, la devuelve sin más.
    async (error) => {
        const originalRequest = error.config;
        
        // Si el error es 401 (No autorizado) y no hemos reintentado ya esta petición
        if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
            originalRequest._retry = true; // Marcamos la petición para evitar bucles infinitos
            
            const tokensString = localStorage.getItem('tokens');
            if (!tokensString) {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(error);
            }

            let storedData = null;
            try {
                storedData = JSON.parse(tokensString);
            } catch {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(error);
            }

            const refreshToken = storedData?.tokens?.refresh_token;
            if (!refreshToken) {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(error);
            }

            try {
                if (!refreshPromise) {
                    refreshPromise = RefrescarToken(refreshToken).finally(() => {
                        refreshPromise = null;
                    });
                }
                const newAccessToken = await refreshPromise;

                const newTokens = { ...storedData.tokens, access_token: newAccessToken };
                // Escribir síncronamente en localStorage antes del retry para que el request interceptor lea el token nuevo
                localStorage.setItem('tokens', JSON.stringify({
                    tokens: newTokens,
                    refreshTokenTimestamp: storedData.refreshTokenTimestamp || Date.now(),
                }));
                originalRequest.headers = originalRequest.headers || {};
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

                store.dispatch({ type: 'SET_TOKENS', payload: newTokens });
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                store.dispatch({ type: 'CLEAR_USER' });
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
  );

  return () => {
    axiosInstance.interceptors.response.eject(interceptorId);
  };
};

export default axiosInstance;