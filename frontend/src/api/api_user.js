import axiosInstance from "./axiosInstance";
import { validate_edit_account } from "./api_account";
import { crearCuenta } from "./api_account";
import { isValid } from "date-fns/isValid";
// Ya no se necesita una instancia local, usaremos la centralizada
// con el interceptor que inyecta el token de autorización.


/**
 * Los datos para el formulario de ususario deben de ir en este orden en el json
 * 
 * Solamente cuando se envian del frontend al backend
 * id de usuario: id_user
 * nombre: nombre
 * segundo nombre: segundo_nombre
 * apellido: apellido
 * segundo apellido: segundo_apellido
 * fecha de nacimiento: fecha_nacimiento
 * fecha de inicio: fecha_inicio
 * fecha de fin: fecha_fin
 * manzana: manzana
 * calle: calle
 * numero exterior: numero
 * 
 * Cuando se reciben del backend vendran en este formato
 * 
 * id de usuario: id_user
 * nombre: first_name`
 * segundo nombre: second_name
 * apellido: last_name
 * segundo apellido: second_last_name
 * fecha de nacimiento: date_of_birth
 * fecha de inicio: date_user_start
 * fecha de fin: date_user_end
 * manzana: user_manzana
 * calle: user_street
 * numero exterior: user_number_ext
 * 
 * **/

/**
 * Agrega un nuevo usuario a la base de datos.
 * 
 * @param {object} data - Objeto con los datos del usuario a agregar.
 * @returns {Promise<AxiosResponse>} - Promesa que se resuelve con la respuesta del backend (si todo sale bien).
 * @throws {Error} - Si el backend devuelve un status code fuera del rango 2xx o si el formato de la respuesta no es el esperado.
 */
export const AgregarUsuario = async (data) => { 
    try {
        console.log("AgregarUsuario Hola desde api_user.js");
        console.log("Data recibida en AgregarUsuario:", data);
        
        // 1. Crear el usuario primero - AGREGANDO HEADERS COMO EN MostrarUsuarios
        const userResponse = await axiosInstance.post('user/create_user/', data, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (!userResponse.data) {
            throw new Error('No se recibieron datos del backend');
        }

        if (userResponse.data.status !== 'success') {
            throw new Error(userResponse.data?.message || 'Error al crear el usuario');
        }
        
        // Obtener ID del usuario creado
        const userId = userResponse.data.body.id;
        if (!userId) {
            throw new Error('No se recibió ID de usuario del backend');
        }

        // 2. Preparar y crear la cuenta asociada
        const accountPayload = {
            customer_id: userId,
            start_date: data.data.fecha_inicio, // Acceder a data.data ya que el payload está anidado
            end_date: data.data.fecha_fin,
            status: data.data.estadoPersona.toLowerCase(),
        };

        console.log('Información para crear la cuenta:', accountPayload);
        
        // Crear la cuenta asociada
        const accountResponse = await crearCuenta(accountPayload);
        console.log("Respuesta de creación de cuenta:", accountResponse);

        // 3. Verificar que ambas operaciones fueron exitosas (ajustado a estructura real)
        if (userResponse.data.status === 'success' && (accountResponse.success || accountResponse.data?.status === 'success')) {
            return { id: userId };
        } else {
            throw new Error(accountResponse.message || 'Error en la creación de la cuenta asociada');
        }
    } catch (error) {
        console.error("Error en AgregarUsuario:", error);
        
        // Priorizamos el mensaje del backend si está disponible - COMO EN MostrarUsuarios
        const errorMessage = error.response?.data?.message 
            || error.message 
            || 'Error al crear el usuario';
        
        throw new Error(errorMessage);
    }
}


/**
 * Realiza una petición GET a la API para obtener la lista de usuarios.
 * 
 * @returns {Promise<AxiosResponse>} - Promesa que se resuelve con la respuesta del backend, conteniendo los datos de los usuarios.
 * @throws {Error} - Si ocurre un error durante la petición HTTP.
 */

export const MostrarUsuarios = (data) => {
    // console.log("MostrarUsuarios Hola desde api_user.js");
    // console.log("Data recibida en MostrarUsuarios:", data);
    return axiosInstance.post('user/read_user/', data, {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.data) {
            throw new Error('No se recibieron datos del backend');
        }

        if (response.data.status === 'success') {
            return {
                data: response.data.body,
                success: true
            };
        } else {
            // Usamos el mensaje del backend si existe
            throw new Error(response.data.message || 'Respuesta inesperada del backend');
        }
    })
    .catch(error => {
        console.error("Error en MostrarUsuarios:", error);
        
        // Priorizamos el mensaje del backend si está disponible
        const errorMessage = error.response?.data?.message 
            || error.message 
            || 'Error al cargar los usuarios';
        
        throw new Error(errorMessage);
    });
}


