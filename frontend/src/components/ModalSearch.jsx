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
            placeholder="Buscar (mínimo 3 caracteres)..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
          <button
            type="button"
            className="absolute right-0 top-0 mt-3 mr-4 text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
            onClick={() => {
              setSearchTerm('');
              window.dispatchEvent(new CustomEvent('globalSearch', { detail: '' }));
            }}
          >
            <span className="sr-only">Limpiar</span>
            <svg className="w-4 h-4 fill-current" viewBox="0 0 16 16">
              <path d="M7.95 6.536l4.242-4.243a1 1 0 111.415 1.414L9.364 7.95l4.243 4.242a1 1 0 11-1.415 1.415L7.95 9.364l-4.243 4.243a1 1 0 01-1.414-1.415L6.536 7.95 2.293 3.707a1 1 0 011.414-1.414L7.95 6.536z" />
            </svg>
          </button>
        </div>
        {searchTerm.length > 0 && searchTerm.length < 3 && (
          <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50">
            Escribe al menos 3 caracteres...
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