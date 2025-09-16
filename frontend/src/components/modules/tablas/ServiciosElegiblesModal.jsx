import { useState } from "react";
import { crearRegistroPago } from '../../../api/pagos/api_crear_pago';
import { getAmount } from '../../../api/pagos/api_get_costo_servicio';
import { useAuth } from "../../../utils/AuthContext";
function ServiciosElegiblesModal({ ServiceDetailType, users, serviceName, onClose, onSuccess }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const { state } = useAuth();
  const { usuario } = state;
  const handleSelectUser = (accountId) => {
    setSelectedUsers(prevSelected => {
      const newSelection = prevSelected.includes(accountId)
        ? prevSelected.filter(id => id !== accountId)
        : [...prevSelected, accountId];
      
      return newSelection;
    });
  };

  const handleConfirm = async () => {
    setIsSubmitting(true);
    
    if (!usuario || !usuario.DIM_CustomerId) {
      console.error("Error: No se pudo obtener el ID del propietario (usuario logueado).");
      setIsSubmitting(false);
      // Aquí podrías mostrar un mensaje de error al usuario.
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
        DIM_OnwerCustomerId: usuario.DIM_CustomerId,
        serviceDetailsType: ServiceDetailType,
        amount: 0,
        AnioPago: anioActual,
        FactAmount: 0, // Como se indicó, este valor es 0
        movementName: "ingreso", // Valor por defecto
        entrada: 'crear_pago' // Valor por defecto
      };
    }).filter(Boolean); // Filtramos por si algún usuario no se encontró

    console.log("Payloads a enviar:", payloads);

    try {
      // Enviamos todos los payloads en paralelo
      //await Promise.all(payloads.map(payload => crearRegistroPago(payload)));
      console.log("Todos los registros de pago se crearon exitosamente.");
      onSuccess(); // Llama a la función para recargar la tabla
    } catch (error) {
      console.error("Error al crear uno o más registros de pago:", error);
      // Aquí podrías manejar el error, por ejemplo, mostrando una notificación.
    } finally {
      setIsSubmitting(false);
      onClose();
    }
  };

//Amount debe ser 0, al igual que fact amount, ya que estos pagos no se crearan  
//LA para enviar los datos a la api debe tener estos campos
        // Validación corregida de campos requeridos
        // if (
        // !data.DIM_AccountId = la cuenta del registro
        // || 
        // !data.DIM_CustomerId || = el id del cliente
        //  !data.ServiceName || = el n0ombre del servicio (ejemplo agua, panteon, delegacion, etc)
        //  !data.DIM_OnwerCustomerId || el id del propietario 
        // !data.serviceDetailsType || =  el nombre del tipo de servicio
        //  !data.amount  || debe ser 0 
        //  !data.AnioPago || anio actual 
        //  !data.FactAmount || la que viene de la funcion get amount


  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-2xl transform transition-all animate-scale-in">
        {/* Encabezado */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Usuarios elegibles para <span className="text-indigo-500">{serviceName}</span>
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
            disabled={isSubmitting}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          <div className="mb-4 text-sm text-gray-600 dark:text-gray-400">
            <p>Selecciona los usuarios a los que se les aplicará el pago. Total de personas: <span className="font-bold text-gray-800 dark:text-gray-200">{users.length}</span></p>
          </div>

          {/* Tabla de usuarios */}
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="p-2 whitespace-nowrap w-10">
                    {/* Checkbox para seleccionar todos (funcionalidad futura) */}
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-left">Nombre</div>
                  </th>
                  <th className="p-2 whitespace-nowrap">
                    <div className="font-semibold text-left">Rol</div>
                  </th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-gray-100 dark:divide-gray-700">
                {users.map((user) => (
                  <tr key={user.DIM_AccountId}>
                    <td className="p-2 whitespace-nowrap text-center">
                      <input
                        type="checkbox"
                        className="h-4 w-4 text-indigo-600 dark:text-indigo-500 border-gray-300 dark:border-gray-600 rounded focus:ring-indigo-500"
                        checked={selectedUsers.includes(user.DIM_AccountId)}
                        onChange={() => handleSelectUser(user.DIM_AccountId)}
                      />
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-left text-gray-800 dark:text-gray-200">
                        {`${user.CustomerName} ${user.CustomerMiddleName !== 'n/a' ? user.CustomerMiddleName : ''} ${user.CustomerLastName} ${user.CustomerSecondLastName}`}
                      </div>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <div className="text-left font-medium text-gray-600 dark:text-gray-400">{user.RoleName}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pie */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={isSubmitting || selectedUsers.length === 0}
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 dark:hover:bg-indigo-800 transition-colors disabled:opacity-50 flex items-center"
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
  );
}

export default ServiciosElegiblesModal;