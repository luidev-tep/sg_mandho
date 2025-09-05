import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import Sidebar from '../partials/SideBar';
import Header from '../partials/Header';
import DateSelect from '../partials/analytics/DateSelect';
import AnalyticsCard11 from '../partials/analytics/AnalyticsCard11';
import AnaliticsButton from '../partials/analytics/AnalyticsButton';
import DashboardCard09 from '../partials/analytics/DashboardCard09';
import FintechCard09 from '../partials/analytics/FintechCard09';
import DashboardCard07 from '../partials/analytics/DashboardCard07';
import FintechIntro from '../partials/analytics/FintechIntro';
import DashboardCard10 from '../partials/analytics/DashboardCard10';

function Analytics() {
 const [sidebarOpen, setSidebarOpen] = useState(false);
 const { comitiva } = useParams();
 const [mes, setMes] = useState('');

 // Función para obtener el título dinámico
 const getPageTitle = (comitiva) => {
   if (!comitiva) return "Analíticas y panel de control";
   
   const titles = {
     agua: "Panel de Control - Comitiva Agua",
     panteon: "Panel de Control - Comitiva Panteón",
     personas: "Panel de Control - Modulo Personas",
     delegacion: "Panel de Control - Comitiva Delegación",
     feria: "Panel de Control - Comitiva Feria"
   };
   
   return titles[comitiva] || `Panel de Control - ${comitiva.charAt(0).toUpperCase() + comitiva.slice(1)}`;
 };

 // Función para manejar el cambio de filtro de fecha
 const handleDateFilterChange = (selectedMonth) => {
   setMes(selectedMonth); // selectedMonth ya viene en formato 'M01', 'M02', etc.
 };

 // Efecto para establecer el mes anterior como filtro por defecto al montar el componente
 useEffect(() => {
   const today = new Date();
   const currentMonth = today.getMonth(); // 0-11
   
   // Calcular el mes anterior
   let previousMonth = currentMonth; // Como currentMonth es 0-11, ya representa el mes anterior al actual
   if (previousMonth === 0) {
     previousMonth = 11; // Si estamos en enero, el mes anterior es diciembre
   } else {
     previousMonth = currentMonth - 1;
   }
   
   // Formatear como 'M01', 'M02', etc.
   const defaultMonth = `M${String(previousMonth + 1).padStart(2, '0')}`;
   setMes(defaultMonth);
 }, []);

 return (
   <div className="flex h-[100dvh] overflow-hidden">

     {/* Sidebar */}
     <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

     {/* Content area */}
     <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">

       {/*  Site header */}
       <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

       <main className="grow">
         <div className="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-[96rem] mx-auto">

           {/* Page header */}
           <div className="sm:flex sm:justify-between sm:items-center mb-8">
          
             {/* Left: Title */}
             <div className="mb-4 sm:mb-0">
               <h1 className="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">
                 {getPageTitle(comitiva)}
               </h1>
             </div>
        
             {/* Right: Actions */}
             <div className="grid grid-flow-col sm:auto-cols-max justify-start sm:justify-end gap-2">
                
               {/* Datepicker built with React Day Picker */}
               <DateSelect align="right" onFilterChange={handleDateFilterChange} />
                
             </div>
          
           </div>            
          
           {/* DashboardCard09 en pantalla completa */}
           <div className="w-full mb-6">
            {/* \Dar la bienvenida al ususario dependiendo de el que se introduzca */}
             <FintechIntro comitiva={comitiva} mes={mes} mes_format={mes_format}/>
             <br />
             <br />
             {/* Estos en pantalla completa - Pasar la comitiva como prop */}
             <AnaliticsButton comitiva={comitiva} mes={mes} mes_format= {mes_format}/>
             <br />
             {/* Mostrar los ingresos que hubieron cada mes  */}
             <DashboardCard09 comitiva={comitiva} mes={mes} mes_format = {mes_format}/>
              
             <br />
             <br />
              {/* Mostrar los ingresos que hubieron cada manzana mensual  */}
             <DashboardCard10 comitiva={comitiva} mes={mes} mes_format = {mes_format} />
             <br />
             <br />
             {/* Report card (Top Channels)  Mostrar un combinado de. EL numero de personas que hay en esa manza, el numero de clientes que deben el que ya pagaron y un porcentage
             asi como el 55% no pagaron y el 45% si pagaron*/}
              <DashboardCard07 comitiva={comitiva} mes={mes}  mes_format = {mes_format} />
             <br />
             <br />
               <FintechCard09 comitiva={comitiva} mes={mes} mes_format = {mes_format} />
           </div>
          
           {/* Cards en grid normal */}
           <div className="grid grid-cols-12 gap-6">
             <AnalyticsCard11 comitiva={comitiva} mes={mes} mes_format = {mes_format}/>
           </div>
         </div>
       </main>
     </div>

   </div>
 );
}

export default Analytics;