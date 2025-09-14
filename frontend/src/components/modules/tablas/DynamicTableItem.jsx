// partials/customers/CustomersTableItem.jsx
import React from 'react';
import Image01 from '../../../images/user-40-01.jpg';
import Image03 from '../../../images/user-40-03.jpg';
import ActionMenu from './ActionMenu';
import { formatCurrency } from '../../../utils/Utils';

function DynamicTableItem(props) {
    const imageMap = {
        'Image01': Image01,
        // 'Image02': Image02, // Ejemplo de cómo agregar más
        // 'Image03': Image03,
    };

    // Determinar qué imagen usar basado props.status_account
    const getImage = () => {
        if (props.status_account && props.status_account.toLowerCase() === 'inactivo') {
            return Image03; // Usuario inactivo
        }
        return imageMap[props.image] || Image01; // Usuario activo o imagen por defecto
    };

    const userImage = getImage();

    // Estilo base para la tarjeta/fila
    const baseClasses = `
        bg-white dark:bg-gray-800
        shadow-md rounded-lg mb-4 p-4 
        md:grid md:grid-cols-8 md:gap-4 md:items-center md:p-0 md:shadow-none md:rounded-none md:mb-0
        transition-all duration-200
    `;

    // Clases condicionales para el estado 'inactivo'
    const inactiveClasses = props.status_account && props.status_account.toLowerCase() === 'inactivo'
        ? `
            border-l-4 border-amber-500 dark:border-amber-400 
            bg-amber-50 dark:bg-amber-900/20
            md:border-0 md:bg-amber-100 md:dark:bg-amber-900/20
          `
        : 'border-l-4 border-transparent';

    return (
        <div className={`${baseClasses} ${inactiveClasses}`}>
            {/* --- Vista de Tarjeta para Móvil --- */}
            <div className="md:hidden grid grid-cols-3 gap-4">
                {/* Columna 1: Imagen */}
                <div className="col-span-1 flex items-center">
                    <img className="rounded-full w-16 h-16" src={userImage} alt={props.full_name} />
                </div>

                {/* Columna 2: Nombre y Rol */}
                <div className="col-span-2 flex flex-col justify-center">
                    <div className="font-bold text-lg text-gray-800 dark:text-gray-100">{props.full_name}</div>
                    <div className="text-sm text-sky-600 dark:text-sky-400">{props.role_name}</div>
                </div>

                {/* Detalles adicionales */}
                <div className="col-span-3 mt-4 space-y-2 text-sm">
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Estado Pago:</span> <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${props.status_factura === 'completo' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'}`}>{props.status_factura}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Servicio:</span> <span className="text-gray-800 dark:text-gray-200">{props.service_type}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Monto:</span> <span className="font-medium text-gray-800 dark:text-gray-200">{formatCurrency(props.amount)}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Fecha:</span> <span className="text-gray-800 dark:text-gray-200">{props.dim_date}</span></div>
                </div>

                {/* Acciones */}
                <div className="col-span-3 mt-4 flex justify-center">
                    <div className="w-full max-w-[140px] scale-90">
                        <div className="inline-flex bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white rounded-lg shadow-md transition-colors duration-200 w-full justify-center cursor-pointer transform hover:scale-105 active:scale-95">
                            <div className="w-full flex justify-center items-center py-2 px-3">
                                <ActionMenu 
                                    id_user={props.dim_customer_id}
                                    serviceName={props.service_name}
                                    onUpdate={props.onEditSuccess}
                                    props={props}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* --- Vista de Tabla para Tablet y Escritorio --- */}
            {/* Imagen */}
            <div className="hidden md:flex md:items-center md:justify-center md:px-2 md:first:pl-5 md:last:pr-5 md:py-3">
                <img className="rounded-full w-10 h-10" src={userImage} alt={props.full_name} />
            </div>

            {/* Nombre Completo */}
            <div className="hidden md:block md:px-2 md:first:pl-5 md:last:pr-5 md:py-3 md:col-span-2">
                <div className="text-left font-medium text-gray-800 dark:text-gray-100 text-base">{props.full_name}</div>
            </div>

            {/* Rol */}
            <div className="hidden md:block md:px-2 md:first:pl-5 md:last:pr-5 md:py-3">
                <div className="text-center font-medium text-sky-600 dark:text-sky-400 text-base">{props.role_name}</div>
            </div>

            {/* Estado Factura */}
            <div className="hidden md:flex md:justify-center md:px-2 md:py-3">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${props.status_factura === 'completo' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'}`}>
                    {props.status_factura}
                </div>
            </div>

            {/* Tipo de Servicio */}
            <div className="hidden md:block md:px-2 md:first:pl-5 md:last:pr-5 md:py-3">
                <div className="text-center text-base">{props.service_type}</div>
            </div>

            {/* Monto */}
            <div className="hidden md:block md:px-2 md:first:pl-5 md:last:pr-5 md:py-3">
                <div className="text-center text-base">{formatCurrency(props.amount)}</div>
            </div>

            {/* Fecha y Acciones (combinados en la última columna) */}
            <div className="hidden md:grid md:grid-cols-2 md:items-center md:px-2 md:first:pl-5 md:last:pr-5 md:py-3">
                <div className="text-left text-base">{props.dim_date}</div>
                <div className="flex justify-center items-center">
                    <div className="inline-flex bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white rounded-lg shadow-md transition-colors duration-200 cursor-pointer min-w-[80px] max-w-[120px] justify-center">
                        <div className="w-full flex justify-center items-center py-2 px-3">
                            <ActionMenu
                                id_user={props.dim_customer_id}
                                serviceName={props.service_name}
                                onUpdate={props.onEditSuccess}
                                props={props}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DynamicTableItem;