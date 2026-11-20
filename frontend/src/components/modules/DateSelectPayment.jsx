import React, { useState, useRef, useEffect, useCallback } from 'react';
import Transition from '../../utils/Transition';

/**
 * Componente DateSelectPayment para seleccionar un año.
 * Reconstruido con una lógica de eventos robusta para garantizar un funcionamiento fiable.
 */
function DateSelectPayment({ onFilterChange }) {
  const startYear = 2021; // Año de inicio de los registros históricos del proyecto
  const currentYear = new Date().getFullYear();

  // Calcula cuántos años mostrar: desde el año actual hasta el año de inicio
  const yearsSinceStart = currentYear >= startYear ? currentYear - startYear + 1 : 1;
  const years = Array.from({ length: yearsSinceStart }, (_, i) => currentYear - i);
  
  const options = years.map((year, index) => ({
    id: index,
    period: year.toString(),
    value: year
  }));
  
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selected, setSelected] = useState(0);
  const trigger = useRef(null);
  const dropdown = useRef(null);
  const containerRef = useRef(null);

  // Función para cerrar el dropdown, envuelta en useCallback para estabilidad
  const closeDropdown = useCallback(() => {
    setDropdownOpen(false);
  }, []);

  // Hook para manejar clics fuera del componente
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!dropdownOpen) return;
      // Si el clic es fuera del contenedor principal del componente, ciérralo
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        closeDropdown();
      }
    };
    // Usamos mousedown para prevenir condiciones de carrera
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen, closeDropdown]);

  // Hook para manejar la tecla 'Escape'
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (dropdownOpen && e.key === 'Escape') {
        closeDropdown();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [dropdownOpen, closeDropdown]);

  // Manejador del clic en el botón para alternar el menú
  const handleButtonClick = useCallback((e) => {
    // Prevenimos el comportamiento por defecto y la propagación
    e.preventDefault();
    e.stopPropagation();
    setDropdownOpen(prev => !prev);
  }, []);

  // Manejador para cuando se selecciona una opción
  const handleSelection = useCallback((id) => {
    const selectedOption = options.find(option => option.id === id);
    if (!selectedOption) return;
    
    setSelected(id);
    closeDropdown();
    
    if (onFilterChange) {
      onFilterChange(selectedOption.value);
    }
  }, [onFilterChange, closeDropdown, options]);
  
  return (
    <div className="relative" ref={containerRef}>
      <button
        ref={trigger}
        type="button"
        className="flex items-center justify-between px-3 py-2 text-sm font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 dark:focus:ring-offset-gray-900 min-w-[120px]"
        onClick={handleButtonClick}
        onMouseDown={(e) => e.preventDefault()} // Previene que el mousedown quite el foco
        aria-expanded={dropdownOpen}
        aria-haspopup="true"
      >
        <div className="flex items-center">
          <svg className="w-4 h-4 mr-2 text-gray-500 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="text-gray-700 dark:text-gray-200">
            {options.find(opt => opt.id === selected)?.period || 'Seleccionar'}
          </span>
        </div>
        <svg 
          className={`ml-1 w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} 
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
  
      <Transition
        show={dropdownOpen}
        tag="div"
        className="z-20 absolute top-full right-0 mt-1 w-full min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg overflow-hidden"
        enter="transition ease-out duration-100"
        enterStart="opacity-0 -translate-y-2"
        enterEnd="opacity-100 translate-y-0"
        leave="transition ease-in duration-75"
        leaveStart="opacity-100"
        leaveEnd="opacity-0"
      >
        <div ref={dropdown} className="py-1 max-h-60 overflow-y-auto">
          {options.map(option => (
            <button
              key={option.id}
              type="button"
              className={`flex items-center w-full px-4 py-2 text-sm text-left transition-colors duration-150 ${
                option.id === selected 
                  ? 'bg-indigo-100 dark:bg-gray-700 text-indigo-700 dark:text-indigo-400' 
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              onClick={() => handleSelection(option.id)}
              onMouseDown={(e) => e.preventDefault()}
            >
              {option.period}
              {option.id === selected && (
                <svg className="ml-auto h-4 w-4 text-indigo-500 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      </Transition>
    </div>
  );
}

export default DateSelectPayment;