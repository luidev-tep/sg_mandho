import React from 'react';

function AccountTableItem(props) {
  // Mapeo de estados de factura con colores
  const statusStyles = {
    'pagado': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'pendiente': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'vencida': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'default': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  };

  return (
    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
      {/* Checkbox */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap w-px">
        <div className="flex items-center">
          <label className="inline-flex">
            <span className="sr-only">Select</span>
            <input 
              id={props.FACT_RevenueId} 
              className="form-checkbox h-4 w-4" 
              type="checkbox" 
              onChange={props.handleClick} 
              checked={props.isChecked} 
            />
          </label>
        </div>
      </td>
      
      {/* Estado de Factura con fondo de color */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className={`text-center text-sm font-medium px-3 py-1 rounded-full ${statusStyles[props.StatusFactura?.toLowerCase()] || statusStyles['default']}`}>
          {props.StatusFactura}
        </div>
      </td>
      
      {/* Monto */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className="text-right text-sm font-medium">
          ${props.amount}
        </div>
      </td>
      
      {/* Fecha */}
      <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
        <div className="text-center text-sm">
          {props.DIM_DateId}
        </div>
      </td>
    </tr>
  );
}

export default AccountTableItem;