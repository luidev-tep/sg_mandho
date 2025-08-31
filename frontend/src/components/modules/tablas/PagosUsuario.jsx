
// Componente corregido:
import React, { useState, useEffect } from 'react';
import { MostrarPagos } from '../../../api/pagos/api_mostrar_pago';
import PaymentItem from './PagosUsuarioItem';

function PaymentsTableModal({ id_user, serviceName, onClose , service_type, Year}) {
  const [pagos, setPagos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectAll, setSelectAll] = useState(false);
  const [isCheck, setIsCheck] = useState([]);

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
      
      console.log('Filtros para pagos:', filters);
      const response = await MostrarPagos(filters);
      
      console.log('Respuesta del backend:', response);
      
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

  const handleSelectAll = () => {
    setSelectAll(!selectAll);
    setIsCheck(selectAll ? [] : pagos.map(pago => pago.FACT_RevenueId));
  };

  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectAll(false);
    setIsCheck(checked 
      ? [...isCheck, id] 
      : isCheck.filter(item => item !== id)
    );
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center py-8">Cargando pagos...</div>;
    }

    if (error) {
      return (
        <>
          <div className="text-center py-8 text-red-500">Error: {error}</div>
          <button 
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded mx-auto block"
          >
            Cerrar
          </button>
        </>
      );
    }

    // Obtener el nombre del cliente del primer pago (si existe)
    const clienteNombre = pagos.length > 0 
      ? `${pagos[0].CustomerName || ''} ${pagos[0].CustomerMiddleName || ''} ${pagos[0].CustomerLastName || ''} ${pagos[0].CustomerSecondLastName || ''}`
      : '';

    return (
      <>
        {/* Nombre del cliente fuera de la tabla */}
        {clienteNombre && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-200">
              Cliente: {clienteNombre}
            </h3>
          </div>
        )}
        
        <table className="table-auto w-full dark:text-gray-300">
          <thead className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-t border-b border-gray-100 dark:border-gray-700/60">
            <tr>
              <th className="px-3 py-3 whitespace-nowrap w-10">
                <div className="flex items-center justify-center">
                  <label className="inline-flex">
                    <span className="sr-only">Select all</span>
                    <input 
                      className="form-checkbox" 
                      type="checkbox" 
                      checked={selectAll} 
                      onChange={handleSelectAll} 
                      disabled={pagos.length === 0}
                    />
                  </label>
                </div>
              </th>
              <th className="px-4 py-3 whitespace-nowrap text-left">
                <div className="font-semibold">Estado</div>
              </th>
              <th className="px-4 py-3 whitespace-nowrap text-left">
                <div className="font-semibold">Monto</div>
              </th>
              <th className="px-4 py-3 whitespace-nowrap text-left">
                <div className="font-semibold">Fecha</div>
              </th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-gray-100 dark:divide-gray-700/60">
            {pagos.length > 0 ? (
              pagos.map(pago => (
                <PaymentItem
                  key={pago.FACT_RevenueId}
                  FACT_RevenueId={pago.FACT_RevenueId}
                  StatusFactura={pago.StatusFactura}
                  amount={pago.amount}
                  DIM_DateId={pago.DIM_DateId}
                  handleClick={handleClick}
                  isChecked={isCheck.includes(pago.FACT_RevenueId)}
                />
              ))
            ) : (
              <tr>
                <td colSpan="4" className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No se encontraron pagos para este servicio
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 shadow-xs rounded-xl relative max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        <header className="px-5 py-4 sticky top-0 bg-white dark:bg-gray-800 z-10 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">
              Pagos del Servicio: <span className="text-blue-600 dark:text-blue-400 font-medium capitalize">
                {serviceName}
              </span>
              <span className="text-gray-400 dark:text-gray-500 font-medium ml-2">
                ({pagos.length})
              </span>
            </h2>
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              aria-label="Cerrar modal"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </header>
        
        <div className="p-4">
          <div className="overflow-x-auto">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentsTableModal;