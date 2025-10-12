import React, { useState, useRef, useEffect } from 'react';
import Transition from '../../utils/Transition';

/**
 * Componente DateSelect
 * 
 * - El estado `dropdownOpen` controla si el menú desplegable está visible.
 * - El estado `selected` almacena el ID de la opción actualmente seleccionada.
 * 
 * useEffect (click fuera):
 *   Se utiliza para escuchar clics en el documento y cerrar el menú desplegable
 *   si el usuario hace clic fuera del botón o del contenedor del menú. -No funciona
 * 
 * useEffect (ESC):
 *   Se utiliza para cerrar el menú desplegable cuando el usuario presiona
 *   la tecla Escape (keyCode 27). - No funciona 
 * 
 * handleSelection:
 *   Función síncrona que:
 *     - Busca la opción seleccionada en el array `options` usando su ID.
 *     - Actualiza el estado `selected` con el ID de la opción elegida.
 *     - Cierra el menú desplegable.
 *     - Llama a la función `onFilterChange` (si fue proporcionada) pasando
 *       el valor correspondiente a la opción seleccionada.
 * 
 * generateMonthOptions:
 *   Función que genera dinámicamente las opciones de meses disponibles:
 *     - No incluye el mes actual ni meses futuros.
 *     - Incluye meses de hasta un año atrás.
 *     - Cada opción contiene id, period (texto visible) y value (fecha ISO).
 * 
 * UI:
 *   - Botón principal con icono de calendario y texto de la opción seleccionada.
 *   - Icono de flecha que indica desplegable.
 *   - Menú desplegable animado (componente Transition) que lista las opciones.
 *   - Opción seleccionada se marca visualmente con un fondo distinto y un icono de check.
 */

function DateSelect({ onFilterChange }) {
  // Función para generar opciones de meses dinámicamente
  const generateMonthOptions = () => {
    const startYear = 2025;
    const startMonth = 9; // 0-indexed: 9 = Octubre
    const startDate = new Date(startYear, startMonth, 1);

    const options = [];
    const today = new Date();

    const monthNames = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    let id = 0;

    // Caso especial: Si estamos en el mes de inicio (Oct 2025), mostramos solo ese mes.
    if (today.getFullYear() === startYear && today.getMonth() === startMonth) {
      options.push({
        id: 0,
        period: `${monthNames[startMonth]} ${startYear}`,
        value: `M${String(startMonth + 1).padStart(2, '0')}`,
        year: startYear.toString()
      });
      return options;
    }

    // Lógica general: Generar hasta 12 meses hacia atrás desde el mes anterior al actual.
    for (let i = 1; i <= 12; i++) {
      const dateIterator = new Date(today.getFullYear(), today.getMonth() - i, 1);

      // Detener si el mes a generar es anterior a la fecha de inicio.
      if (dateIterator < startDate) break;

      options.push({
        id: id++,
        period: `${monthNames[dateIterator.getMonth()]} ${dateIterator.getFullYear()}`,
        value: `M${String(dateIterator.getMonth() + 1).padStart(2, '0')}`,
        year: dateIterator.getFullYear().toString()
      });
    }
    
    return options;
  };

  const options = generateMonthOptions();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selected, setSelected] = useState(0); // Seleccionar el primer mes disponible por defecto
  const trigger = useRef(null);
  const dropdown = useRef(null);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const clickHandler = ({ target }) => {
      if (!dropdownOpen) return;
      if (!dropdown.current || !trigger.current) return;
      if (dropdown.current.contains(target) || trigger.current.contains(target)) return;
      setDropdownOpen(false);
    };
    document.addEventListener('click', clickHandler);
    return () => document.removeEventListener('click', clickHandler);
  }, [dropdownOpen]);

  // Cerrar al presionar la tecla Escape
  useEffect(() => {
    const keyHandler = ({ keyCode }) => {
      if (!dropdownOpen || keyCode !== 27) return;
        setDropdownOpen(false);
    };
    document.addEventListener('keydown', keyHandler);
    return () => document.removeEventListener('keydown', keyHandler);
  }, [dropdownOpen]);

  const handleSelection = (id) => {
    const option = options.find(opt => opt.id === id);
    if (!option) return;
    
    setSelected(id);
    setDropdownOpen(false);
    
    if (onFilterChange) {
      onFilterChange({
        month: option.value,
        year: option.year
      });
    }
  };

  return (
    <div className="relative">
      <button   
        ref={trigger}
        id="date-select-button"
        className="flex items-center justify-between px-5 py-3 text-base font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-2 dark:focus:ring-offset-gray-900 min-w-[220px]"
        onClick={() => setDropdownOpen(!dropdownOpen)}
        aria-expanded={dropdownOpen}
        aria-haspopup="true"
      >
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-3 text-gray-500 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="text-gray-700 dark:text-gray-200">
            {options.find(opt => opt.id === selected)?.period || 'Filtrar por mes'}
          </span>
        </div>
        <svg className="ml-2 w-5 h-5 text-gray-500 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>

      <Transition
        show={dropdownOpen} 
        tag="div"
        className="z-20 absolute mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg overflow-hidden"
        enter="transition ease-out duration-100"
        enterFrom="opacity-0 scale-95"
        enterTo="opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="opacity-100 scale-100"
        leaveTo="opacity-0 scale-95"
      >
        <div
          ref={dropdown}
          className="py-1 max-h-60 overflow-y-auto"
        >
          {options.map(option => (
            <button
              key={option.id}
              className={`flex items-center w-full px-4 py-2 text-sm text-left ${option.id === selected ? 'bg-indigo-100 dark:bg-gray-700 text-indigo-700 dark:text-indigo-400' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'}`}
              onClick={() => handleSelection(option.id)}
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

export default DateSelect;