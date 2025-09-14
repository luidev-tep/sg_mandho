//editarusuariomodal
import { useState, useEffect } from "react";
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { crearRegistroPago } from '../../api/pagos/api_crear_pago.js';
import { getAmount } from '../../api/pagos/api_get_costo_servicio.js';
import { useAuth } from "../../utils/AuthContext.jsx";
import { data } from "react-router-dom";

// Esquema de validación
const editSchema = yup.object().shape({
  cantidadRecibida: yup
    .number()
    .typeError('La cantidad debe ser un número válido')
    .required('La cantidad recibida es requerida')
    .positive('La cantidad debe ser positiva')
    .integer('La cantidad debe ser un número entero')
});

function FinishPayment({onClose, onUpdate, props }) {
  const { state } = useAuth();
  const { usuario } = state;
  const [isLoading, setIsLoading] = useState(true);
  const [fechaActual] = useState(new Date().toISOString().split('T')[0]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [amountTotal, setAmountTotal] = useState(0);
  const [cantidadFaltante, setCantidadFaltante] = useState(0);
  
  // Extraer datos de las props
  const {
    id,
    full_name,
    role_name,
    service_type,
    service_name,
    amount,
    dim_date,
    dim_customer_id,
    status_factura // Nueva prop para verificar el estado del pago
  } = props;

  // Verificar si el servicio ya está pagado
  const isAlreadyPaid = status_factura === 'completo';

  // Actualizar cantidad faltante cuando amountTotal cambie
  useEffect(() => {
    if (amountTotal && amount) {
      const faltante = amountTotal - amount;
      setCantidadFaltante(faltante > 0 ? faltante : 0);
    }
  }, [amountTotal, amount]);

  const { 
    register, 
    handleSubmit, 
    formState: { errors },
    reset,
    setError: setFormError,
    clearErrors
  } = useForm({
    resolver: yupResolver(editSchema)
  });
  //Se debe enviar un objeto con esta infromacion dentro 
useEffect(() => {
  const empaquetadorXD = {
  service_type: service_type,
  Year: dim_date,
  ServiceName: service_name
  };
  const data = {
    costoservicio: empaquetadorXD
  }

  getAmount(data)
    .then((amount) => {
      setAmountTotal(amount);
      setIsLoading(false);
    })
    .catch((error) => {
      console.error('Error obteniendo el monto total:', error);
      setError('Error al obtener el monto total del servicio');
      setIsLoading(false);
    });
  }, [ service_type, dim_date]);

  const validateAmount = (value) => {
    if (value > cantidadFaltante) {
      return 'La cantidad no puede exceder la cantidad faltante';
    }
    return true;
  };

  const onSubmit = async (data) => {
    // Validación adicional antes de enviar
    if (data.cantidadRecibida > cantidadFaltante) {
      setFormError('cantidadRecibida', {
        type: 'manual',
        message: 'La cantidad no puede exceder la cantidad faltante'
      });
      return;
    }

    if (data.cantidadRecibida <= 0) {
      setFormError('cantidadRecibida', {
        type: 'manual',
        message: 'La cantidad debe ser mayor a 0'
      });
      return;
    }

    try {
      if (!usuario) {
        throw new Error('No hay usuario logueado');
      }
      setIsSubmitting(true);
      clearErrors();

      const payload = {
        metodoPago: "efectivo",
        DIM_OnwerCustomerId: usuario.DIM_CustomerId,
        DIM_AccountId: id,
        DIM_CustomerId: dim_customer_id,
        ServiceName: service_name,
        fecha: fechaActual,
        serviceDetailsType: service_type,
        amount: amountTotal,
        AnioPago: dim_date,
        movementName: "ingreso",
        FactAmount: data.cantidadRecibida,
        entrada: '' //Se deja vacio ya que las validaciones solo se aplican a crear pagp
      };

      const response = await crearRegistroPago(payload);
      if (response && response.message === "Pago creado satisfactoriamente") {
        setSuccess(true);
        setTimeout(() => {
          // Extraer el objeto si la respuesta es un array como [{...}]
          const updatedData = Array.isArray(response.data) && response.data.length > 0
            ? response.data[0]
            : response.data;

          // Fusionar los datos originales (props) con los datos actualizados del backend
          const completeUpdatedRecord = { ...props, ...updatedData };

          if (onUpdate) {
            onUpdate(completeUpdatedRecord);
          }
          onClose();
        }, 2000);
        return;
      }
      const errorMessage = response?.message || response?.data?.message || 'Error desconocido al procesar el pago';
      throw new Error(errorMessage);
    } catch (err) {
      console.error('❌ Error en onSubmit:', err.message);
      let errorMessage = 'Error al procesar el pago';
      if (err.response) {
        errorMessage = err.response.data?.message || err.response.data?.error || err.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 shadow-xs rounded-xl relative max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <header className="px-5 py-4 sticky top-0 bg-white dark:bg-gray-800 z-10 border-b border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-gray-800 dark:text-gray-100">
              Terminar pago {service_name}
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

        <div className="p-5">
          {isLoading ? (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-100 rounded-lg">
              {error}
            </div>
          ) : isAlreadyPaid ? (
            // Mostrar mensaje cuando el servicio ya está pagado
            <div className="text-center py-8">
              <div className="bg-green-100 dark:bg-green-900/30 border border-green-400 dark:border-green-700 text-green-700 dark:text-green-100 rounded-lg p-6 mb-4">
                <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <h3 className="text-lg font-semibold mb-2">¡Servicio ya pagado!</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Este servicio ya fue pagado para {full_name}
                </p>
              </div>
              <button
                onClick={onClose}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800"
              >
                Cerrar
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
              {success && (
                <div className="mb-4 p-3 bg-green-100 dark:bg-green-900/30 border border-green-400 dark:border-green-700 text-green-700 dark:text-green-100 rounded-lg">
                  ¡Pago registrado correctamente! Cerrando...
                </div>
              )}
              
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-4 text-gray-800 dark:text-gray-100">Información del Cliente</h3>
                <div className="space-y-4 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Nombre completo</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {full_name}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Rol del cliente</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {role_name}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Servicio</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {service_name} - {service_type}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Monto pagado hasta ahora</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {amount.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Año de pago</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {dim_date}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Costo del servicio</label>
                      <p className="text-base font-medium text-gray-800 dark:text-gray-200 p-2 bg-white dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
                        {amountTotal.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-red-500 dark:text-red-400 mb-1">Cantidad faltante por pagar</label>
                      <p className="text-lg font-bold text-red-600 dark:text-red-400 p-2 bg-red-50 dark:bg-red-900/20 rounded-md border border-red-200 dark:border-red-700">
                        {cantidadFaltante.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <h3 className="text-lg font-medium text-gray-800 dark:text-gray-100">Registrar pago</h3>
                <div>
                  <label htmlFor="cantidadRecibida" className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    Cantidad a pagar
                  </label>
                  <input
                    type="number"
                    id="cantidadRecibida"
                    {...register('cantidadRecibida', {
                      validate: validateAmount
                    })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                  {errors.cantidadRecibida && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.cantidadRecibida.message}</p>
                  )}
                </div>
              </div>
            
              <div className="mt-6 flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  disabled={isSubmitting}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 disabled:opacity-50"
                  disabled={isSubmitting || success}
                >
                  {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default FinishPayment;