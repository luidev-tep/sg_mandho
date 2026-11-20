import { useState, useEffect } from "react";
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { capitalizeFirstLetter } from "../../utils/stringUtils";
import { MostrarUsuarios } from "../../api/api_user";
import { EditarUsuario } from "../../api/api_user";
import { MostrarCuentas } from '../../api/api_account';
import FormattedErrorMessage from "../alertas/FormattedErrorMessage";
import ConfirmationModal from "../Modalmessaje";
import { getLocalDateISO } from "../../utils/dateUtils";

// Esquema de validación
const editSchema = yup.object().shape({
  CustomerFraction: yup.string()
    .required('La manzana es requerida')
    .oneOf([
      'tepetate',
      'cerritos',
      'garambullo',
      'yhonda',
      'centro',
      'buenavista'
    ], 'Seleccione una manzana válida'),

  CustomerAddress: yup.string()
    .required('La calle es requerida')
    .transform(value => value ? value.trim() : value)
    .test('no-cero', 'El valor "0" no es permitido', value => value !== '0')
    .test('no-negative', 'No se permiten números negativos', value => {
      return !/^-?\d+$/.test(value);
    }),

  CustomerNumberExt: yup.string()
    .transform(value => {
      if (!value || value.trim() === '') return 's/n';
      return value.trim();
    })
    .test(
      'valid-format',
      'Debe ser solo números positivos o "s/n"',
      (value) => {
        return /^\d+$/.test(value) || value.toLowerCase() === 's/n';
      }
    )
    .test('no-negative', 'No se permiten números negativos', (value) => {
      return !/^-\d+$/.test(value);
    }),

  DIM_RoleId: yup.string()
    .nullable()
    .notRequired()
    .oneOf([
      'Estudiante', 'Inmigrante', 'Pequeño propietario',
      'Vecino', 'Ranchero', 'Invalido', 'Residente', 'Vecino exento', null
    ], 'Estado no válido'),
});

