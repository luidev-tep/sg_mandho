import React from 'react';
import PieChart from '../../charts/PieChart'; 
import { getCssVariable } from '../../utils/Utils';

function FintechCard09({ comitiva, mes_format, data, loading }) {
  
  // Paleta de colores predefinida
  const colorPalette = [
    '--color-green-400', 
    '--color-yellow-400', 
    '--color-sky-500',
    '--color-violet-500', 
    '--color-red-400', 
    '--color-orange-400',
    '--color-blue-400',
    '--color-indigo-400',
    '--color-purple-400',
    '--color-pink-400'
  ];

  const hoverColorPalette = [
    '--color-green-500', 
    '--color-yellow-500', 
    '--color-sky-600',
    '--color-violet-600', 
    '--color-red-500', 
    '--color-orange-500',
    '--color-blue-500',
    '--color-indigo-500',
    '--color-purple-500',
    '--color-pink-500'
  ];

  // Verificar si data es null o undefined antes de acceder a sus propiedades
  const manzanas = data && data.manzanas ? data.manzanas : [];

  // Preparar datos para el gráfico - CORREGIDO: usar 'fraction' y 'population'
  const chartData = {
    labels: manzanas.map(m => m.fraction),
    datasets: [
      {
        label: 'Población por Manzana',
        data: manzanas.map(m => m.population),
        backgroundColor: manzanas.map((_, index) => 
          getCssVariable(colorPalette[index % colorPalette.length])
        ),
        hoverBackgroundColor: manzanas.map((_, index) => 
          getCssVariable(hoverColorPalette[index % hoverColorPalette.length])
        ),
        borderWidth: 0,
      },
    ],
  };

  // Calcular total de personas - CORREGIDO: usar 'population'
  const totalPersonas = manzanas.reduce((sum, manzana) => sum + manzana.population, 0);

  if (loading) {
    return (
      <div className="flex flex-col col-span-full sm:col-span-6 xl:col-span-4 bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col col-span-full sm:col-span-6 xl:col-span-4 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">
          Población por Manzana {comitiva && `- ${comitiva}`} {mes_format && `- ${mes_format}`}
        </h2>
      </header>
      <div className="px-5 py-3">
        <div className="text-sm italic mb-2">Distribución de habitantes por manzana:</div>
        <div className="text-3xl font-bold text-gray-800 dark:text-gray-100">
          {totalPersonas.toLocaleString()} personas
        </div>
      </div>
      {/* Chart built with Chart.js 3 */}
      {/* Change the height attribute to adjust the chart height */}
      {manzanas.length > 0 ? (
        <PieChart data={chartData} width={389} height={220} />
      ) : (
        <div className="flex justify-center items-center h-60">
          <p className="text-gray-500 dark:text-gray-400">No hay datos disponibles</p>
        </div>
      )}
    </div>
  );
}

export default FintechCard09;