import axios from "axios";

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api/analitycs_route/'
});


export const GetAnalytics = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data.comitiva || !data.mes || !data.usuario) {
            throw new Error('Faltan datos requeridos para obtener el monto');
        }
        console.log("Los datos llegaron correctamente a Api.js en getAmount", data);
        const response = await api.post('get_analytics/', data);

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }

        return response.data.body;

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


// FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA DASHBORAD CARD 9
// const chartData = {
//     labels: [
//       '12-01-2022', '01-01-2023', '02-01-2023',
//       '03-01-2023', '04-01-2023', '05-01-2023',
//     ],
//     datasets: [
//       // Light blue bars
//       {
//         label: 'Stack 1',
//         data: [
//           6200, 9200, 6600, 8800, 5200, 9200,
//         ],



// FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA DASHBORAD CARD 10
//   const chartData = {
//     labels: [
//       'Centro', 'Yhonda', 'garambullo', 'Buenavista', 'tepetate', 'cerritos',
//     ],
//     datasets: [
//       // Light blue bars
//       {
//         label: 'Stack 1',
//         data: [
//           6200, 9200, 6600, 8800, 5200, 9200,
//         ],
//         backgroundColor: getCssVariable('--color-violet-500'),
//         hoverBackgroundColor: getCssVariable('--color-violet-600'),
//         barPercentage: 0.7,
//         categoryPercentage: 0.7,
//         borderRadius: 4,
//       },
//     ],
//   };

// [
//     { manzana: 'Centro', ingresos: 12500 },
//     { manzana: 'Yhonda', ingresos: 9800 },
//     // ...
//   ]


// FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA DASHBORAD CARD 10
// {
//     "manzanas": [
//       {
//         "id": 1,
//         "nombre": "Centro",
//         "personas": 185,
//         "pagados": 142,
//         "pendientes": 43,
//         "porcentaje": 76.8,
//         "color": "#24292E"
//       },
//       {
//         "id": 2,
//         "nombre": "Tepetetate",
//         "personas": 156,
//         "pagados": 98,
//         "pendientes": 58,
//         "porcentaje": 62.8,
//         "color": "#1877F2"
//       },
//       {
//         "id": 3,
//         "nombre": "Yhonda",
//         "personas": 143,
//         "pagados": 115,
//         "pendientes": 28,
//         "porcentaje": 80.4,
//         "color": "#EA4335"
//       },
//       {
//         "id": 4,
//         "nombre": "Buenavista",
//         "personas": 127,
//         "pagados": 89,
//         "pendientes": 38,
//         "porcentaje": 70.1,
//         "color": "#4BC9FF"
//       },
//       {
//         "id": 5,
//         "nombre": "Garambullo",
//         "personas": 134,
//         "pagados": 78,
//         "pendientes": 56,
//         "porcentaje": 58.2,
//         "color": "#0E2439"
//       },
//       {
//         "id": 6,
//         "nombre": "Cerritos",
//         "personas": 118,
//         "pagados": 92,
//         "pendientes": 26,
//         "porcentaje": 78.0,
//         "color": "#28A745"
//       }
//     ]
//   }



//FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA DASHBORAD CARD 10
// {
//     "manzanas": [
//       {
//         "nombre": "Centro",
//         "personas": 185
//       },
//       {
//         "nombre": "Tepetetate",
//         "personas": 156
//       },
//       {
//         "nombre": "Yhonda",
//         "personas": 143
//       },
//       {
//         "nombre": "Buenavista",
//         "personas": 127
//       },
//       {
//         "nombre": "Garambullo",
//         "personas": 134
//       },
//       {
//         "nombre": "Cerritos",
//         "personas": 118
//       }
//     ]
//   }


//FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA analityis card11
// {
//     "administradores": [
//       {
//         "id": 1,
//         "nombre": "Monserrat",
//         "apellidos": "Lopez Rubio",
//         "comitiva": "agua",
//         "fechaInicio": "2025-01-01",
//         "fechaFin": "2025-12-31"
//       },
//       {
//         "id": 2,
//         "nombre": "Carlos",
//         "apellidos": "Martinez Gonzalez",
//         "comitiva": "luz",
//         "fechaInicio": "2025-02-15",
//         "fechaFin": "2025-11-30"
//       },
//       {
//         "id": 3,
//         "nombre": "Ana",
//         "apellidos": "Rodriguez Sanchez",
//         "comitiva": "agua",
//         "fechaInicio": "2025-03-01",
//         "fechaFin": "2025-10-31"
//       },
//       {
//         "id": 4,
//         "nombre": "Luis",
//         "apellidos": "Hernandez Morales",
//         "comitiva": "seguridad",
//         "fechaInicio": "2025-01-15",
//         "fechaFin": "2025-12-15"
//       }
//     ]
//   }