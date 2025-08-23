//Agua tabla
// partials/customers/CustomersTable.jsx
import React, { useState, useEffect, useRef } from 'react';
import Customer from './AguaTableItem';
import { MostrarPagos } from '../../../api/pagos/api_mostrar_pago';

function AguaTable({ filters }) {
  const [selectAll, setSelectAll] = useState(false);
  const [isCheck, setIsCheck] = useState([]);
  const [allCustomers, setAllCustomers] = useState([]);
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const tableRef = useRef(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Cargar datos iniciales
  useEffect(() => {
    const fetchCustomers = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
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
        
        // Mapear filtros de fecha
        Object.keys(filters).forEach(key => {
          if (key.startsWith('Y')) {
            backendFilters.DIM_Date = key;
          }
        });

        // MODIFICACIÓN: Filtro de inactivos - cambiar de 'inactivo' a 'pendiente'
        if (filters.pendiente) {
          backendFilters.DIM_StatusId = true;
        }

        const response = await MostrarPagos({
          'serviceName': "agua",
          'filters': backendFilters
        });
        
        console.log('✅ Pagos cargados con éxito.');
        setAllCustomers(response.data);
        setFilteredCustomers(response.data);
      } catch (err) {
        setError(err.message || "Error al cargar pagos");
        console.error("❌ Error al cargar pagos:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, [filters]);

  // Escuchar eventos de búsqueda global
  useEffect(() => {
    const handleGlobalSearch = (event) => {
      // console.log('Búsqueda global:', event.detail);
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

    // console.log('Aplicando filtro de búsqueda:', searchTerm);

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

    // 2. Resaltar coincidencias en la tabla
    const rows = tableRef.current.querySelectorAll('tbody tr');
    let firstMatch = null;
    
    rows.forEach(row => {
      // Eliminar cualquier resaltado previo
      row.classList.remove('bg-yellow-100', 'border-l-4', 'border-yellow-500');
      
      // Resaltar si coincide con la búsqueda
      if (searchTerm.length >= 3) {
        const rowText = row.textContent.toLowerCase();
        if (rowText.includes(searchTerm)) {
          row.classList.add('bg-yellow-100', 'border-l-4', 'border-yellow-500');
          if (!firstMatch) firstMatch = row;
        }
      }
    });

    // Scroll al primer resultado si existe
    if (firstMatch) {
      firstMatch.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [searchTerm, allCustomers]);

  const handleUpdateCustomer = (updatedCustomer) => {
    // console.log('Pago actualizado:', updatedCustomer);
    setAllCustomers(prev => 
      prev.map(customer => 
        customer.FACT_RevenueId === updatedCustomer.FACT_RevenueId ? updatedCustomer : customer
      )
    );
    
    setFilteredCustomers(prev => 
      prev.map(customer => 
        customer.FACT_RevenueId === updatedCustomer.FACT_RevenueId ? updatedCustomer : customer
      )
    );
  };

  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectAll(false);
    setIsCheck([...isCheck, id]);
    if (!checked) {
      setIsCheck(isCheck.filter(item => item !== id));
    }
  };

  if (isLoading) return <div className="p-4 text-center">Cargando pagos...</div>;
  if (error) return <div className="p-4 text-center text-red-500">Error: {error}</div>;

  return (
    <div ref={tableRef} className="bg-white dark:bg-gray-800 shadow-xs rounded-xl relative">
      <header className="px-5 py-4">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">
          Total de Pagos Agua <span className="text-gray-400 dark:text-gray-500 font-medium">
            {filteredCustomers.length}
          </span>
        </h2>
      </header>
      <div>
        <div className="overflow-x-auto">
          <table className="table-auto w-full dark:text-gray-300">
            {/* Table header */}
            <thead className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-t border-b border-gray-100 dark:border-gray-700/60">
              <tr>
                {/* Columna Imagen */}
                <th className="px-3 py-3 whitespace-nowrap w-10">
                  <div className="flex items-center justify-center">
                    <p className="hidden md:block">Imagen</p>
                    <p className="md:hidden">Img</p>
                  </div>
                </th>

                {/* Resto de columnas */}
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-left">
                  <div className="font-semibold">Nombre Completo</div>
                </th>
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-center">
                  <div className="font-semibold hidden md:block">Rol de usuario</div>
                  <div className="font-semibold md:hidden">Rol</div>
                </th>
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-left">
                  <div className="font-semibold hidden md:block">Estado de pago</div>
                  <div className="font-semibold md:hidden">estado</div>
                </th>
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-left">
                  <div className="font-semibold hidden md:block">Tipo de servicio</div>
                  <div className="font-semibold md:hidden">Servicio.</div>
                 </th>
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-left">
                  <div className="font-semibold hidden md:block">Cantidad</div>
                </th>
                <th className="px-2 md:px-4 py-3 whitespace-nowrap text-left">
                  <div className="font-semibold hidden md:block">Fecha de pago</div>
                  <div className="font-semibold md:hidden">Fec. pago</div>
                </th>
                <th className="px-2 py-3 whitespace-nowrap w-20 text-center">
                  <span className="font-semibold">Acciones</span>
                </th>
              </tr>
            </thead>
            
            {/* Table body */}
            <tbody className="text-sm divide-y divide-gray-100 dark:divide-gray-700/60">
              {filteredCustomers.map(customer => (
                <Customer
                  key={customer.FACT_RevenueId}
                  id={customer.DIM_AccountId}
                  image={customer.image}
                  full_name={`${customer.CustomerName} ${customer.CustomerMiddleName || ''} ${customer.CustomerLastName} ${customer.CustomerSecondLastName || ''}`}
                  role_name={customer.RoleName}
                  status_factura={customer.StatusFactura}
                  service_type={customer.ServiceDetailesType}
                  amount={customer.amount}
                  status_account={customer.StatusCuenta}
                  dim_date={customer.DIM_DateId}
                  FACT_revenue={customer.FACT_RevenueId}
                  handleClick={handleClick}
                  isChecked={isCheck.includes(customer.FACT_RevenueId)} // Cambiado a FACT_RevenueId
                  onEditSuccess={handleUpdateCustomer}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AguaTable;