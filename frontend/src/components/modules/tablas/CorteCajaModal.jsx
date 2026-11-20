import React, { useState, useEffect } from 'react';
import { Get_servicios_disponibles } from '../../../api/pagos/api_get_costo_servicio';
import { CorteDeCaja } from '../../../api/pagos/api_crear_pago';
import { useAuth } from '../../../utils/AuthContext';
import PasswordVerificationModal from '../../ModalValitePass';

function CorteCajaModal({ serviceName, serviceDetailTypes, onClose, onSuccess }) {
  const [availableServices, setAvailableServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [finalMessage, setFinalMessage] = useState({ show: false, type: '', text: '' });
  const { state } = useAuth();
  const { usuario } = state;

  useEffect(() => {
    const fetchAvailableServices = async () => {
      if (serviceDetailTypes.length === 0) {
        setError("No hay servicios en la vista actual para generar un corte.");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const payload = {
          servicios_corte_caja: {
            "DIM_ServiceDetailesType": serviceDetailTypes,
            "DIM_service": serviceName
          }
        };
        const response = await Get_servicios_disponibles(payload);

        if (response.success && response.data && response.data.length > 0) {
          setAvailableServices(response.data);
        } else {
          setError(response.message || "No se encontraron servicios disponibles para generar el corte.");
        }

      } catch (err) {
        console.error("Error al obtener servicios para corte de caja:", err);
        setError(err.message || "Ocurrió un error al cargar los datos.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAvailableServices();
  }, [serviceName, serviceDetailTypes]);

  const handleConfirmClick = () => {
    if (!selectedService) {
      setError("Por favor, seleccione un tipo de servicio para continuar.");
      return;
    }
    // Mostrar el modal de contraseña
    setShowPasswordModal(true);
  };

  const handlePasswordVerificationSuccess = async () => {
    if (!usuario || !usuario.DIM_ServiceOwnersId) {
      setError("No se pudo obtener el ID del usuario. Por favor, inicie sesión de nuevo.");
      return;
    }

    setIsConfirming(true);
    setShowPasswordModal(false);
    setError(null);

    try {
      const payload = {
        "DIM_ServiceDetailesType": selectedService,
        "DIM_ServiceOwnersId": usuario.DIM_ServiceOwnersId,
        "DIM_service": serviceName
      };

      const response = await CorteDeCaja(payload);
      
      if (response.success && (response.status === 200 || response.status === 201)) {
        setFinalMessage({ show: true, type: 'success', text: response.message || 'Corte de caja generado exitosamente.' });
        setTimeout(() => {
          if (onSuccess) onSuccess();
          onClose();
        }, 2000);
      } else {
        throw new Error(response.message || "La respuesta del servidor no fue exitosa.");
      }

    } catch (err) {
      console.error("Error al generar el corte de caja:", err);
      const errorMessage = err.message || "Ocurrió un error al generar el corte.";
      setFinalMessage({ show: true, type: 'error', text: errorMessage });
      setTimeout(() => {
        setFinalMessage({ show: false, type: '', text: '' });
      }, 3000);
    } finally {
      setIsConfirming(false);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center p-4">Cargando servicios disponibles...</div>;
    }

    if (finalMessage.show) {
      const isSuccess = finalMessage.type === 'success';
      const bgColor = isSuccess ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30';
      const textColor = isSuccess ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300';
      return (
        <div className={`p-4 text-center rounded-md ${bgColor} ${textColor}`}>
          {finalMessage.text}
        </div>
      );
    }

    if (error && !finalMessage.show) {
      return <div className="p-4 text-center text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">{error}</div>;
    }

    if (availableServices.length > 0) {
      return (
        <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
          {availableServices.map(([id, tipo]) => (
            <label key={id} className="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors">
              <input type="radio" name="service-selection" className="form-radio h-4 w-4 text-indigo-600" value={tipo} onChange={(e) => setSelectedService(e.target.value)} />
              <span className="ml-3 flex-grow text-gray-800 dark:text-gray-200 capitalize">{tipo}</span>
            </label>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-sm transform transition-all animate-scale-in">
          {/* Encabezado */}
          <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Generar Corte de Caja
            </h3>
          </div>

          {/* Cuerpo */}
          <div className="p-6">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Terminar el servicio <span className="font-bold text-indigo-500">{serviceName}</span>.
              Seleccione el tipo de servicio sobre el cual desea terminar la operación.
            </p>
            {renderContent()}
          </div>

          {/* Pie */}
          <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={isConfirming || finalMessage.show}
              className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirmClick}
              disabled={isLoading || isConfirming || !selectedService || error || finalMessage.show}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:bg-indigo-400 disabled:cursor-not-allowed flex items-center"
            >
              {isConfirming ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Procesando...
                </>
              ) : (
                'Confirmar Corte'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Modal de verificación de contraseña */}
      {showPasswordModal && (
        <PasswordVerificationModal
          onClose={() => setShowPasswordModal(false)}
          onVerificationSuccess={handlePasswordVerificationSuccess}
          title="Confirmar acción"
          message={`Esta acción finalizará el servicio '${selectedService}' para '${serviceName}'. Se requiere su contraseña para confirmar la acción.`}
          verificationType="owner"
        />
      )}
    </>
  );
}

export default CorteCajaModal;