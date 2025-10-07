//_En: PagosUsuarioItem.js_
//_Descripción: Componente hijo que renderiza cada fila de pago. Ahora es completamente responsivo._

import React from 'react';

function PaymentItem({ StatusFactura, amount, DIM_DateId }) {
  const statusInfo = {
    'pagado': { text: 'Pagado', color: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300' },
    'pendiente': { text: 'Pendiente', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300' },
    'vencido': { text: 'Vencido', color: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300' },
    'default': { text: StatusFactura || 'Desconocido', color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' }
  };

  const statusKey = StatusFactura ? String(StatusFactura).toLowerCase() : 'default';
  const { text, color } = statusInfo[statusKey] || statusInfo.default;

  return (
    // Contenedor principal: se comporta como columna en móvil y fila en pantallas 'sm' o más grandes.
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
      
      {/* Estado */}
      <div className="flex items-center justify-between sm:w-1/3 mb-2 sm:mb-0">
        <span className="sm:hidden text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Estado</span>
        <span className={`inline-flex font-medium rounded-full text-center px-2.5 py-0.5 text-sm ${color}`}>
          {text}
        </span>
      </div>

      {/* Monto */}
      <div className="flex items-center justify-between sm:w-1/3 mb-2 sm:mb-0">
        <span className="sm:hidden text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Monto</span>
        <span className="font-medium text-gray-800 dark:text-gray-200">${amount.toFixed(2)}</span>
      </div>

      {/* Fecha */}
      <div className="flex items-center justify-between sm:w-1/3">
        <span className="sm:hidden text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Fecha</span>
        <span className="text-sm text-gray-600 dark:text-gray-300">{DIM_DateId}</span>
      </div>
      
    </div>
  );
}

export default PaymentItem;