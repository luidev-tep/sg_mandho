import { communityConfig } from '../../config/communityConfig';
import React, { useState, useEffect } from 'react';
import Sidebar from '../../partials/SideBar.jsx';
import Header from '../../partials/Header.jsx';
import DateSelect from '../../components/modules/DateSelectPayment.jsx';
import FilterButton from '../../components/DropdownFilter.jsx';
import DynamicTable from '../../components/modules/tablas/DynamicTable.jsx';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../utils/AuthContext.jsx';

function DynamicMenu() {
  const { moduleName } = useParams();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [filters, setFilters] = useState({});
  const { state } = useAuth();
  const userRole = state.usuario?.RoleName?.toLowerCase();
  const filterOptions = [
    ...communityConfig.geography.zones,
    { label: 'Pendientes', value: 'pendiente' } 
  ];

  const handleDateFilterChange = (year) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      // Eliminar cualquier clave que sea un número (año)
      Object.keys(newFilters).forEach(key => {
        if (/^\d{4}$/.test(key)) {
          delete newFilters[key];
        }
      });
      if (year) {
        newFilters[year] = true; // La clave es el año (número) y el valor true
      }
      return newFilters;
    });
  };
    // Efecto para establecer el año actual como filtro por defecto al montar el componente
  useEffect(() => {
    const currentYear = new Date().getFullYear();
    // MODIFICADO: Envía el año actual (número) en lugar de la cadena "YXX"
    handleDateFilterChange(currentYear);
  }, []);

  // Limpiar búsqueda al cambiar de vista
  useEffect(() => {
    return () => {
      window.dispatchEvent(new CustomEvent('globalSearch', { detail: '' }));
    };
  }, []);

  const handleCategoryFilterChange = (categoryFilters) => {
    const selectedZoneLabels = filterOptions
      .filter(option => categoryFilters[option.value])
      .map(option => option.label);
    setFilters(prev => {
      const newFilters = { ...prev };
      filterOptions.forEach(option => {
        delete newFilters[option.value];
      });
      Object.keys(categoryFilters).forEach(key => {
        if (categoryFilters[key]) {
          newFilters[key] = true;
        }
      });
      return newFilters;
    });
  };

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Content area */}
      <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        {/* Site header */}
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        <main className="grow">
          <div className="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-[96rem] mx-auto">
            {/* Page header */}
            <div className="sm:flex sm:justify-between sm:items-center mb-8">
              {/* Left: Title */}
              <div className="mb-4 sm:mb-0">
                <h1 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100">Pagos de {moduleName} </h1>
              </div>

              {/* Right: Actions */}
              <div className="flex flex-col sm:flex-row gap-3">
                {/* Filtros container */}
                <div className="flex items-center gap-3 bg-white dark:bg-gray-800 p-2 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
                  {/* Date filter */}
                  <div className="relative">
                    <DateSelect onFilterChange={handleDateFilterChange} />
                  </div>

                  {/* Category filter */}
                  <div className="relative">
                    <FilterButton 
                      align="right" 
                      options={filterOptions} 
                      onFilterChange={handleCategoryFilterChange} 
                    />
                  </div>
                </div>

                {/* Add button */}
                {userRole === 'comitiva' && (
                  <Link
                    to={`/modulos/crear_pago/${moduleName}`}
                    className="flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                  >
                    <span className="flex items-center">
                      <span className="mr-2 text-lg">+</span>
                      <span className="text-sm sm:text-base">Agregar Nuevo Pago</span>
                    </span>
                  </Link>
                )}

                <Link
                  to={`/Analytics/${moduleName}`}
                  className="flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                >
                  <span className="flex items-center">
                    <span className="mr-2 text-lg">+</span>
                    <span className="text-sm sm:text-base">Panel de Control</span>
                  </span>
                </Link>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
              <DynamicTable 
                filters={filters}
                serviceName={moduleName}
              />
            </div>

            <div className="mt-6"> </div>

          </div>
        </main>

      </div>

    </div>
  );
}

export default DynamicMenu;