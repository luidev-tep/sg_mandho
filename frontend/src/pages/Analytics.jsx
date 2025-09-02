import React, { useState } from 'react';
import { useParams } from 'react-router-dom';

import Sidebar from '../partials/SideBar';
import Header from '../partials/Header';
import Datepicker from '../components/Datepicker';
import AnalyticsCard11 from '../partials/analytics/AnalyticsCard11';
import AnaliticsButton from '../partials/analytics/AnalyticsButton';
import DashboardCard09 from '../partials/analytics/DashboardCard09';
import FintechCard09 from '../partials/analytics/FintechCard09';
import DashboardCard07 from '../partials/analytics/DashboardCard07';

function Analytics() {
 const [sidebarOpen, setSidebarOpen] = useState(false);
 const { comitiva } = useParams();

 // Función para obtener el título dinámico
 const getPageTitle = (comitiva) => {
   if (!comitiva) return "Analíticas y panel de control";
   
   const titles = {
     agua: "Panel de Control - Módulo Agua",
     panteon: "Panel de Control - Módulo Panteón",
     personas: "Panel de Control - Módulo Personas",
     delegacion: "Panel de Control - Módulo Delegación",
     feria: "Panel de Control - Módulo Feria"
   };
   
   return titles[comitiva] || `Panel de Control - ${comitiva.charAt(0).toUpperCase() + comitiva.slice(1)}`;
 };

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
               <Datepicker align="right" />
                
             </div>
          
           </div>            
          
           {/* DashboardCard09 en pantalla completa */}
           <div className="w-full mb-6">
             {/* Estos en pantalla completa - Pasar la comitiva como prop */}
             <AnaliticsButton comitiva={comitiva} />
             <br />
             {/* Mostrar los ingresos que hubieron cada mes  */}
             <DashboardCard09 />
             <br />
             <br />
             {/* Report card (Top Channels)  Mostrar un combinado de. EL numero de personas que hay en esa manza, el numero de clientes que deben el que ya pagaron y un porcentage
             asi como el 55% no pagaron y el 45% si pagaron*/}
              <DashboardCard07 />
             <br />
             <br />
               <FintechCard09 />
           </div>
          
           {/* Cards en grid normal */}
           <div className="grid grid-cols-12 gap-6">
             <AnalyticsCard11 />
           </div>
         </div>
       </main>
     </div>

   </div>
 );
}

export default Analytics;