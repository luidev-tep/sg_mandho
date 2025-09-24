import React from 'react';
import UserImage from '../../images/user-40-02.jpg';

// ESTE COMPONENTE RECIBIRA UNJSON C ON LOS DATOS DE LOS USUARIOS ADMINISTRADORES DE LA COMITIVA EN CUESTION
// POR EJEMPLO PARA LA COMITIVA DE AGUA DEVOLVERA A LOS USUARIOS CUYO SERIVICIO SEA EL DE AGUA, JUNTO CON SU FECHA DE INICIO Y 
// FECHA DE FIN
function AnalyticsCard11({ comitiva, data, loading }) {
  //console.log(data);
  return (
    <div className="col-span-full bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-50">Administradores - {comitiva}</h2>
      </header>
      <div className="p-3">

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="table-auto w-full dark:text-gray-300">
            {/* Table header */}
            <thead className="text-xs uppercase text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-700/50 rounded-xs">
              <tr>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-left">Nombre Completo</div>
                </th>
                <th className="p-2 whitespace-nowrap">
                  <div className="font-semibold text-left">Rol</div>
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
              {data && data.length > 0 ? data.map((admin, index) => (
                <tr key={index}>
                  <td className="p-2 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="shrink-0 rounded-full mr-2 sm:mr-3">
                        <img className="rounded-full" src={UserImage} width="36" height="36" alt="User" />
                      </div>
                      <div className="font-medium text-gray-800 dark:text-gray-100 capitalize">{admin.fullname}</div>
                    </div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-left text-gray-800 dark:text-gray-100 capitalize">{admin.RoleName}</div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-center text-gray-800 dark:text-gray-100">{admin.StartDate}</div>
                  </td>
                  <td className="p-2 whitespace-nowrap">
                    <div className="text-center text-gray-800 dark:text-gray-100">{admin.EndDate}</div>
                  </td>
                 </tr>
              )) : (
                <tr>
                  <td colSpan="4" className="p-4 text-center text-gray-500">
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