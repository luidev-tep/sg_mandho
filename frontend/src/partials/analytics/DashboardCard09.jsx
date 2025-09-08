import React, { useEffect, useState } from 'react';
import BarChart from '../../charts/BarChart02'; 
import  Tooltip  from '../../components/Tooltip';
import { getCssVariable } from '../../utils/Utils';

function DashboardCard09({ comitiva, mes_format, data, loading }) {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{
      label: 'Ingresos',
      data: [],
      backgroundColor: getCssVariable('--color-violet-500'),
      hoverBackgroundColor: getCssVariable('--color-violet-600'),
      barPercentage: 0.7,
      categoryPercentage: 0.7,
      borderRadius: 4,
    }]
  });

  // Formatear los datos cuando cambian los props
  useEffect(() => {
    if (data && Array.isArray(data)) {
      // Asumiendo que data es un array de objetos con { month: 'MM-YYYY', amount: number }
      const sortedData = [...data].sort((a, b) => {
        return new Date(a.month) - new Date(b.month);
      });

      setChartData({
        labels: sortedData.map(item => {
          const [month, year] = item.month.split('-');
          const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
          return `${monthNames[parseInt(month) - 1]} ${year}`;
        }),
        datasets: [{
          ...chartData.datasets[0],
          data: sortedData.map(item => item.amount)
        }]
      });
    }
  }, [data]);

  // Opciones del gráfico
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          borderDash: [4, 4],
        },
        ticks: {
          callback: (value) => `$${value.toLocaleString()}`,
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  // Calcular total
  const totalIncome = chartData.datasets[0].data.reduce((sum, value) => sum + value, 0);
  const previousMonthIncome = chartData.datasets[0].data[chartData.datasets[0].data.length - 2] || 0;
  const currentMonthIncome = chartData.datasets[0].data[chartData.datasets[0].data.length - 1] || 0;
  const percentageChange = previousMonthIncome 
    ? Math.round(((currentMonthIncome - previousMonthIncome) / previousMonthIncome) * 100) 
    : 0;

  if (loading) {
    return (
      <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl p-5">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
      <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
        <h2 className="font-semibold text-gray-800 dark:text-gray-100">
          Ingresos Totales {comitiva ? `de ${comitiva}` : 'de la comunidad'}
        </h2>
        <Tooltip className="ml-2" size="lg">
          <div className="text-sm">
            Muestra los ingresos de los últimos 6 meses para {comitiva || 'la comitiva seleccionada'}
          </div>
        </Tooltip>
      </header>
      <div className="px-5 py-3">
        <div className="flex items-start">
          <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mr-2">
            ${totalIncome.toLocaleString()}
          </div>
          <div 
            className={`text-sm font-medium px-1.5 rounded-full ${
              percentageChange >= 0 
                ? 'text-green-700 bg-green-500/20' 
                : 'text-red-700 bg-red-500/20'
            }`}
          >
            {percentageChange >= 0 ? '↑' : '↓'} {Math.abs(percentageChange)}%
          </div>
        </div>
      </div>
      <div className="grow px-5 pb-5">
        <div style={{ height: '248px' }}>
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

export default DashboardCard09;