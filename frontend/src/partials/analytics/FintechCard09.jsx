import React from 'react';
import PieChart from '../../charts/PieChart';

// Import utilities
import { getCssVariable } from '../../utils/Utils';

function FintechCard09() {

 const chartData = {
   labels: ['Centro', 'Tepetetate', 'Yhonda', 'Buenavista', 'Garambullo', 'Cerritos'],
   datasets: [
     {
       label: 'Población por Manzana',
       data: [95, 126, 143, 327, 204, 78],
       backgroundColor: [
         getCssVariable('--color-green-400'),
         getCssVariable('--color-yellow-400'),
         getCssVariable('--color-sky-500'),
         getCssVariable('--color-violet-500'),
         getCssVariable('--color-red-400'),
         getCssVariable('--color-orange-400'),
       ],
       hoverBackgroundColor: [
         getCssVariable('--color-green-500'),
         getCssVariable('--color-yellow-500'),
         getCssVariable('--color-sky-600'),
         getCssVariable('--color-violet-600'),
         getCssVariable('--color-red-500'),
         getCssVariable('--color-orange-500'),
       ],
       borderWidth: 0,
     },
   ],
 };

 return (
   <div className="flex flex-col col-span-full sm:col-span-6 xl:col-span-4 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
     <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60 flex items-center">
       <h2 className="font-semibold text-gray-800 dark:text-gray-100">Población por Manzana</h2>
     </header>
     <div className="px-5 py-3">
       <div className="text-sm italic mb-2">Distribución de habitantes por manzana:</div>
       <div className="text-3xl font-bold text-gray-800 dark:text-gray-100">863 personas</div>
     </div>
     {/* Chart built with Chart.js 3 */}
     {/* Change the height attribute to adjust the chart height */}
     <PieChart data={chartData} width={389} height={220} />
   </div>
 );
}

export default FintechCard09;