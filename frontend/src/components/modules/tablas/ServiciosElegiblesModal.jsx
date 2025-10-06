import { useState, useMemo, useEffect } from "react";
import { crearRegistroPago } from '../../../api/pagos/api_crear_pago';
import { useAuth } from "../../../utils/AuthContext";
import Notification from "../../ui/Notification";

function ServiciosElegiblesModal({ ServiceDetailType, users, serviceName, onClose, onSuccess }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [expandedFractions, setExpandedFractions] = useState({});
  const { state } = useAuth();
  const { usuario } = state;
  const [notification, setNotification] = useState({ show: false, message: '', type: 'success' });

  // Función unificada para cerrar el modal
  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  const handleSelectUser = (accountId) => {
    setSelectedUsers(prevSelected => {
      const newSelection = prevSelected.includes(accountId)
        ? prevSelected.filter(id => id !== accountId)
        : [...prevSelected, accountId];
      
      return newSelection;
    });
  };

  const groupedUsers = useMemo(() => {
    if (!users) return {};
    return users.reduce((acc, user) => {
      const fraction = user.CustomerFraction || 'Sin Zona';
      if (!acc[fraction]) {
        acc[fraction] = [];
      }
      acc[fraction].push(user);
      return acc;
    }, {});
  }, [users]);

  const toggleFraction = (fraction) => {
    setExpandedFractions(prev => ({
      ...prev,
      [fraction]: !prev[fraction]
    }));
  };

  const handleSelectAllFraction = (fraction, isChecked) => {
    const usersInFraction = groupedUsers[fraction].map(u => u.DIM_AccountId);
    setSelectedUsers(prevSelected => {
      if (isChecked) {
        // Añadir usuarios de la fracción, evitando duplicados
        return [...new Set([...prevSelected, ...usersInFraction])];
      } else {
        // Quitar usuarios de la fracción
        return prevSelected.filter(id => !usersInFraction.includes(id));
      }
    });
  };
 
  const handleConfirm = async () => {
    setIsSubmitting(true);
    setNotification({ show: false, message: '', type: 'success' });

    if (!usuario || !usuario.DIM_ServiceOwnersId) {
      setNotification({ show: true, message: "Error: No se pudo obtener el ID del propietario. Vuelva a iniciar sesión.", type: 'error' });
      setIsSubmitting(false);
      return;
    }

    const anioActual = new Date().getFullYear();

    const payloads = selectedUsers.map(accountId => {
      const user = users.find(u => u.DIM_AccountId === accountId);
      if (!user) return null;

      return {
        DIM_AccountId: user.DIM_AccountId,
        DIM_CustomerId: user.DIM_CustomerId,
        ServiceName: serviceName,
        DIM_OnwerCustomerId: usuario.DIM_ServiceOwnersId,
        serviceDetailsType: ServiceDetailType,
        amount: 0,
        AnioPago: anioActual,
        FactAmount: 0, // Como se indicó, este valor es 0
        movementName: "ingreso", // Valor por defecto
        entrada: 'check_list' // Valor por defecto
      };
    }).filter(Boolean); // Filtramos por si algún usuario no se encontró

    console.log("Payloads a enviar:", payloads);

    try {
      // Enviamos todos los payloads en una sola petición
      const response = await crearRegistroPago(payloads);
      if (response.success) {
        setNotification({ show: true, message: response.message || "Registros creados exitosamente.", type: 'success' });
        setTimeout(() => {
          onSuccess(); // Llama a la función para recargar la tabla
          handleClose();   // Cierra el modal usando la función unificada
        }, 2000); // Espera 2 segundos antes de cerrar
      } else {
        throw new Error(response.message || "Ocurrió un error en el servidor.");
      }
    } catch (error) {
      console.error("Error al crear uno o más registros de pago:", error);
      setNotification({ show: true, message: error.message || "Error al crear los registros.", type: 'error' });
    } finally {
      // Solo se detiene el spinner, el cierre se maneja en el success
      if (!notification.show || notification.type === 'error') {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh] transform transition-all animate-scale-in">
        {/* Encabezado */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Usuarios elegibles para <span className="text-indigo-500">{serviceName}</span>
          </h3>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
            disabled={isSubmitting}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6 overflow-y-auto">
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            <p>Selecciona los usuarios a los que se les aplicará el pago. Total de personas: <span className="font-bold text-gray-800 dark:text-gray-200">{users.length}</span></p>
          </div>

          {/* Acordeón de usuarios por zona */}
          <div className="space-y-2">
            {Object.keys(groupedUsers).sort().map(fraction => {
              const isExpanded = !!expandedFractions[fraction];
              const usersInFraction = groupedUsers[fraction];
              const allInFractionSelected = usersInFraction.every(u => selectedUsers.includes(u.DIM_AccountId));

              return (
                <div key={fraction} className="border border-gray-200 dark:border-gray-700 rounded-lg">
                  {/* Encabezado del acordeón */}
                  <button
                    className="w-full flex justify-between items-center p-3 text-left bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700/80"
                    onClick={() => toggleFraction(fraction)}
                  >
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        className="h-5 w-5 text-indigo-600 dark:text-indigo-500 border-gray-300 dark:border-gray-600 rounded focus:ring-indigo-500 mr-3"
                        checked={allInFractionSelected}
                        onChange={(e) => handleSelectAllFraction(fraction, e.target.checked)}
                        onClick={(e) => e.stopPropagation()} // Evita que el acordeón se cierre al hacer clic en el checkbox
                      />
                      <span className="font-semibold text-gray-800 dark:text-gray-200 capitalize">{fraction}</span>
                      <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">({usersInFraction.length} usuarios)</span>
                    </div>
                    <svg className={`w-5 h-5 text-gray-500 dark:text-gray-400 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>

                  {/* Contenido del acordeón (lista de usuarios) */}
                  {isExpanded && (
                    <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                      <ul className="space-y-2">
                        {usersInFraction.map(user => (
                          <li key={user.DIM_AccountId} className="flex items-center p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                            <input
                              type="checkbox"
                              className="h-5 w-5 text-indigo-600 dark:text-indigo-500 border-gray-300 dark:border-gray-600 rounded focus:ring-indigo-500 mr-3"
                              checked={selectedUsers.includes(user.DIM_AccountId)}
                              onChange={() => handleSelectUser(user.DIM_AccountId)}
                            />
                            <div className="flex-grow text-sm text-gray-800 dark:text-gray-200">
                              {`${user.CustomerName} ${user.CustomerMiddleName !== 'n/a' ? user.CustomerMiddleName : ''} ${user.CustomerLastName} ${user.CustomerSecondLastName}`}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">{user.RoleName}</div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Pie */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl mt-auto border-t border-gray-100 dark:border-gray-700">
          {notification.show && (
            <div className="mb-3">
              <Notification
                type={notification.type}
                message={notification.message}
                onClose={() => setNotification({ ...notification, show: false })}
              />
            </div>
          )}
          <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-3 space-y-2 sm:space-y-0">
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="w-full sm:w-auto px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={isSubmitting || selectedUsers.length === 0}
            className="w-full sm:w-auto px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 dark:hover:bg-indigo-800 transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Procesando...
              </>
            ) : (
              `Confirmar (${selectedUsers.length})`
            )}
          </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ServiciosElegiblesModal;