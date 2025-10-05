// partials/customers/CustomersTable.jsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import DynamicTableItem from './DynamicTableItem';
import ServiciosElegiblesDropdown from './ServiciosElegiblesDropdown';
import { MostrarPagos } from '../../../api/pagos/api_mostrar_pago';
import CorteCajaModal from './CorteCajaModal';
import { useAuth } from '../../../utils/AuthContext';

function DynamicTable({ filters, serviceName }) {
  const [selectAll, setSelectAll] = useState(false);
  const [isCheck, setIsCheck] = useState([]);
  const [allCustomers, setAllCustomers] = useState([]);
  const [serviciosValidos, setServiciosValidos] = useState(null);
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const tableRef = useRef(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCorteCajaModalOpen, setIsCorteCajaModalOpen] = useState(false);
  const { state } = useAuth();
  const userRole = state.usuario?.RoleName?.toLowerCase();

  const fetchCustomers = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      //Verificar si es funcional
      const backendFilters = {};
      
      // Mapear filtros de zona
      const CustomerFraction = [];
      if (filters.cerritos) CustomerFraction.push('cerritos');
      if (filters.centro) CustomerFraction.push('centro');
      if (filters.garambullo) CustomerFraction.push('garambullo');
      if (filters.yhonda) CustomerFraction.push('yhonda');
      if (filters.tepetate) CustomerFraction.push('tepetate');
      if (filters.buenavista) CustomerFraction.push('buenavista');
      
      if (CustomerFraction.length > 0) {
        backendFilters.CustomerFraction = CustomerFraction;
      }
      
      // Mapear filtros de fecha - Buscar clave que coincida con año numérico
      Object.keys(filters).forEach(key => {
        // Verificar si la clave es un número de 4 dígitos (año)
        if (/^\d{4}$/.test(key)) {
          backendFilters.DIM_Date = parseInt(key); // Convertir a número
        }
      });

      // MODIFICACIÓN: Siempre enviar año por defecto (actual) si no se especificó uno
      if (backendFilters.DIM_Date === undefined) {
        backendFilters.DIM_Date = new Date().getFullYear();
      }

      // MODIFICACIÓN: Filtro de inactivos - cambiar de 'inactivo' a 'pendiente'
      if (filters.pendiente) {
        backendFilters.DIM_StatusId = true;
      }

      const response = await MostrarPagos({
        'serviceName': serviceName,
        'filters': backendFilters
      });
      
      //console.log('✅ Pagos cargados con éxito.', response.data);

      // Extraer los datos de servicios válidos si existen
      const lastItem = response.data[response.data.length - 1];
      if (lastItem && lastItem.servicios_validos) {
        // Separar servicios y usuarios del array servicios_validos
        const servicios = lastItem.servicios_validos[0]; // Array de tipos de servicio ['faena', 'cooperacion']
        const usuarios = lastItem.servicios_validos[1]; // Array de objetos de usuarios
        
        setServiciosValidos({ 
          servicios: servicios, 
          usuarios: usuarios 
        });
        
        // Excluir este objeto especial de la lista de clientes a renderizar
        const customerData = response.data.slice(0, -1);
        setAllCustomers(customerData);
        setFilteredCustomers(customerData);
      } else {
        setAllCustomers(response.data);
        setFilteredCustomers(response.data);
        setServiciosValidos(null); // Resetear si no vienen datos
      }
    } catch (err) {
      setError(err.message || "Error al cargar pagos");
      console.error("❌ Error al cargar pagos:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Cargar datos iniciales
  useEffect(() => {
    fetchCustomers();
  }, [filters, serviceName]);

  // Escuchar eventos de búsqueda global
  useEffect(() => {
    const handleGlobalSearch = (event) => {
      setSearchTerm(event.detail.toLowerCase());
    };

    window.addEventListener('globalSearch', handleGlobalSearch);
    
    return () => {
      window.removeEventListener('globalSearch', handleGlobalSearch);
    };
  }, []);

  // Filtrar y resaltar resultados
  useEffect(() => {
    if (!tableRef.current) return;

    // 1. Filtrar pagos
    let filtered = allCustomers;
    if (searchTerm.length >= 3) {
      filtered = allCustomers.filter(customer => {
        const searchFields = [
          customer.CustomerName,
          customer.CustomerMiddleName,
          customer.CustomerLastName,
          customer.CustomerSecondLastName,
          customer.StatusFactura,
          customer.StatusCuenta,
          customer.ServiceDetailesType,
        ].filter(Boolean).join(' ').toLowerCase();

        return searchFields.includes(searchTerm);
      });
    }
    setFilteredCustomers(filtered);

  }, [searchTerm, allCustomers]);

  // Función para crear una clave única para cada registro de pago
  const getUniqueKey = (record) => {
    const key = `${record.DIM_AccountId}-${record.ServiceDetailesType || 'default'}`;
    return key;
  };
  const handleUpdateRecord = (updatedRecord) => {
    const updatedKey = getUniqueKey(updatedRecord);
  
    const updateFunction = (prevList) =>
      prevList.map(record => {
        const currentKey = getUniqueKey(record);
        if (currentKey === updatedKey) {
          return { ...record, ...updatedRecord };
        }
        return record;
      });
  
    setAllCustomers(updateFunction);
    setFilteredCustomers(updateFunction);
  }; 
  
  const handleClick = (e) => {
    const { id, checked, dataset } = e.target;
    const serviceType = dataset.serviceType || 'default';
    
    // Crear clave única combinando ID y tipo de servicio
    const uniqueId = `${id}-${serviceType}`;
    
    setSelectAll(false);
    
    if (checked) {
      setIsCheck([...isCheck, uniqueId]);
    } else {
      setIsCheck(isCheck.filter(item => item !== uniqueId));
    }
  };

  // Obtener tipos de servicio únicos de los resultados filtrados
  const uniqueServiceDetailTypes = useMemo(() => {
    const types = new Set(filteredCustomers.map(c => c.ServiceDetailesType).filter(Boolean));
    return Array.from(types);
  }, [filteredCustomers]);


  if (isLoading) return <div className="p-4 text-center">Cargando pagos...</div>;
  if (error) return <div className="p-4 text-center text-red-500">Error: {error}</div>;

  return (
    <div ref={tableRef} className="bg-transparent">
      <header className="px-5 py-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex-grow">
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">
              Total de Pagos {serviceName} <span className="text-gray-400 dark:text-gray-500 font-medium">{filteredCustomers.length}</span>
            </h2>
          </div>
          {userRole !== 'delegado' && (
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <ServiciosElegiblesDropdown 
                serviciosValidos={serviciosValidos} 
                serviceName={serviceName} 
                onSuccess={fetchCustomers} // Pasar la función para recargar
              />
              {/* El botón "Finalizar Servicio" solo se muestra si el servicio no es 'agua' ni 'delegacion' */}
              {serviceName !== 'agua' && serviceName !== 'delegacion' && (
                <button 
                  onClick={() => setIsCorteCajaModalOpen(true)}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-gray-800 hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600 border border-transparent rounded-lg shadow-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-gray-400 dark:focus:ring-offset-gray-800"
                >
                  <svg className="w-4 h-4 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  <span className="whitespace-nowrap">Finalizar Servicio</span>
                </button>
              )}
            </div>
          )}
        </div>
      </header>
      <div className="w-full">
        {/* Encabezado de la tabla */}
        <div className="hidden md:grid md:grid-cols-8 md:gap-4 bg-gray-50 dark:bg-gray-700/50 font-semibold text-xs uppercase text-gray-500 dark:text-gray-400 p-2 rounded-t-lg border-b border-gray-200 dark:border-gray-700">
          <div className="text-center">Imagen</div>
          <div className="col-span-2">Nombre</div>
          <div className="text-center">Rol</div>
          <div className="text-center">Estado</div>
          <div className="text-center">Servicio</div>
          <div className="text-center">Monto</div>
          <div className="grid grid-cols-2 items-center">
              <div className="text-center">Fecha</div>
              <div className="text-center">Acciones</div>
          </div>
        </div>

        {/* Cuerpo de la tabla con padding inferior para el menú de acciones */}
        <div className="space-y-2 md:space-y-0 pb-24">
          {filteredCustomers.map(customer => {
            // Crear clave única combinando ID de cuenta y tipo de servicio
            const uniqueKey = getUniqueKey(customer);
            
            return (
              <DynamicTableItem
                key={uniqueKey}
                id={customer.DIM_AccountId}
                image={customer.image}
                full_name={`${customer.CustomerName} ${customer.CustomerMiddleName || ''} ${customer.CustomerLastName} ${customer.CustomerSecondLastName || ''}`}
                role_name={customer.RoleName}
                status_factura={customer.StatusFactura}
                service_type={customer.ServiceDetailesType || 'N/A'}
                amount={customer.amount}
                status_account={customer.StatusCuenta}
                dim_date={customer.YearPay}
                handleClick={handleClick}
                service_name ={serviceName}
                dim_customer_id={customer.DIM_CustomerId}
                isChecked={isCheck.includes(uniqueKey)}
                onEditSuccess={handleUpdateRecord}
              />
            );
          })}
        </div>
      </div>
      {userRole !== 'delegado' && isCorteCajaModalOpen && (
        <CorteCajaModal
          serviceName={serviceName}
          serviceDetailTypes={uniqueServiceDetailTypes}
          onClose={() => setIsCorteCajaModalOpen(false)}
          onSuccess={fetchCustomers} // Recargar datos si el corte es exitoso
        />
      )}
    </div>
  );
}

export default DynamicTable;