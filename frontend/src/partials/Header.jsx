import React, { useState } from 'react';
import SearchDropdown from '../components/ModalSearch';
import UserMenu from '../components/DropdownProfile';
import ThemeToggle from '../components/ThemeToggle';

function Header({
  sidebarOpen,
  setSidebarOpen,
  variant = 'default',
}) {
  // Corregido: nombre diferente para el estado (searchOpen) y el componente (SearchDropdown)
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header className={`sticky top-0 before:absolute before:inset-0 before:backdrop-blur-md max-lg:before:bg-white/90 dark:max-lg:before:bg-gray-800/90 before:-z-10 z-30 ${variant === 'v2' || variant === 'v3' ? 'before:bg-white after:absolute after:h-px after:inset-x-0 after:top-full after:bg-gray-200 dark:after:bg-gray-700/60 after:-z-10' : 'max-lg:shadow-xs lg:before:bg-gray-100/90 dark:lg:before:bg-gray-900/90'} ${variant === 'v2' ? 'dark:before:bg-gray-800' : ''} ${variant === 'v3' ? 'dark:before:bg-gray-900' : ''}`}>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className={`flex items-center justify-between h-20 ${variant === 'v2' || variant === 'v3' ? '' : 'lg:border-b border-gray-200 dark:border-gray-700/60'}`}>

          {/* Header: Left side */}
          <div className="flex pl-12 lg:pl-0">
            <h1 className="text-lg sm:text-2xl font-bold text-gray-800 dark:text-white whitespace-nowrap">
              <span className="sm:hidden">S.R. El Mandho</span>
              <span className="hidden sm:inline">Sistema de Registro El Mandhó</span>
            </h1>
          </div>
          {/* Header: Right side */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* Botón de búsqueda - ahora responsivo */}
            <div>
              <button
                className={`flex items-center justify-center bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600/80 rounded-full ml-3 px-3 py-2 ${
                  searchOpen ? 'bg-gray-200' : ''
                }`}
                onClick={(e) => { 
                  e.stopPropagation(); 
                  setSearchOpen(!searchOpen); 
                }}
                aria-controls="search-dropdown"
              > 
                <span className="sr-only">Buscar</span>
                <svg className="w-4 h-4 mr-2" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                  <path className="fill-current text-gray-500 dark:text-gray-400" d="M7 14c-3.86 0-7-3.14-7-7s3.14-7 7-7 7 3.14 7 7-3.14 7-7 7zM7 2C4.243 2 2 4.243 2 7s2.243 5 5 5 5-2.243 5-5-2.243-5-5-5z" />
                  <path className="fill-current text-gray-400 dark:text-gray-500" d="M15.707 14.293L13.314 11.9a8.019 8.019 0 01-1.414 1.414l2.393 2.393a1 1 0 001.414-1.414z" />
                </svg>
                <span className="hidden sm:inline text-sm font-semibold text-gray-600 dark:text-gray-300">Buscar</span>
              </button>
              
              {/* Desplegable de búsqueda */}
              <SearchDropdown
                id="search-dropdown"
                searchId="search"
                dropdownOpen={searchOpen}
                setDropdownOpen={setSearchOpen}
              />
            </div>

            {/* Divider */}
            <hr className="w-px h-8 bg-gray-200 dark:bg-gray-700/60 border-none" />
            
            <ThemeToggle />
            
            <UserMenu align="right" />
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;