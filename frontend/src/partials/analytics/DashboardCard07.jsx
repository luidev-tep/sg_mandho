import React from 'react';

// Agrega esta función al inicio del componente, antes del return:
const getTrimestreYMes = (fecha) => {
  const meses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];
  
  const [mes, anio] = fecha.split(' ');
  const mesIndex = meses.findIndex(m => m.toLowerCase() === mes.toLowerCase());
  const trimestre = Math.floor(mesIndex / 3) + 1;
  
  return `Año ${anio} - Trimestre ${trimestre} (${mes})`;
};

function DashboardCard07({ comitiva, mes_format, data, loading }) {
 return (
   <div className="col-span-full xl:col-span-8 bg-white dark:bg-gray-800 shadow-xs rounded-xl">
     <header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">
       <h2 className="font-semibold text-gray-800 dark:text-gray-100">
         {comitiva} - {getTrimestreYMes(mes_format)}
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
           <tbody className="text-sm font-medium divide-y divide-gray-100 dark:divide-gray-700/60">
             {data && data.manzanas ? data.manzanas.map((manzana) => (
               <tr key={manzana.id}>
                 <td className="p-2">
                   <div className="flex items-center">
                     <svg className="shrink-0 mr-2 sm:mr-3" width="36" height="36" viewBox="0 0 36 36">
                       <circle fill={manzana.color} cx="18" cy="18" r="18" />
                       <path
                         d="M14.232 12.818V23H11.77V12.818h2.46zM15.772 23V12.818h2.462v4.087h4.012v-4.087h2.456V23h-2.456v-4.092h-4.012V23h-2.461z"
                         fill="#E6ECF4"
                       />
                     </svg>
                     <div className="text-gray-800 dark:text-gray-100">{manzana.nombre}</div>
                   </div>
                 </td>
                 <td className="p-2">
                   <div className="text-center">{manzana.personas}</div>
                 </td>
                 <td className="p-2">
                   <div className="text-center text-green-500">{manzana.pagados}</div>
                 </td>
                 <td className="p-2">
                   <div className="text-center">{manzana.pendientes}</div>
                 </td>
                 <td className="p-2">
                   <div className="text-center text-sky-500">{manzana.porcentaje}%</div>
                 </td>
               </tr>
             )) : (
               <tr>
                 <td colSpan="5" className="p-4 text-center text-gray-500">
                   {loading ? 'Cargando...' : 'No hay datos disponibles'}
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

export default DashboardCard07;