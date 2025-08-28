from src.payments.payment import PaymentCrud

def test_show_payments() -> None:
    """
    Test para verificar que se pueden mostrar los pagos correctamente.
    Se asume que ya existen pagos en la base de datos para este test.
    """
    payment_handler = PaymentCrud()
    
    # Casos de prueba con diferentes combinaciones de filtros
    test_cases = [
        # Caso 1: Filtros válidos - debería retornar 200
        {
            'serviceName': 'delegacion',
            'filters': {
                "CustomerFraction": ["cerritos", "centro", "garambullo", "yhonda"],
                "DIM_StatusId": True,
                "DIM_Date": 2025
            }
        },
        # Caso 2: Filtros válidos con CustomerFraction - debería retornar 200
# Este es un ejemplo de un objeto JSON que se enviaría como solicitud a la API
            {
                'serviceName': 'agua',           # Nombre del servicio a consultar (en este caso "agua")
                'filters': {                     # Objeto que contiene todos los filtros de búsqueda
                    "CustomerFraction": [        # Array de fracciones/colonias a filtrar
                        "cerritos",              # Incluir usuarios de la fracción Cerritos
                        "centro",                # Incluir usuarios de la fracción Centro  
                        "garambullo",            # Incluir usuarios de la fracción Garambullo
                        "yhonda"                 # Incluir usuarios de la fracción Yhonda
                    ],
                    "DIM_StatusId": True,        # Filtro por estado: True probablemente significa "activo" o "pendiente"
                    "DIM_Date": 2022           # Filtro por año: "Y22" probablemente representa el año 2022
                }
            },
        # Caso 3: Filtros mínimos - debería retornar 200
        # {
        #     'serviceName': 'agua',
        #     'filters': {
        #         "DIM_Date": "Y22"
        #     }
        # },
        # Caso 4: Filtro inválido (serviceName faltante) - debería retornar 400
        {
            'filters': {
                "DIM_Date": 2021
            }
        },
        # Caso 5: Filtro inválido (filters faltante) - debería retornar 400
        {
            'serviceName': 'agua'
        },
        # Caso 6: Filtro inválido (serviceName vacío) - debería retornar 400
        {
            'serviceName': '',
            'filters': {
                "DIM_Date": 2021
            }
        }
    ]
    
    expected_results = [200, 200, 400, 400, 400]
    
    for i, (test_case, expected_status) in enumerate(zip(test_cases, expected_results), 1):
        print(f"\n--- Ejecutando caso de prueba {i} ---")
        print(f"Filtros: {test_case}")
        
        status_code, mensaje, data = payment_handler.read_payments(test_case)
        
        print(f"Status Code: {status_code}")
        print(f"Mensaje: {mensaje}")
        print(f"Data: {data[:3]}")
        
        # Verificaciones
        assert status_code == expected_status, f"Caso {i}: Esperado {expected_status}, obtenido {status_code}"
        
        if expected_status == 200:
            assert isinstance(data, list), f"Caso {i}: Data debería ser una lista"
            # assert len(data) > 0, f"Caso {i}: Debería haber al menos un pago retornado"
        else:
            # Para casos de error, data debería ser None o lista vacía
            assert data is None or data == [] or (isinstance(data, list) and len(data) == 0), \
                f"Caso {i}: Para error 400, data debería ser None o vacía"

"""
    {
    "filters": {
        "CustomerFraction": ["cerritos", "centro", "garambullo", "yhonda"],
        "DIM_StatusId": True,
        "DIM_Date": "Y22"
    }, 
    "serviceName": "agua", 
    },


    {
        "filters": {
            "CustomerFraction": ["cerritos", "centro", "garambullo", "yhonda"],
            "DIM_StatusId": True,
            "DIM_Date": "Y22"
        },
        "serviceName": "agua"
    },


    {
        "filters": {
            "DIM_Date": "Y22"
        },
        "serviceName": "agua"
    },


    {
        "filters": {
            "CustomerFraction": ["cerritos"],
            "DIM_Date": "Y25", # Sebe cambiar year a DIM_Date
            "DIM_StatusId": True,

        },
        "serviceName": "agua"
    }


"""