export const EditarUsuario = async (data) => {
    try {
        // Primero actualizar el usuario
        const updateResponse = await axiosInstance.post('user/update_user/', data, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (updateResponse.data.status !== 'success') {
            const errorMessage = updateResponse.data.message || 'Respuesta inesperada del backend al actualizar usuario';
            throw new Error(errorMessage);
        }

        // Si la actualización fue exitosa, ahora validar y crear cuenta si es necesario
        const data_account = {
            status: data.estadoPersona,
            customer_id: data.DIM_CustomerId,
            start_date: data.fechaCuenta,
            end_date: "",
            orginal_status: data.EstadoPersonaOriginal,
        };

        const shouldCreateAccount = await validate_edit_account(data_account);
        if (shouldCreateAccount) {
            console.log("Actualizando cuenta");
            await crearCuenta(data_account);
        } else {
            console.log("No se requiere actualización de cuenta");
        }
        console.log("Data de la cuenta", updateResponse.data.body);
        return {
            
            data: normalizeUserData(updateResponse.data.body),
            success: true
        };
    } catch (error) {
        console.error("Error en EditarUsuario:", {
            error: error,
            responseData: error.response?.data,
            status: error.response?.status
        });
        
        const backendMessage = error.response?.data?.message;
        const errorMessage = backendMessage || error.message || "Error al actualizar el usuario";
        
        return {
            success: false,
            message: errorMessage
        };
    }
}
// API.js
export const DesactivarUsuario = (DIM_CustomerId) => {
    if (!DIM_CustomerId) {
        
        return Promise.reject(new Error("ID de usuario no proporcionado"));
    }

    return axiosInstance.patch('user/delete_user/', {
        DIM_CustomerId: DIM_CustomerId
    }).then(response => {
        
        if (response.data.status === 'success') {
            
            const normalizedData = normalizeUserData(response.data.body);
            
            return {
                success: response.data.status,
                data: normalizedData
            };
        } else {
            throw new Error(response.data.message || 'Respuesta inesperada del backend');
        }
    }).catch(error => {
        console.error("[API] 5. Error en DesactivarUsuario:", {
            error: error,
            responseData: error.response?.data,
            status: error.response?.status
        });
        return {
            success: false,
            message: error.response?.data?.message || error.message
        };
    });
};

const normalizeUserData = (userData) => {
    return {
        id_user: userData.DIM_CustomerId,
        first_name: userData.CustomerName,
        second_name: userData.CustomerMiddleName || '',
        last_name: userData.CustomerLastName,
        second_last_name: userData.CustomerSecondLastName || '',
        date_of_birth: userData.CustomerDateBirth,
        date_user_start: userData.CustomerStartDate,
        date_user_end: userData.CustomerEndDate,
        manzana: userData.CustomerFraction,
        street: userData.CustomerAddress,
        number_ext: userData.CustomerNumberExt
    };
};

// API.js - Corrige la ruta en el frontend
export const GenerarReporteUsuario = (Dim_customerId) => {
    if (!Dim_customerId) {
        return Promise.reject(new Error("ID de usuario no proporcionado"));
    }

    return axiosInstance.get('user/gat_data/', {  // Cambiado de 'get_data/' a 'gat_data/'
        params: {
            Dim_customerId: Dim_customerId
        }
    }).then(response => {
        if (response.data.status === 'success') {
            const normalizedData = response.data.body;
            return {
                success: response.data.status,
                data: normalizedData
            };
        } else {
            throw new Error(response.data.message || 'Respuesta inesperada del backend');
        }
    }).catch(error => {
        console.error("[API] Error en GenerarReporteUsuario:", {
            error: error,
            responseData: error.response?.data,
            status: error.response?.status
        });
        return {
            success: false,
            message: error.response?.data?.message || error.message
        };
    });
};

export const MostrarAdmin = () => {
    console.log("MostrarAdmin Hola dese aqui el admin");
    console.log("Esta api aun no es funcional");
    const items = [
    // La informacion proveniente del backend deberia venir en este formato
    [
      {
        id: 0,
        name: 'Carlos Martínez',
        role: 'delegado',
        details: 'buenavista Av.20 noviembre s/n',
        date: '2025-05-01',
      },
    ],
    // Grupo 2 (Subdelegados) - 1 por manzana (6 en total)
    [
      {
        id: 2,
        name: 'Pedro Sánchez',
        role: 'subdelegado',
        details: 'tepetate Av.20 noviembre s/n',
        date: '2025-05-01',
      },
    ],
    // Grupo 3 (Comotivas personal) - 5 en total
    [
      {
        id: 7,
        name: 'Sofía Mendoza',
        role: 'comotiva',
        details: 'buenavista Av.20 noviembre s/n',
        date: '2025-05-01',
      },
    ],
  ];

  return items;
};