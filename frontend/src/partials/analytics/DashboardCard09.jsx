//DashboardCard09
import React, { useEffect, useState } from 'react';
import BarChart from '../../charts/BarChart02';
import Tooltip from '../../components/Tooltip';
import { getCssVariable } from '../../utils/Utils';

function DashboardCard09({ comitiva, mes_format, data, loading }) {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Ingresos',
        data: [],
        backgroundColor: getCssVariable('--color-violet-500'),
        hoverBackgroundColor: getCssVariable('--color-violet-600'),
        barPercentage: 0.7,
        categoryPercentage: 0.7,
        borderRadius: 4,
      },
    ],
  });

  //console.log("Dayos recibidos en el compoennte hijo: ", data )
  const [chartKey, setChartKey] = useState(0);

  // Efecto para actualizar chartData cuando cambian los datos
  useEffect(() => {
    if (data && Array.isArray(data) && data.length > 0) {
      // Ordenar y procesar datos
      const sortedData = [...data].sort((a, b) => {
        const [aMonth, aYear] = a.month.split('-').map(Number);
        const [bMonth, bYear] = b.month.split('-').map(Number);
        return aYear - bYear || aMonth - bMonth;
      });

      const labels = sortedData.map(item => {
        const [month, year] = item.month.split('-');
        return `${month}-01-${year}`;
      });

      const amounts = sortedData.map(item => item.amount);

      const newChartData = {
        labels,
        datasets: [
          {
            label: 'Ingresos',
            data: amounts,
            backgroundColor: getCssVariable('--color-violet-500'),
            hoverBackgroundColor: getCssVariable('--color-violet-600'),
            barPercentage: 0.7,
            categoryPercentage: 0.7,
            borderRadius: 4,
          },
        ],
      };

      setChartData(newChartData);
      setChartKey(prevKey => prevKey + 1); // Incrementar la clave para forzar re-render de BarChart
    } else {
      // Resetear datos
      const emptyChartData = {
        labels: [],
        datasets: [
          {
            label: 'Ingresos',
            data: [],
            backgroundColor: getCssVariable('--color-violet-500'),
            hoverBackgroundColor: getCssVariable('--color-violet-600'),
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
  const totalIngresos = data?.reduce((sum, item) => sum + (item.amount || 0), 0) || 0;

  // Calcular el cambio porcentual respecto al mes anterior
  const calcularCambioPorcentual = () => {
    if (!data || data.length < 2) return 0;
    
    // Ordenar datos de más reciente a más antiguo
    const sortedData = [...data].sort((a, b) => {
      const [aMonth, aYear] = a.month.split('-').map(Number);
      const [bMonth, bYear] = b.month.split('-').map(Number);
      return bYear - aYear || bMonth - aMonth;
    });
    
    const ultimoMes = sortedData[0].amount;
    const penultimoMes = sortedData[1].amount;
    
    if (penultimoMes === 0) return 0;
    
    return Math.round(((ultimoMes - penultimoMes) / penultimoMes) * 100);
  };

  const cambioPorcentual = calcularCambioPorcentual();

  if (loading) {
    return (
      <div className="flex flex-col col-span-full sm:col-span-6 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
        <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
          <h2 className="font-semibold text-gray-800 dark:text-gray-100 text-2x1">Ingresos Totales {comitiva ? `de ${comitiva}` : 'de la comunidad'}</h2>
        </header>
        <div className="px-5 py-3">
          <div className="flex items-start">
            <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mr-2">Cargando...</div>
          </div>
        </div>
        <div className="grow">
          <div className="h-60 w-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500"></div>
          </div>
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
            Visualización de los ingresos por mes para {comitiva || 'la comitiva seleccionada'}
          </div>
        </Tooltip>
      </header>
      <div className="px-5 py-3">
        <div className="flex items-start">
          <div className="text-3xl font-bold text-gray-800 dark:text-gray-100 mr-2">
            ${totalIngresos.toLocaleString()}
          </div>
          {cambioPorcentual !== 0 && (
            <div className={`text-sm font-medium px-1.5 rounded-full ${
              cambioPorcentual >= 0 
                ? 'text-green-700 bg-green-500/20' 
                : 'text-red-700 bg-red-500/20'
            }`}>
              {cambioPorcentual >= 0 ? '↑' : '↓'} {Math.abs(cambioPorcentual)}%
            </div>
          )}
        </div>
      </div>
      <div className="grow">
        {data && data.length > 0 ? (
          <BarChart key={chartKey} data={chartData} width={595} height={248} />
        ) : (
          <div className="h-60 w-full flex items-center justify-center">
            <div className="text-gray-500 dark:text-gray-400">No hay datos disponibles</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardCard09;