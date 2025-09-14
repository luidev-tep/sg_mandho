import React from 'react';

function DashboardCard07({ comitiva, anio, data, loading }) {
  
  // Función para formatear el porcentaje sin decimales
  const formatPercentage = (value) => {
    return Math.round(Number(value));
  };

  // Función para determinar el color del porcentaje según el valor
  const getPercentageColor = (percentage) => {
    const value = formatPercentage(percentage);
    if (value >= 90) return '#10B981'; // Verde
    if (value >= 70) return '#3B82F6'; // Azul
    if (value >= 50) return '#F59E0B'; // Amarillo
    return '#EF4444'; // Rojo
  };

  return (
    <div className="col-span-full xl:col-span-8 bg-white dark:bg-gray-800 shadow-lg rounded-xl overflow-hidden">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100 text-2xl">
          {comitiva} - Resumen Anual {anio}
        </h2>
      </header>
      <div className="p-3">
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="table-auto w-full dark:text-gray-300">
            {/* Table header */}
            <thead className="text-xs uppercase text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-700/50 rounded-xs">
              <tr>
                <th className="p-2">
                  <div className="font-semibold text-left">Manzanas</div>
                </th>
                <th className="p-2">
                  <div className="font-semibold text-center">Personas</div>
                </th>
                <th className="p-2">
                  <div className="font-semibold text-center">Pagados</div>
                </th>
                <th className="p-2">
                  <div className="font-semibold text-center">Pendientes</div>
                </th>
                <th className="p-2">
                  <div className="font-semibold text-center">Porcentaje</div>
                </th>
              </tr>
            </thead>
            {/* Table body */}
            <tbody className="text-sm font-semibold divide-y divide-gray-100 dark:divide-gray-700/60">
              {loading ? (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-gray-500">
                    <div className="flex justify-center items-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                      <span className="ml-2">Cargando datos...</span>
                    </div>
                  </td>
                </tr>
              ) : data && data.manzanas && data.manzanas.length > 0 ? (
                data.manzanas.map((manzana) => {
                  const percentageColor = getPercentageColor(manzana.porcentaje);
                  return (
                    <tr key={manzana.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                      <td className="p-2">
                        <div className="flex items-center">
                          <div className="shrink-0 mr-3 w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: manzana.color }}>
                            <span className="text-white font-bold text-xs">{manzana.nombre.charAt(0)}</span>
                          </div>
                          <div className="text-gray-800 dark:text-gray-100 font-semibold">{manzana.nombre}</div>
                        </div>
                      </td>
                      <td className="p-2">
                        <div className="text-center">{manzana.personas}</div>
                      </td>
                      <td className="p-2">
                        <div className="text-center text-green-500 font-bold">{manzana.pagados}</div>
                      </td>
                      <td className="p-2">
                        <div className="text-center text-red-500 font-bold">{manzana.pendientes}</div>
                      </td>
                      <td className="p-2">
                        <div className="text-center font-bold" style={{ color: percentageColor }}>
                          {formatPercentage(manzana.porcentaje)}%
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-gray-500">
                    No hay datos disponibles
                  </td>
                </tr>
              )}
            </tbody>
            {/* Table footer con totales */}
            {data && data.manzanas && data.manzanas.length > 0 && !loading && (
              <tfoot className="text-sm font-bold text-gray-800 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/70">
                <tr>
                  <td className="p-2 text-left">Total</td>
                  <td className="p-2 text-center">
                    {data.manzanas.reduce((total, manzana) => total + manzana.personas, 0)}
                  </td>
                  <td className="p-2 text-center text-green-500">
                    {data.manzanas.reduce((total, manzana) => total + manzana.pagados, 0)}
                  </td>
                  <td className="p-2 text-center text-red-500">
                    {data.manzanas.reduce((total, manzana) => total + manzana.pendientes, 0)}
                  </td>
                  <td className="p-2 text-center" style={{ 
                    color: getPercentageColor(
                      (data.manzanas.reduce((total, manzana) => total + manzana.pagados, 0) /
                      data.manzanas.reduce((total, manzana) => total + manzana.personas, 0)) * 100
                    )
                  }}>
                    {formatPercentage(
                      (data.manzanas.reduce((total, manzana) => total + manzana.pagados, 0) /
                        data.manzanas.reduce((total, manzana) => total + manzana.personas, 0)) * 100
                    )}%
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>
    </div>
  );
}

export default DashboardCard07;