function EditCustomerModal({ id_user, onClose, onUpdate }) {
  // Estados
  const [customer, setCustomer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fechaActual] = useState(() => getLocalDateISO());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [originalRoleId, setOriginalRoleId] = useState(null);
  const [hasActiveAccount, setHasActiveAccount] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [pendingData, setPendingData] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  // Form hook
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm({
    resolver: yupResolver(editSchema)
  });

  // Opciones
  const fractionOptions = [
    { value: 'tepetate', label: 'Tepetate' },
    { value: 'cerritos', label: 'Cerritos' },
    { value: 'garambullo', label: 'Garambullo' },
    { value: 'yhonda', label: 'Yhonda' },
    { value: 'centro', label: 'Centro' },
    { value: 'buenavista', label: 'Buenavista' },
  ];

  const roleOptions = [
    { value: 'Estudiante', label: 'Estudiante' },
    { value: 'Inmigrante', label: 'Inmigrante' },
    { value: 'Pequeño propietario', label: 'Pequeño propietario' },
    { value: 'Vecino', label: 'Vecino' },
    { value: 'Ranchero', label: 'Ranchero' },
    { value: 'Invalido', label: 'Invalido' },
    { value: 'Residente', label: 'Residente' },
    { value: 'Vecino exento', label: 'Vecino exento' }
  ];

  // Cargar datos del usuario al montar el componente
  useEffect(() => {
    const fetchCustomer = async () => {
      setIsLoading(true);
      setError(null);
      setIsAdmin(false);

      if (!id_user) {
        setError('ID de usuario no proporcionado');
        setIsLoading(false);
        return;
      }

      try {
        const filters = {
          'id_user': id_user,
          'filters': {}
        };

        const response = await MostrarUsuarios(filters);
        const responseaccount = await MostrarCuentas(filters);

        if (response?.success && responseaccount?.success) {
          const activeAccount = responseaccount.data.body.find(account =>
            account.DIM_StatusId?.toLowerCase() === 'activo'
          );

          if (activeAccount) {
            setHasActiveAccount(true);
            const capitalizedRole = activeAccount.DIM_RoleId
              ? capitalizeFirstLetter(activeAccount.DIM_RoleId)
              : activeAccount.DIM_RoleId;

            setOriginalRoleId(capitalizedRole || null);

            const adminRoles = ['delegado', 'comitiva', 'subdelegado', 'administrador'];
            if (activeAccount.DIM_RoleId &&
              adminRoles.includes(activeAccount.DIM_RoleId.toLowerCase())) {
              setIsAdmin(true);
            }
          } else {
            setHasActiveAccount(false);
            setOriginalRoleId(null);
          }

          const customerData = response.data;
          setCustomer(customerData);

          reset({
            DIM_CustomerId: customerData.DIM_CustomerId,
            CustomerFraction: customerData.CustomerFraction,
            CustomerAddress: customerData.CustomerAddress,
            CustomerNumberExt: customerData.CustomerNumberExt,
            DIM_AccountId: activeAccount ? activeAccount.DIM_AccountId : null,
            DIM_StatusId: activeAccount ? activeAccount.DIM_StatusId : '',
            ...(activeAccount && {
              DIM_RoleId: activeAccount.DIM_RoleId
                ? capitalizeFirstLetter(activeAccount.DIM_RoleId)
                : activeAccount.DIM_RoleId
            }),
          });
        } else {
          throw new Error('Cliente no encontrado');
        }
      } catch (err) {
        setError(err.message || "Error al cargar los datos del cliente");
        console.error("Error fetching customer:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCustomer();
  }, [id_user, reset]);

  // Función que muestra el modal de confirmación (se ejecuta al submit del form)
  const submitForm = (data) => {
    if (isSubmitting) return;
    setPendingData(data);
    setShowConfirmModal(true);
  };

  // Función que se ejecuta cuando el usuario CONFIRMA en el modal
  const handleConfirmUpdate = async () => {
    if (!pendingData) return;

    setShowConfirmModal(false);
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const payload = {
        DIM_CustomerId: customer.DIM_CustomerId,
        CustomerAddress: pendingData.CustomerAddress,
        CustomerNumberExt: pendingData.CustomerNumberExt,
        CustomerFraction: pendingData.CustomerFraction,
        estadoPersona: hasActiveAccount ? pendingData.DIM_RoleId.toLowerCase() : false,
        fechaCuenta: hasActiveAccount ? fechaActual : false,
        EstadoPersonaOriginal: hasActiveAccount ? originalRoleId.toLowerCase() : false
      };

      // CORRECCIÓN: Llamada a la API que faltaba
      const response = await EditarUsuario(payload);

      if (response && response.success) {
        if (onUpdate) {
          onUpdate(response.data);
        }
        setSuccess(true);
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        const errorMessage = response?.message ||
                            response?.data?.message ||
                            "Error al actualizar el usuario";
        throw new Error(errorMessage);
      }
    } catch (err) {
      setError(err.message || "Error al guardar los cambios");
    } finally {
      setIsSubmitting(false);
      setPendingData(null);
    }
  };

  // Función para cerrar el modal de confirmación
  const handleCloseConfirmModal = () => {
    setShowConfirmModal(false);
    setPendingData(null);
  };

  // Construir el mensaje del modal de confirmación
  const getConfirmationMessage = () => {
    if (!customer) return '¿Estás seguro de que deseas guardar los cambios?';
    
    const fullName = `${customer.CustomerName} ${customer.CustomerLastName}`;
    return `¿Estás seguro de que deseas modificar los datos de ${fullName}?`;
  };

return (
  // Contenedor principal: centra el modal y añade el fondo oscuro
  <div className="fixed inset-0 bg-black/50 flex justify-center items-center p-2 sm:p-4 z-50">
    {/* Panel del modal: ahora con altura máxima y flexbox vertical */}
    <div
      className="bg-white dark:bg-gray-800 shadow-xs rounded-xl relative w-full max-w-4xl max-h-[90vh] flex flex-col"
      // NUEVO: Detiene la propagación del clic para evitar que el modal se cierre accidentalmente.
      onClick={(e) => e.stopPropagation()}
    >
      {/* Encabezado: no se encoge y ya no es "sticky" */}
      <header className="px-3 sm:px-5 py-3 sm:py-4 bg-white dark:bg-gray-800 z-10 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="flex justify-between items-center">
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            Editar Usuario
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            aria-label="Cerrar modal"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </header>

      {/* Contenido principal: ahora es el contenedor con scroll */}
      <div className="p-3 sm:p-5 overflow-y-auto">
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
          </div>
        ) : error ? (
                    <FormattedErrorMessage message={error} />
        ) : customer ? (
          isAdmin ? (
            <div>
              <div className="mb-6 p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/50 border border-yellow-200 dark:border-yellow-700 text-yellow-900 dark:text-white rounded-lg">
                <h3 className="text-base sm:text-lg font-bold mb-2">
                  Usuario Administrador
                </h3>
                <p className="text-sm sm:text-base">
                  No se pueden modificar los datos de un usuario administrador (delegado, comitiva, subdelegado).
                </p>
              </div>

              <div className="mt-8 flex justify-center">
                <button
                  onClick={onClose}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors"
                >
                  Salir
                </button>
              </div>
            </div>
          ) : (
          <form onSubmit={handleSubmit(submitForm)}>
            {success && (
              <div className="mb-4 p-3 bg-green-100 dark:bg-green-900/50 border border-green-400 dark:border-green-700 text-green-900 dark:text-white rounded-lg text-sm sm:text-base">
                ¡Usuario actualizado correctamente! Cerrando...
              </div>
            )}

            <div className="mb-6">
              <h3 className="text-base sm:text-lg font-medium mb-4 text-gray-900 dark:text-white">Información del Cliente</h3>

              <div className="space-y-3 sm:space-y-4 bg-gray-50 dark:bg-gray-700/50 p-3 sm:p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Fecha de Registro</label>
                    <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-white p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                      {customer.CustomerStartDate}
                    </p>
                  </div>
                  <div>
                    <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Fecha de Nacimiento</label>
                    <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-white p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                      {customer.CustomerDateBirth}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Nombre Completo</label>
                  <p className="text-sm sm:text-base font-medium text-gray-900 dark:text-white p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700 break-words">
                    {customer.CustomerName}
                    {customer.CustomerMiddleName ? ` ${customer.CustomerMiddleName}` : ''}
                    {` ${customer.CustomerLastName} ${customer.CustomerSecondLastName}`}
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3 sm:space-y-4">
              <h3 className="text-base sm:text-lg font-medium text-gray-900 dark:text-white">Datos de Dirección</h3>

              <div>
                <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-300 mb-1" htmlFor="CustomerFraction">
                  Manzana <span className="text-red-500">*</span>
                </label>
                <select
                  id="CustomerFraction"
                  className={`form-select w-full rounded-lg py-2 sm:py-2.5 text-sm sm:text-base ${errors.CustomerFraction ? 'border-red-500' : 'border-gray-300'} dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white`}
                  {...register("CustomerFraction")}
                  disabled={isSubmitting || success}
                >
                  <option value="">Seleccionar manzana</option>
                  {fractionOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {errors.CustomerFraction && (
                  <p className="mt-1 text-xs sm:text-sm text-red-600 dark:text-red-400">{errors.CustomerFraction.message}</p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-300 mb-1" htmlFor="CustomerAddress">
                    Calle <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="CustomerAddress"
                    className={`form-input w-full rounded-lg py-2 sm:py-2.5 text-sm sm:text-base ${errors.CustomerAddress ? 'border-red-500' : 'border-gray-300'} dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white`}
                    type="text"
                    {...register("CustomerAddress")}
                    disabled={isSubmitting || success}
                  />
                  {errors.CustomerAddress && (
                    <p className="mt-1 text-xs sm:text-sm text-red-600 dark:text-red-400">{errors.CustomerAddress.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-300 mb-1" htmlFor="CustomerNumberExt">
                    Número Exterior <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="CustomerNumberExt"
                    className={`form-input w-full rounded-lg py-2 sm:py-2.5 text-sm sm:text-base ${errors.CustomerNumberExt ? 'border-red-500' : 'border-gray-300'} dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white`}
                    type="text"
                    {...register("CustomerNumberExt")}
                    disabled={isSubmitting || success}
                  />
                  {errors.CustomerNumberExt && (
                    <p className="mt-1 text-xs sm:text-sm text-red-600 dark:text-red-400">{errors.CustomerNumberExt.message}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-base sm:text-lg font-medium pt-4 text-gray-900 dark:text-white">Detalles de la Cuenta</h3>

              {hasActiveAccount ? (
                <div className="mb-4 mt-2">
                  <label className="block text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-300 mb-1">
                    Estado de la persona <span className="text-red-500">*</span>
                  </label>
                  <select
                    className={`form-select w-full rounded-lg py-2 sm:py-2.5 text-sm sm:text-base border-gray-300 dark:bg-gray-700 dark:border-gray-600 text-gray-900 dark:text-white`}
                    {...register("DIM_RoleId")}
                    disabled={isSubmitting || success}
                  >
                    <option value="">Seleccionar estado</option>
                    {roleOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  {errors.DIM_RoleId && (
                    <p className="mt-1 text-xs sm:text-sm text-red-600 dark:text-red-400">{errors.DIM_RoleId.message}</p>
                  )}
                </div>
              ) : (
                <div className="p-3 bg-yellow-100 dark:bg-yellow-900/50 border border-yellow-400 dark:border-yellow-700 text-yellow-900 dark:text-white rounded-lg mt-2 text-sm sm:text-base">
                  Este usuario no tiene cuentas activas. La sección de estado de persona está deshabilitada.
                </div>
              )}
            </div>

            <div className="mt-6 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="w-full sm:w-auto px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 text-sm sm:text-base"
                disabled={isSubmitting}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 disabled:opacity-50 text-sm sm:text-base"
                disabled={isSubmitting || success}
              >
                {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </form>
          )
        ) : (
          <div className="p-3 sm:p-4 bg-yellow-100 dark:bg-yellow-900/50 border border-yellow-400 dark:border-yellow-700 text-yellow-900 dark:text-white rounded-lg text-sm sm:text-base">
            No se encontraron datos del cliente
          </div>
        )}
      </div>
    </div>
        <ConfirmationModal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          onConfirm={handleConfirmUpdate}
          title="Confirmar Edición de Usuario"
          message={`¿Estás seguro de que deseas guardar los cambios?`}
          confirmText="Sí, guardar cambios"
          cancelText="Cancelar"
          variant="info"
          icon="question"
          isProcessing={isSubmitting}
          />
  </div>
);
}

export default EditCustomerModal;