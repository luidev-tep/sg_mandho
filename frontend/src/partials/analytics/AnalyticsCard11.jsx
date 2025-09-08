import React from 'react';
import UserImage from '../../images/user-40-02.jpg';

// ESTE COMPONENTE RECIBIRA UN JSON CON LOS DATOS DE LOS USUARIOS ADMINISTRADORES DE LA COMITIVA EN CUESTION
// POR EJEMPLO PARA LA COMITIVA DE AGUA DEVOLVERA A LOS USUARIOS CUYO SERIVICIO SEA EL DE AGUA, JUNTO CON SU FECHA DE INICIO Y 
// FECHA DE FIN
function AnalyticsCard11({ comitiva, data, loading }) {
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">Administradores - {comitiva}</h2>
      </header>
      <div className="p-3">

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="table-auto w-full dark:text-gray-300">
            {/* Table header */}
            <thead className="text-xs uppercase text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-700/50 rounded-xs">
              <tr>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-left">Nombre</div>
                </th>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-left">Apellidos</div>
                </th>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-left">Comitiva</div>
                </th>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-center">Fecha Inicio</div>
                </th>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-center">Fecha Fin</div>
                </th>
              </tr>
            </thead>
            {/* Table body */}
            <tbody className="text-sm divide-y divide-gray-100 dark:divide-gray-700/60">
              {data && data.administradores ? data.administradores.map((admin) => (
                <tr key={admin.id}>
                  <td className="p-2 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="shrink-0 rounded-full mr-2 sm:mr-3">
                        <img className="rounded-full" src={UserImage} width="36" height="36" alt="User" />
                      </div>
                      <div className="font-medium text-gray-800 dark:text-gray-100">{admin.nombre}</div>
                    </div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-gray-800 dark:text-gray-100">{admin.apellidos}</div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="flex items-center">
                      <svg className="fill-current text-gray-400 dark:text-gray-500 shrink-0 mr-2" width="16" height="16" viewBox="0 0 16 16">
                        <path d="M4.3 4.5c1.9-1.9 5.1-1.9 7 0 .7.7 1.2 1.7 1.4 2.7l2-.3c-.2-1.5-.9-2.8-1.9-3.8C10.1.4 5.7.4 2.9 3.1L.7.9 0 7.3l6.4-.7-2.1-2.1zM15.6 8.7l-6.4.7 2.1 2.1c-1.9 1.9-5.1 1.9-7 0-.7-.7-1.2-1.7-1.4-2.7l-2 .3c.2 1.5.9 2.8 1.9 3.8 1.4 1.4 3.1 2 4.9 2 1.8 0 3.6-.7 4.9-2l2.2 2.2.8-6.4z" />
                      </svg>
                      <div className="text-gray-800 dark:text-gray-100 capitalize">{admin.comitiva}</div>
                    </div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-center text-gray-800 dark:text-gray-100">{admin.fechaInicio}</div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-center text-gray-800 dark:text-gray-100">{admin.fechaFin}</div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-gray-500">
                    {loading ? 'Cargando administradores...' : 'No hay administradores disponibles'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>

        </div>

      </div>
    </div>
  );
}

export default AnalyticsCard11;