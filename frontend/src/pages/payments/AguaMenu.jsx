import React, { useState, useEffect } from 'react';
import Sidebar from '../../partials/SideBar';
import Header from '../../partials/Header';
import DateSelect from '../../components/modules/DateSelectPayment.jsx';
import FilterButton from '../../components/DropdownFilter';
import AguaTable from '../../components/modules/tablas/aguaTable.jsx';
import { Link } from 'react-router-dom';

function AguaMenu() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [filters, setFilters] = useState({});
  const filterOptions = [
    { label: 'Cerritos', value: 'cerritos' },
    { label: 'Centro', value: 'centro' },
    { label: 'Garambullo', value: 'garambullo' },
    { label: 'Yhonda', value: 'yhonda' },
    { label: 'Tepetate', value: 'tepetate' },
    { label: 'Buena vista', value: 'buenavista' },
    { label: 'Inactivos', value: 'pendiente' } 
  ];

  const handleDateFilterChange = (dateValue) => {
    const year = dateValue ? '20' + dateValue.slice(1) : null;
    setFilters(prev => {
      const newFilters = { ...prev };
      Object.keys(newFilters).forEach(key => {
        if (key.startsWith('Y')) {
          delete newFilters[key];
        }
      });
      if (dateValue) {
        newFilters[dateValue] = true;
      }
      return newFilters;
    });
  };

  // Efecto para establecer el año actual como filtro por defecto al montar el componente
  useEffect(() => {
    const currentYear = new Date().getFullYear();
    const shortYear = currentYear.toString().slice(-2);
    const yearValue = `Y${shortYear}`;
    handleDateFilterChange(yearValue);
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
                <h1 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100">Pagos de Agua </h1>
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
                <Link
                  to="/modulos/crear_pago/agua"
                  className="flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                >
                  <span className="flex items-center">
                    <span className="mr-2 text-lg">+</span>
                    <span className="text-sm sm:text-base">Agregar Nuevo Pago</span>
                  </span>
                </Link>

                <Link
                  to="/personas/registro"
                  className="flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                >
                  <span className="flex items-center">
                    <span className="mr-2 text-lg">+</span>
                    <span className="text-sm sm:text-base">Generar (No funciona)</span>
                  </span>
                </Link>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
              <AguaTable
                filters={filters}
              />
            </div>

            <div className="mt-6"> </div>

          </div>
        </main>

      </div>

    </div>
  );
}

export default AguaMenu;