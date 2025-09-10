import React from 'react';
import PieChart from '../../charts/PieChart'; 
import { getCssVariable } from '../../utils/Utils';

function FintechCard09({ comitiva, data, loading }) {
  
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

  // Preparar datos para el gráfico
  const chartData = {
    labels: data?.manzanas ? data.manzanas.map(m => m.nombre) : [],
    datasets: [
      {
        label: 'Población por Manzana',
        data: data?.manzanas ? data.manzanas.map(m => m.personas) : [],
        backgroundColor: data?.manzanas ? 
          data.manzanas.map((_, index) => 
            getCssVariable(colorPalette[index % colorPalette.length])
          ) : [],
        hoverBackgroundColor: data?.manzanas ? 
          data.manzanas.map((_, index) => 
            getCssVariable(hoverColorPalette[index % hoverColorPalette.length])
          ) : [],
        borderWidth: 0,
      },
    ],
  };

  // Calcular total de personas
  const totalPersonas = data?.manzanas ? 
    data.manzanas.reduce((sum, manzana) => sum + manzana.personas, 0) : 0;

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
          Población por Manzana {comitiva && `- ${comitiva}`}
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
      <PieChart data={chartData} width={389} height={220} />
    </div>
  );
}

export default FintechCard09;