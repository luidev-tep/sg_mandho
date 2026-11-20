import { useState, useEffect } from "react";
import { GenerarReporteUsuario } from "../../api/api_user"; // Asegúrate de que la ruta sea correcta

// Componente para el botón de estado de cada año
function YearStatusButton({ year, status, details }) {
  const [isOpen, setIsOpen] = useState(false);

  const statusClasses = {
    completo: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-900/60',
    pendiente: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-900/60',
  };

  const detailStatusClasses = {
    completo: 'text-green-600 dark:text-green-400',
    pendiente: 'text-red-600 dark:text-red-400',
  };

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full text-left font-semibold px-3 py-2 rounded-lg transition-all duration-200 flex justify-between items-center ${statusClasses[status]}`}
      >
        <span>Año {year}</span>
        <svg className={`w-4 h-4 transform transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
      {isOpen && (
        <div className="mt-2 pl-4 border-l-2 border-gray-200 dark:border-gray-600 space-y-2 py-2">
          {details.map((detail, index) => (
            <div key={index} className="text-sm text-gray-700 dark:text-gray-300 flex justify-between">
              <span>• {detail.ServiceDetailesType} <span className="font-mono text-xs opacity-80">(${Number(detail.amount || 0).toFixed(2)})</span></span>
              <span className={`font-medium ${detailStatusClasses[detail.status]}`}>{detail.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Modal principal
function UserReportModal({ id_user, onClose }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    const processReportData = (apiData) => {
        if (!apiData) return {}; // Añadimos una validación por si apiData es nulo
        const allPayments = {}; // Estructura: { servicio: { año: { status: 'completo'|'pendiente', details: [] } } }

        const addPayment = (serviceName, payment, status) => {
            if (!payment || !payment.Year) return;
            const year = payment.Year;
            if (!allPayments[serviceName]) allPayments[serviceName] = {};
            if (!allPayments[serviceName][year]) allPayments[serviceName][year] = { details: [] };
            allPayments[serviceName][year].details.push({ ...payment, status });
        };

        // Procesar pagos completos. La API devuelve un array de pagos por servicio.
        Object.entries(apiData.completos || {}).forEach(([service, dataArray]) => {
            dataArray.forEach(payment => addPayment(service, payment, 'completo'));
        });
        // Procesar pendientes. La API devuelve un array de pagos por servicio.
        Object.entries(apiData.pendientes || {}).forEach(([service, dataArray]) => {
            dataArray.forEach(payment => addPayment(service, payment, 'pendiente'));
        });
        // Procesar pendientes sin facturar. La API devuelve un array de pagos por servicio.
        Object.entries(apiData.pendientes_sin_facturar || {}).forEach(([service, dataArray]) => {
            dataArray.forEach(payment => addPayment(service, payment, 'pendiente'));
        });

        // Determinar el estado final de cada año
        Object.values(allPayments).forEach(service => {
            Object.values(service).forEach(yearData => {
                const hasPending = yearData.details.some(d => d.status === 'pendiente');
                yearData.status = hasPending ? 'pendiente' : 'completo';
            });
        });
        return allPayments;
    };
    
    const fetchReport = async () => {
      if (!id_user) {
        setError("ID de usuario no proporcionado.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const response = await GenerarReporteUsuario(id_user);
        
        // CORRECCIÓN APLICADA AQUÍ
        if (response && response.data) {
          const processedData = processReportData(response.data);
          setReportData(processedData);
        } else {
          throw new Error("La respuesta de la API no contiene la propiedad 'data' o no es válida.");
        }
      } catch (err) {
        setError(err.message || "Error al generar el reporte.");
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [id_user]);

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl transform transition-all animate-scale-in">
        {/* Encabezado */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Reporte de Pagos del Usuario
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {loading && (
            <div className="flex justify-center items-center h-48">
              <svg className="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          )}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-700 dark:text-red-300">{error}</div>
          )}
          {reportData && (
            <div className="space-y-6">
              {Object.keys(reportData).length > 0 ? (
                Object.entries(reportData).map(([serviceName, yearsData]) => (
                  <div key={serviceName}>
                    <h4 className="font-bold text-lg uppercase tracking-wider text-gray-700 dark:text-gray-300 mb-3 pb-2 border-b-2 border-gray-200 dark:border-gray-600">
                      Servicio {serviceName}
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(yearsData)
                        .sort(([yearA], [yearB]) => parseInt(yearB) - parseInt(yearA)) // Ordenar años descendente
                        .map(([year, data]) => (
                          <YearStatusButton key={year} year={year} status={data.status} details={data.details} />
                        ))
                      }
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-500 dark:text-gray-400">
                  <p>No se encontraron datos de pagos para este usuario.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Pie */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl flex justify-end">
          <button onClick={onClose} className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}

export default UserReportModal;