// partials/customers/CustomersTable.jsx
import React, { useState, useEffect, useRef } from 'react';
import Customer from './MostrarUsuariosItem';
import { MostrarUsuarios } from '../../../../api/api_user';

function CustomersTable({ filters }) {
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
        const zonas = [];
        if (filters.cerritos) zonas.push('cerritos');
        if (filters.centro) zonas.push('centro');
        if (filters.garambullo) zonas.push('garambullo');
        if (filters.yhonda) zonas.push('yhonda');
        if (filters.tepetate) zonas.push('tepetate');
        if (filters.buenavista) zonas.push('buenavista');
        
        if (zonas.length > 0) {
          backendFilters.CustomerFraction = zonas;
        }
        
        // Mapear filtros de fecha
        if (filters.day) backendFilters.DIM_Date = 'FiscalDay';
        else if (filters.month) backendFilters.DIM_Date = 'FiscalMonth';
        else if (filters.year) backendFilters.DIM_Date = 'FiscalYear';

        // Mapear filtro de defunciones
        if (filters.enddate) backendFilters.CustomerEndDate = true;

        const response = await MostrarUsuarios({
          'id_user': "",
          'filters': backendFilters
        });
        
        setAllCustomers(response.data);
        setFilteredCustomers(response.data);
      } catch (err) {
        setError(err.message || "Error al cargar usuarios");
        console.error("Error fetching customers:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, [filters]);

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

    // 1. Filtrar clientes
    let filtered = allCustomers;
    if (searchTerm.length >= 3) {
      filtered = allCustomers.filter(customer => {
        const searchFields = [
          customer.first_name,
          customer.second_name,
          customer.last_name,
          customer.second_last_name,
          customer.street,
          customer.number_ext,
          customer.manzana,
          customer.date_of_birth
        ].join(' ').toLowerCase();

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


  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectAll(false);
    setIsCheck([...isCheck, id]);
    if (!checked) {
      setIsCheck(isCheck.filter(item => item !== id));
    }
  };

  if (isLoading) return <div className="p-4 text-center">Cargando usuarios...</div>;
  if (error) return <div className="p-4 text-center text-red-500">Error: {error}</div>;

  return (
    <div ref={tableRef} className="bg-transparent">
      <header className="px-5 py-4">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">
          Total de Usuarios <span className="text-gray-400 dark:text-gray-500 font-medium">
            {filteredCustomers.length}
          </span>
        </h2>
      </header>
      <div className="w-full">
        {/* Encabezado (visible en md y superior) */}
        <div className="hidden md:grid md:grid-cols-8 md:gap-4 bg-gray-50 dark:bg-gray-700/50 font-semibold text-xs uppercase text-gray-500 dark:text-gray-400 p-2 rounded-t-lg border-b border-gray-200 dark:border-gray-700">
          <div className="text-center">imagen</div>
          <div className="md:col-span-2">Nombre Completo</div>
          <div className="text-center">Manzana</div>
          <div>Dirección</div>
          <div className="text-center">Nacimiento</div>
          <div className="text-center">Defunción</div>
          <div className="text-center">Acciones</div>
        </div>

        {/* Cuerpo de la tabla */}
        <div className="space-y-2 md:space-y-0 pb-24">
          {filteredCustomers.map(customer => (
            <Customer
              key={customer.id_user}
              id={customer.id_user}
              image={customer.image}
              name={customer.first_name + ' ' + customer.second_name}
              last_name={customer.last_name + ' ' + customer.second_last_name}
              birth_date={customer.date_of_birth}
              manzana={customer.manzana}
              address={customer.street + ' ' + customer.number_ext}
              date_of_end={customer.date_user_end}
              handleClick={handleClick}
              isChecked={isCheck.includes(customer.id_user)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default CustomersTable;