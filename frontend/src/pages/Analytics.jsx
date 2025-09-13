import React, { useState, useEffect, useCallback } from 'react';
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
import { GetAnalytics } from '../api/api_analiticas';
import { useAuth } from '../utils/AuthContext';

function Analytics() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { comitiva } = useParams();
  const [mes, setMes] = useState('');
  const [anio, setAnio] = useState(new Date().getFullYear().toString());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estados para los datos de los componentes - Corregido: dataCountUsers inicializado con estructura correcta
  const [dashboardData, setDashboardData] = useState({
    dataIncomes: null,
    dataFractions: null,
    dataUserBills: { manzanas: [] },
    dataCountUsers: { manzanas: [] },
    dataServiceMembers: null
  });

  const { state: authState } = useAuth();

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
  const handleDateFilterChange = (dateData) => {
    if (dateData) {
      setMes(dateData.month);
      setAnio(dateData.year);
    }
  };

  // Función para formatear el mes de 'M01' a 'Enero', 'M02' a 'Febrero', etc.
  const formatMonth = (monthCode) => {
    if (!monthCode) return '';
    
    const months = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    
    // Extraer el número del mes (eliminar la 'M' y convertir a número)
    const monthNumber = parseInt(monthCode.substring(1), 10) - 1;
    
    // Validar que el número de mes sea válido
    if (monthNumber >= 0 && monthNumber < months.length) {
      return months[monthNumber];
    }
    
    return monthCode; // Retornar el código original si no es un mes válido
  };

  // Obtener el mes formateado
  const mesFormateado = formatMonth(mes);

  // Efecto para establecer el mes anterior como filtro por defecto al montar el componente
  useEffect(() => {
    const today = new Date();
    const currentMonth = today.getMonth(); // 0-11
    
    // Calcular el mes anterior
    let previousMonth = currentMonth;
    if (previousMonth === 0) {
      previousMonth = 11;
    } else {
      previousMonth = currentMonth - 1;
    }
    
    const defaultMonth = `M${String(previousMonth + 1).padStart(2, '0')}`;
    setMes(defaultMonth);
  }, []);

  // Función para obtener datos analíticos con useCallback
  const fetchAnalyticsData = useCallback(async () => {
    if (!mes || !comitiva || !authState.usuario) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await GetAnalytics({
        comitiva: comitiva,
        mes: mes,
        anio: anio,
        usuario: authState.usuario.DIM_AccountId
      });
      
      // console.log("Datos recibidos:", response);
      if (response) {
        // Transformar dataCountUsers - YA VIENE EN EL FORMATO CORRECTO
        const formattedDataCountUsers = response.dataCountUsers || { manzanas: [] };

        // Transformar dataUserBills - YA VIENE EN EL FORMATO CORRECTO
        const formattedDataUserBills = response.dataUserBills || { manzanas: [] };

        // Crear nuevas instancias de arrays para forzar actualización
        setDashboardData({
          dataIncomes: response.dataIncomes ? [...response.dataIncomes] : [],
          dataFractions: response.dataFractions ? [...response.dataFractions] : [],
          dataUserBills: formattedDataUserBills,
          dataCountUsers: formattedDataCountUsers,
          dataServiceMembers: response.dataServiceMembers ? [...response.dataServiceMembers] : []
        });
        console.log("Datos recibidos:", response);
      }
    } catch (err) {
      console.error('Error al cargar datos analíticos:', err);
      setError('Error al cargar los datos. Por favor, intente de nuevo.');
    } finally {
      setLoading(false);
    }
  }, [mes, comitiva, authState.usuario, anio]);

  // Efecto para cargar datos cuando cambia el mes o la comitiva
  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

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
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}
              
              <FintechIntro comitiva={comitiva} mes_format={mesFormateado}/>
              <br />
              <br />
              
              <AnaliticsButton comitiva={comitiva} mes_format={mesFormateado}/>
              <br />
              
              <DashboardCard09 
                comitiva={comitiva} 
                mes_format={mesFormateado} 
                data={dashboardData.dataIncomes}
                loading={loading}
              />
               
              <br />
              <br />
              
              <DashboardCard10 
                comitiva={comitiva} 
                mes_format={mesFormateado} 
                data={dashboardData.dataFractions}
                loading={loading}
              />
              <br />
              <br />
              
              {/* DashboardCard07 recibe dataUserBills que ya tiene el formato correcto */}
              <DashboardCard07 
                comitiva={comitiva} 
                mes_format={mesFormateado} 
                data={dashboardData.dataUserBills}
                anio={anio}
                loading={loading}
              />

              <br />
              <br />

              {/* FintechCard09 recibe dataCountUsers que ya tiene el formato correcto */}
              <FintechCard09 
                comitiva={comitiva} 
                mes_format={mesFormateado}
                data={dashboardData.dataCountUsers}
                loading={loading}
              />
              <br />
              <br />

            </div>
            
            {/* Cards en grid normal */}
            <div className="grid grid-cols-12 gap-6">
              <AnalyticsCard11 
                comitiva={comitiva} 
                mes_format={mesFormateado} 
                data={dashboardData.dataServiceMembers}
                loading={loading}
              />
            </div>
          </div>
        </main>
      </div>

    </div>
  );
}

export default Analytics;