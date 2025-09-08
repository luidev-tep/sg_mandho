import React, { useEffect, useState } from 'react';
import BarChart from '../../charts/BarChart02'; 
import Tooltip  from '../../components/Tooltip';
import { getCssVariable } from '../../utils/Utils';

function DashboardCard10({ comitiva, mes_format, data, loading }) {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{
      label: 'Ingresos por Manzana',
      data: [],
      backgroundColor: getCssVariable('--color-indigo-500'),
      hoverBackgroundColor: getCssVariable('--color-indigo-600'),
      barPercentage: 0.8,
      categoryPercentage: 0.9,
      borderRadius: 4,
    }]
  });

  // Formatear los datos cuando cambian los props
  useEffect(() => {
    if (data && Array.isArray(data)) {
      // Ordenar las manzanas alfabéticamente
      const sortedData = [...data].sort((a, b) => a.manzana.localeCompare(b.manzana));

      setChartData({
        labels: sortedData.map(item => item.manzana),
        datasets: [{
          ...chartData.datasets[0],
          data: sortedData.map(item => item.ingresos)
        }]
      });
    }
  }, [data]);

  // Opciones del gráfico
  const options = {
    indexAxis: 'y', // Hace que las barras sean horizontales
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `$${context.raw.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          borderDash: [4, 4],
        },
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`,
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  };

  // Calcular total
  const totalIngresos = chartData.datasets[0].data.reduce((sum, value) => sum + value, 0);
  const manzanaMayorIngreso = chartData.labels[
    chartData.datasets[0].data.indexOf(Math.max(...chartData.datasets[0].data))
  ] || 'N/A';

  if (loading) {
    return (
      <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
  <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
    <h2 className="font-semibold text-gray-800 dark:text-gray-100">
      Ingresos por Manzana - {comitiva} - {mes_format}
    </h2>
    <Tooltip className="ml-2" size="lg">
      <div className="text-sm">
        Distribución de ingresos por manzana en {mes_format}
      </div>
    </Tooltip>
  </header>
      
      <div className="px-5 py-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Recaudado</div>
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              ${totalIngresos.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Mayor Ingreso</div>
            <div className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              {manzanaMayorIngreso}
            </div>
          </div>
        </div>
      </div>

      <div className="grow px-5 pb-5">
        <div style={{ height: `${Math.max(200, data?.length * 30 || 200)}px` }}>
        <BarChart 
          data={chartData} 
          width={595} 
          height={248} 
        />
        </div>
      </div>
    </div>
  );
}

export default DashboardCard10;