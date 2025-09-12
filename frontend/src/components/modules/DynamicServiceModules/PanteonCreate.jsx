import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

const DynamicPanteonPaymentComponent = ({ onValidityChange, onModuleData, paymentData }) => {
  const { register, handleSubmit, watch, setValue, formState: { errors, isValid } } = useForm({
    mode: 'onChange',
    defaultValues: {
      serviceType: '',
      amount: 0,
      serviceName: 'panteon',
      description: ''
    }
  });

  const serviceType = watch('serviceType');
  const amount = watch('amount');
  const description = watch('description');
  const [selectedServiceInfo, setSelectedServiceInfo] = useState(null);

  useEffect(() => {
    onValidityChange?.(isValid);
  }, [isValid, onValidityChange]);

  useEffect(() => {
    if (isValid) {
      onModuleData?.({
        serviceType,
        amount,
        serviceName: 'panteon',
        description
      });
    }
  }, [serviceType, amount, description, isValid, onModuleData]);

  useEffect(() => {
    if (serviceType && paymentData) {
      const selected = paymentData.find(p => p.serviceType === serviceType);
      if (selected) {
        setValue('amount', selected.amount, { shouldValidate: true });
        const newDescription = `Pago por ${selected.serviceType.replace('_', ' ')} del año seleccionado.`;
        setValue('description', newDescription);
        setSelectedServiceInfo(selected);
      }
    } else {
      setValue('amount', 0);
      setValue('description', '');
      setSelectedServiceInfo(null);
      setValue('serviceName', 'panteon');
    }
  }, [serviceType, paymentData, setValue]);

  return (
    <div className="space-y-4 bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Campo: Tipo de servicio */}
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 mb-2">
            Tipo de servicio <span className="text-red-500">*</span>
          </label>
          <select
            {...register('serviceType', { required: true })}
            className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed"
            disabled={!paymentData || paymentData.length === 0}
          >
            <option value="">-- Seleccione un servicio --</option>
            {paymentData?.map(service => (
              <option key={service.serviceType} value={service.serviceType}>
                {`${service.serviceType.charAt(0).toUpperCase() + service.serviceType.slice(1)} - $${service.amount}`}
              </option>
            ))}
          </select>
          {errors.serviceType && (
            <p className="text-red-500 text-sm mt-1">Este campo es requerido</p>
          )}
        </div>

        {/* Campo: Cantidad */}
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 mb-2">
            Costo del servicio
          </label>
          <div className="relative">
            <input
              type="number"
              {...register('amount')}
              readOnly
              className="w-full px-4 py-2 border rounded-lg bg-gray-100 dark:bg-gray-600 cursor-not-allowed dark:border-gray-600 dark:text-gray-300"
              placeholder="Costo se asigna al seleccionar"
            />
          </div>
          {errors.amount && (
            <p className="text-red-500 text-sm mt-1">Este campo es requerido</p>
          )}
        </div>

        {/* Campo oculto: serviceName */}
        <input type="hidden" {...register('serviceName')} />

        {/* Campo: Descripción */}
        <div className="mb-4 md:col-span-2">
          <label className="block text-gray-700 dark:text-gray-300 mb-2">
            Descripción
          </label>
          <textarea
            {...register('description')}
            className="w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
            rows={2}
          />
        </div>
      </div>
    </div>
  );
};

export default DynamicPanteonPaymentComponent;