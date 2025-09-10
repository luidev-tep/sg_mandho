// DashboardCard10 - Versión final
import React, { useEffect, useState } from 'react';
import BarChartFraction from '../../charts/BarchartFraction';
import Tooltip from '../../components/Tooltip';
import { getCssVariable } from '../../utils/Utils';

function DashboardCard10({ comitiva, mes_format, data, loading }) {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Ingresos',
        data: [],
        backgroundColor: getCssVariable('--color-indigo-500'),
        hoverBackgroundColor: getCssVariable('--color-indigo-600'),
        barPercentage: 0.7,
        categoryPercentage: 0.7,
        borderRadius: 4,
      },
    ],
  });

  console.log("Datos recibidos en el componente hijo: ", data);
  const [chartKey, setChartKey] = useState(0);

  // Efecto para actualizar chartData cuando cambian los datos
  useEffect(() => {
    if (data && Array.isArray(data) && data.length > 0) {
      // Ordenar datos alfabéticamente por fraction
      const sortedData = [...data].sort((a, b) => a.fraction.localeCompare(b.fraction));

      const labels = sortedData.map(item => item.fraction);
      const amounts = sortedData.map(item => item.revenue || 0);

      const newChartData = {
        labels,
        datasets: [
          {
            label: 'Ingresos',
            data: amounts,
            backgroundColor: getCssVariable('--color-indigo-500'),
            hoverBackgroundColor: getCssVariable('--color-indigo-600'),
            barPercentage: 0.7,
            categoryPercentage: 0.7,
            borderRadius: 4,
          },
        ],
      };

      setChartData(newChartData);
      setChartKey(prevKey => prevKey + 1); // Incrementar la clave para forzar re-render
    } else {
      // Resetear datos
      const emptyChartData = {
        labels: [],
        datasets: [
          {
            label: 'Ingresos',
            data: [],
            backgroundColor: getCssVariable('--color-indigo-500'),
            hoverBackgroundColor: getCssVariable('--color-indigo-600'),
            barPercentage: 0.7,
            categoryPercentage: 0.7,
            borderRadius: 4,
          },
        ],
      };
      setChartData(emptyChartData);
      setChartKey(prevKey => prevKey + 1);
    }
  }, [data, mes_format]); // Se ejecuta cuando data o mes_format cambian

  // Calcular el total de ingresos
  const totalIngresos = data?.reduce((sum, item) => sum + (item.revenue || 0), 0) || 0;

  // Encontrar la manzana con mayor ingreso
  const findManzanaMayorIngreso = () => {
    if (!data || data.length === 0) return 'N/A';
    
    const maxItem = data.reduce((max, item) => 
      (item.revenue > max.revenue) ? item : max, data[0]);
    
    return maxItem.fraction || 'N/A';
  };

  const manzanaMayorIngreso = findManzanaMayorIngreso();

  if (loading) {
    return (
      <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
        <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
          <h2 className="font-semibold text-gray-800 dark:text-gray-100">Ingresos por Manzana {comitiva ? `de ${comitiva}` : 'de la comunidad'}</h2>
        </header>
        <div className="px-5 py-3">
          <div className="flex items-start">
            <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mr-2">Cargando...</div>
          </div>
        </div>
        <div className="grow">
          <div className="h-60 w-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">
          Ingresos por Manzana {comitiva && `- ${comitiva}`} {mes_format && `- ${mes_format}`}
        </h2>
        <Tooltip className="ml-2" size="lg">
          <div className="text-sm">
            Distribución de ingresos por manzana {mes_format ? `en ${mes_format}` : ''}
          </div>
        </Tooltip>
      </header>
      
      <div className="px-5 py-3">
        <div className="flex items-start">
          <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mr-2">
            ${totalIngresos.toLocaleString()}
          </div>
          <div className="text-sm font-medium px-1.5 rounded-full text-indigo-700 bg-indigo-500/20">
            Mayor: {manzanaMayorIngreso}
          </div>
        </div>
      </div>

      <div className="grow">
        {data && data.length > 0 ? (
          <BarChartFraction key={chartKey} data={chartData} width={595} height={248} />
        ) : (
          <div className="h-60 w-full flex items-center justify-center">
            <div className="text-gray-500 dark:text-gray-400">No hay datos disponibles</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardCard10;