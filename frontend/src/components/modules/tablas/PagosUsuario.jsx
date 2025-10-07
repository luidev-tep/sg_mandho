
// Componente corregido:
import React, { useState, useEffect, useMemo } from 'react';
import { MostrarPagos } from '../../../api/pagos/api_mostrar_pago';
import PaymentItem from './PagosUsuarioItem';

function PaymentsTableModal({ id_user, serviceName, onClose , service_type, Year}) {
  const [pagos, setPagos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPagos = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
      const filters = {
        "DIM_CustomerId": id_user,
        "serviceName": serviceName,
        "service_type": service_type,
        'Year': Year
      };
      
      //console.log('Filtros para pagos:', filters);
      const response = await MostrarPagos(filters);
      
      //console.log('Respuesta del backend:', response);
      
      // CORRECCIÓN: Verificar la estructura de la respuesta correctamente
      if (response?.success === "success" && Array.isArray(response.data)) {
        setPagos(response.data);
      } else if (response?.success === "success" && !Array.isArray(response.data)) {
        // Si success es "success" pero data no es array, usar array vacío
        setPagos([]);
      } else {
        if (response?.message && response.success !== "success") {
          throw new Error(response.message);
        }
        setPagos([]);
      }
    } catch (err) {
      console.error("Error fetching pagos:", err);
      if (!err.message.includes("No se encontraron pagos")) {
        setError(err.message);
      }
      setPagos([]);
    } finally {
      setIsLoading(false);
    }
  };

    if (id_user && serviceName) {
      fetchPagos();
    } else {
      setIsLoading(false);
      setPagos([]);
    }
  }, [id_user, serviceName]);

  // Memoizamos el nombre del cliente para evitar recálculos innecesarios
  const clienteNombre = useMemo(() => {
    if (pagos.length > 0) {
      const cliente = pagos[0];
      // Filtramos los 'n/a' y unimos los nombres
      return [cliente.CustomerName, cliente.CustomerMiddleName, cliente.CustomerLastName, cliente.CustomerSecondLastName]
        .filter(name => name && name.toLowerCase() !== 'n/a')
        .join(' ');
    }
    return '';
  }, [pagos]);

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center py-10 text-gray-500 dark:text-gray-400">Cargando pagos...</div>;
    }

    // Obtener el nombre del cliente del primer pago (si existe)
    const clienteNombre = pagos.length > 0 
      ? `${pagos[0].CustomerName || ''} ${pagos[0].CustomerMiddleName || ''} ${pagos[0].CustomerLastName || ''} ${pagos[0].CustomerSecondLastName || ''}`
      : '';

    return (
      <>
        {/* Encabezado de la lista (visible en pantallas md y superiores) */}
        <div className="hidden md:grid grid-cols-3 gap-4 px-4 py-2 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/20 rounded-t-lg">
          <div className="text-left">Estado</div>
          <div className="text-left">Monto</div>
          <div className="text-left">Fecha</div>
        </div>

        {/* Lista de pagos */}
        <div className="space-y-2 md:space-y-0">
          {pagos.length > 0 ? (
            pagos.map(pago => (
              <PaymentItem
                key={pago.FACT_RevenueId}
                StatusFactura={pago.StatusFactura}
                amount={pago.amount}
                DIM_DateId={pago.DIM_DateId}
              />
            ))
          ) : (
            <div className="text-center py-10 text-gray-500 dark:text-gray-400">
              {error ? `Error: ${error}` : 'No se encontraron pagos para este servicio y año.'}
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh] transform transition-all animate-scale-in">
        {/* Encabezado del Modal */}
        <header className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-start justify-between">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Pagos de <span className="text-indigo-500 capitalize">{serviceName}</span>
              </h3>
              {clienteNombre && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Cliente: <span className="font-medium text-gray-700 dark:text-gray-300">{clienteNombre}</span>
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300 px-2.5 py-1 rounded-full">
              {Year}
            </span>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
              aria-label="Cerrar modal"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </header>
        
        {/* Cuerpo del Modal (con scroll) */}
        <div className="p-4 sm:p-6 overflow-y-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default PaymentsTableModal;