// components/ModalSearch.jsx
import React, { useRef, useEffect, useState } from 'react';
import Transition from '../utils/Transition';

function SearchDropdown({
  id,
  searchId,
  dropdownOpen,
  setDropdownOpen
}) {
  const dropdownRef = useRef(null);
  const searchInput = useRef(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const clickHandler = ({ target }) => {
      if (!dropdownRef.current || !dropdownOpen || dropdownRef.current.contains(target)) return;
      setDropdownOpen(false);
    };
    document.addEventListener('click', clickHandler);
    return () => document.removeEventListener('click', clickHandler);
  }, [dropdownOpen]);

  // Cerrar al presionar Esc
  useEffect(() => {
    const keyHandler = ({ keyCode }) => {
      if (!dropdownOpen || keyCode !== 27) return;
      setDropdownOpen(false);
    };
    document.addEventListener('keydown', keyHandler);
    return () => document.removeEventListener('keydown', keyHandler);
  }, [dropdownOpen]);

  useEffect(() => {
    if (dropdownOpen) {
      searchInput.current.focus();
    } else {
      setSearchTerm('');
      window.dispatchEvent(new CustomEvent('globalSearch', { detail: '' }));
    }
  }, [dropdownOpen]);

  const handleSearchChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    
    // Disparar evento siempre pero la tabla solo actuará con 3+ caracteres
    window.dispatchEvent(new CustomEvent('globalSearch', { detail: term }));
  };

  return (
    <Transition
      show={dropdownOpen}
      tag="div"
      id={id}
      className="absolute top-full left-0 right-0 z-50 mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden"
      enter="transition ease-out duration-200 transform"
      enterStart="opacity-0 -translate-y-2"
      enterEnd="opacity-100 translate-y-0"
      leave="transition ease-out duration-200"
      leaveStart="opacity-100"
      leaveEnd="opacity-0"
    >
      <div ref={dropdownRef} className="px-4 py-2">
        <div className="relative">
          <label htmlFor={searchId} className="sr-only">Buscar</label>
          <input
            id={searchId}
            ref={searchInput}
            className="w-full border-0 px-4 py-3 focus:ring-0 focus:outline-none dark:bg-gray-800 dark:text-gray-100"
            type="search"
            placeholder="Buscar (Escribe para empezar a buscar)..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
          <div className="absolute right-0 top-0 mt-3 mr-4 flex items-center text-gray-400">
            <svg className="w-4 h-4 fill-current mr-1" viewBox="0 0 16 16">
              <path d="M7 14c-3.86 0-7-3.14-7-7s3.14-7 7-7 7 3.14 7 7-3.14 7-7 7zM7 2C4.243 2 2 4.243 2 7s2.243 5 5 5 5-2.243 5-5-2.243-5-5-5zM15.707 14.293L13.314 11.9a8.019 8.019 0 01-1.414 1.414l2.393 2.393a.997.997 0 001.414 0 .999.999 0 000-1.414z" />
            </svg>
            <span className="text-sm">Buscar</span>
          </div>
        </div>
        {searchTerm.length > 0 && searchTerm.length < 3 && (
          <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50">
            Escribe para empezar a buscar ... 
          </div>
        )}
        {searchTerm.length >= 3 && (
          <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50">
            Buscando: <span className="font-medium">{searchTerm}</span>
          </div>
        )}
      </div>
    </Transition>
  );
}

export default SearchDropdown;