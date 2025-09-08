import React from 'react';
import PieChart from '../../charts/PieChart'; 
import { getCssVariable } from '../../utils/Utils';

function FintechCard09({ comitiva, mes_format, data, loading }) {
  // Datos iniciales vacíos
  const [chartData, setChartData] = React.useState({
    labels: [],
    datasets: [{
      label: 'Población por Manzana',
      data: [],
      backgroundColor: [],
      hoverBackgroundColor: [],
      borderWidth: 0,
    }]
  });

  // Calcular total de personas
  const totalPersonas = React.useMemo(() => {
    if (!data?.manzanas) return 0;
    return data.manzanas.reduce((sum, manzana) => sum + manzana.personas, 0);
  }, [data]);

  // Actualizar datos del gráfico cuando cambian los datos
  React.useEffect(() => {
    if (data?.manzanas) {
      const colors = [
        '--color-green-400', '--color-yellow-400', '--color-sky-500',
        '--color-violet-500', '--color-red-400', '--color-orange-400'
      ];
      const hoverColors = colors.map(c => c.replace('400', '500').replace('500', '600'));

      setChartData({
        labels: data.manzanas.map(m => m.nombre),
        datasets: [{
          ...chartData.datasets[0],
          data: data.manzanas.map(m => m.personas),
          backgroundColor: colors.map(c => getCssVariable(c)),
          hoverBackgroundColor: hoverColors.map(c => getCssVariable(c))
        }]
      });
    }
  }, [data]);

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
          Población por Manzana - {comitiva}
        </h2>
      </header>
      <div className="px-5 py-3">
        <div className="text-sm italic mb-2">Distribución de habitantes por manzana:</div>
        <div className="text-3xl font-bold text-gray-800 dark:text-gray-100">
          {totalPersonas.toLocaleString()} personas
        </div>
      </div>
      <div className="grow px-5 pb-5">
        <div style={{ height: '300px' }}>
          <PieChart data={chartData} width={400} height={300} />
        </div>
      </div>
    </div>
  );
}

export default FintechCard09;
