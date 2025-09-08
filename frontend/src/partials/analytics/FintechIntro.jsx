import React from 'react';
import { useAuth } from '../../utils/AuthContext';
import UserImage from '../../images/user-40-02.jpg';

function FintechIntro({ comitiva, mes, mes_format }) {
  const { state } = useAuth();
  const nombreUsuario = state.usuario?.UserFullName || 'Usuario';
  const nombreComitiva = comitiva ? comitiva.charAt(0).toUpperCase() + comitiva.slice(1) : '';
    
  return (
    <div className="flex flex-col col-span-full bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <div className="px-5 py-6">
        <div className="flex flex-col sm:flex-row items-center md:items-start">
          {/* Imagen de perfil */}
          <div className="mb-4 sm:mb-0 sm:mr-6">
            <div className="relative">
              <img 
                src={UserImage} 
                className="w-16 h-16 rounded-full border-2 border-indigo-100 dark:border-gray-600 shadow-sm" 
                alt={nombreUsuario}
              />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-700"></div>
            </div>
          </div>
          
          {/* Información del usuario y mensaje */}
          <div className="text-center sm:text-left">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Hola, <span className="text-indigo-500">{nombreUsuario}</span> 👋
            </h2>
            <p className="mt-1 text-gray-600 dark:text-gray-300">
              Estas son las analíticas de la comitiva <span className="font-medium text-indigo-600 dark:text-indigo-400">{nombreComitiva}</span> en el mes de <span className="font-medium text-indigo-600 dark:text-indigo-400">{mes_format || mes}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FintechIntro;