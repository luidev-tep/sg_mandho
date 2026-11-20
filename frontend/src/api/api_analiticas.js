import axiosInstance from "./axiosInstance";


export const GetAnalytics = async (data) => {
    try {
        // Validación de datos requeridos
        if (!data.comitiva || !data.mes || !data.anio) {
            throw new Error('Faltan datos requeridos para obtener los datos analíticos');
        }
                // Convertir el año al formato 'Y25' (últimos 2 dígitos del año)
                const formattedYear = `Y${data.anio.slice(-2)}`;
                
                //console.log("Datos para la petición de analytics:", { ...data, anio: formattedYear });
                
                // Enviar los datos en el cuerpo de la petición POST
                const response = await axiosInstance.post('analitycs/get_analytics/', {
                    comitiva: data.comitiva,
                    mes: data.mes,
                    usuario: data.usuario,
                    anio: formattedYear, 
                });

        // Verificar si la respuesta tiene el formato esperado
        if (!response.data) {
            throw new Error('No se recibieron datos del servidor');
        }
        const data_response = {
            dataIncomes: response.data.body.dataIncomes,
            dataFractions: response.data.body.dataFractions,
            dataUserBills: response.data.body.dataUserBills,
            dataCountUsers: response.data.body.dataCountUsers,
            dataServiceMembers: response.data.body.dataServiceMembers
        }
        //console.log("Datos recibidos en la respuesta:", data_response);
        return data_response;

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
//     // ...
//   ]


// FORMATO EN QUE SE DEBE REGRESAR LA INFORMACION PARA DASHBORAD CARD 10
// {
//     "manzanas": [
//       {
//         "id": 3,
//         "personas": 143,
//         "pagados": 115,
//         "pendientes": 28,
//         "porcentaje": 80.4,
//         "color": "#EA4335"
//       },
//       {
//         "id": 4,
//         "personas": 127,
//         "pagados": 89,
//         "pendientes": 38,
//         "porcentaje": 70.1,
//         "color": "#4BC9FF"
//       },
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
//         "id": 4,
//         "nombre": "Luis",
//         "apellidos": "Hernandez Morales",
//         "comitiva": "seguridad",
//         "fechaInicio": "2025-01-15",
//         "fechaFin": "2025-12-15"
//       }
//     ]
//   }