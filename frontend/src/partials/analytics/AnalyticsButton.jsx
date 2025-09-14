import React from 'react';
import { Link } from 'react-router-dom';
import ModuleButton from './ModuleBoton';

function AnalyticsButton({ comitiva }) {
 const moduleOptionsMap = {
   panteon: [
     { path: "/modulos/generar_reporte/panteon", label: "Generar Reporte", isReport: true },
     { path: "/modulos/panteon", label: "Ver Registros" },
     { path: "/modulos/crear_pago/panteon", label: "Generar Registro" },
     { path: "/modulos/usuarios/panteon", label: "Ver Personas" },
     { path: "/modulos/crear_servicio/panteon", label: "Agregar servicio" }
   ], 
   personas: [
     { path: "/modulos/generar_reporte/personas", label: "Generar Reporte", isReport: true },
     { path: "/personas/usuarios", label: "Lista de personas" },
     { path: "/cuentas/cuenta", label: "Crear cuenta" },
     { path: "/personas/registro", label: "Agregar persona" },
     { path: "/modulos/crear_servicio/personas", label: "Agregar servicio" }
   ],
   agua: [
     { path: "/modulos/generar_reporte/agua", label: "Generar Reporte", isReport: true },
     { path: "/modulos/agua", label: "Ver pagos" },
     { path: "/modulos/crear_pago/agua", label: "Generar recibo" },
     { path: "/modulos/usuarios/agua", label: "Ver Personas" },
     { path: "/modulos/crear_servicio/agua", label: "Agregar servicio" }
   ],
   delegacion: [
     { path: "/modulos/generar_reporte/delegacion", label: "Generar Reporte", isReport: true },
     { path: "/modulos/delegacion", label: "Ver registros" },
     { path: "/modulos/crear_pago/delegacion", label: "Generar recibo" },
     { path: "/modulos/usuarios/delegacion", label: "Ver Personas" },
     { path: "/modulos/crear_servicio/delegacion", label: "Agregar servicio" }
   ],
   feria: [
     { path: "/modulos/generar_reporte/feria", label: "Generar Reporte", isReport: true },
     { path: "/modulos/feria", label: "Ver registros" },
     { path: "/modulos/crear_pago/feria", label: "Generar recibo" },
     { path: "/modulos/usuarios/feria", label: "Ver Personas" },
     { path: "/modulos/crear_servicio/feria", label: "Agregar servicio" }
   ]
 };

 // Si no hay comitiva especificada, mostrar los módulos generales
 const defaultModules = [
   { path: "/modulos/panteon", label: "Módulo Panteón" },
   { path: "/modulos/agua", label: "Módulo Pago Agua" },
   { path: "/modulos/delegacion", label: "Módulo Delegación" },
   { path: "/personas/usuarios", label: "Módulo de Personas" },
   { path: "/modulos/feria", label: "Módulo Feria" }
 ];

 const modulesToRender = comitiva ? moduleOptionsMap[comitiva] || [] : defaultModules;

 return (
   <div className="col-span-full bg-white dark:bg-gray-800 shadow-xs rounded-xl">
<header className="px-5 py-4 border-b border-gray-100 dark:border-gray-700/60">

<h2 className="font-bold text-3xl text-gray-800 dark:text-gray-100"> {comitiva ? `Comitiva ${comitiva.charAt(0).toUpperCase() + comitiva.slice(1)}` : 'Comitivas del Pueblo'} </h2> </header>
     <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
       {modulesToRender.map((module, index) => (
         module.isReport ? (
           <Link
             key={index}
             to={module.path}
             className="flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
           >
             {module.label}
           </Link>
         ) : (
           <ModuleButton key={index} to={module.path}>
             {module.label}
           </ModuleButton>
         )
       ))}
     </div>
   </div>
 );
}

export default AnalyticsButton;