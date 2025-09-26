import axios from 'axios';

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
        const tokens = JSON.parse(tokensString);

        // 4. Si el accessToken existe, añadirlo a la cabecera
        if (tokens?.tokens?.access_token) {
          config.headers['Authorization'] = `Bearer ${tokens.tokens.access_token}`;
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

export default axiosInstance;