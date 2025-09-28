import React from 'react';

function AccountTableItem(props) {
  // Mapeo de estados de factura con colores mejorados para modo light/dark
  const statusStyles = {
    'completo': {
      bg: 'bg-green-100 dark:bg-green-900',
      text: 'text-green-800 dark:text-green-200'
    },
    'pendiente': {
      bg: 'bg-yellow-100 dark:bg-yellow-900',
      text: 'text-yellow-800 dark:text-yellow-200'
    },
    'vencida': {
      bg: 'bg-red-100 dark:bg-red-900',
      text: 'text-red-800 dark:text-red-200'
    },
    'default': {
      bg: 'bg-gray-100 dark:bg-gray-700',
      text: 'text-gray-800 dark:text-gray-300'
    }
  };

  const status = props.StatusFactura?.toLowerCase();
  const style = statusStyles[status] || statusStyles['default'];

  return (
    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
      
      {/* Estado de Factura con fondo de color */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className={`text-center text-sm font-medium px-3 py-1 rounded-full ${style.bg} ${style.text}`}>
          {props.StatusFactura}
        </div>
      </td>
      
      {/* Monto */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className="text-right text-sm font-medium text-gray-900 dark:text-white">
          ${props.amount}
        </div>
      </td>
      
      {/* Fecha */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className="text-center text-sm text-gray-900 dark:text-white">
          {props.DIM_DateId}
        </div>
      </td>
    </tr>
  );
}

export default AccountTableItem;