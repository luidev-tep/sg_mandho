// partials/customers/CustomersTableItem.jsx
import React from 'react';
import Image01 from '../../../../images/user-40-01.jpg';
import Image02 from '../../../../images/user-40-02.jpg';
import Image03 from '../../../../images/user-40-03.jpg';
import ActionMenu from './ActionMenu';

function CustomersTableItem(props) {
    const imageMap = {
        'Image01': Image01,
        'Image02': Image02,
        'Image03': Image03,
    };

    // Determinar qué imagen usar basado en date_of_end
    const getImage = () => {
        if (props.date_of_end && props.date_of_end.toLowerCase() !== 's/n') {
            return Image03; // Usuario inactivo
        }
        return imageMap[props.image] || Image01; // Usuario activo o imagen por defecto
    };

    const userImage = getImage();

    return (
<div className="bg-white dark:bg-gray-800 shadow-md rounded-lg mb-4 p-4 md:p-0 md:shadow-none md:rounded-none md:mb-0 md:grid md:grid-cols-8 md:gap-4 md:items-center transition-all duration-200">
            {/* --- Vista de Tarjeta para Móvil (<md) --- */}
            <div className="md:hidden grid grid-cols-3 gap-4">
                {/* Col 1: Imagen */}
                <div className="col-span-1 flex items-center">
                    <img className="rounded-full w-16 h-16" src={userImage} alt={props.name} />
                </div>

                {/* Col 2: Nombre y Apellido */}
                <div className="col-span-2 flex flex-col justify-center">
                    <div className="font-bold text-lg text-gray-800 dark:text-gray-100">{props.name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{props.last_name}</div>
                </div>

                {/* Detalles Adicionales */}
                <div className="col-span-3 mt-4 space-y-2 text-sm">
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Manzana:</span> <span className="font-medium text-sky-600 dark:text-sky-400">{props.manzana}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Dirección:</span> <span className="text-right text-gray-800 dark:text-gray-200">{props.address}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Nacimiento:</span> <span className="text-gray-800 dark:text-gray-200">{props.birth_date}</span></div>
                    <div className="flex justify-between"><span className="font-semibold text-gray-600 dark:text-gray-400">Defunción:</span> <span className="text-gray-800 dark:text-gray-200">{props.date_of_end}</span></div>
                </div>
                {/* Acciones */}
                <div className="col-span-3 mt-4 flex justify-center">
                    <div className="inline-flex items-center justify-center px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white font-medium rounded-lg shadow transition-all duration-200 hover:shadow-md active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900">
                        <ActionMenu 
                            id_user={props.id}
                            onUpdate={props.onEditSuccess}
                        />
                    </div>
                </div>
            </div>

            {/* --- Vista de Tabla para Tablet y Escritorio (>=md) --- */}
            {/* Imagen */}
            <div className="hidden md:flex md:items-center md:justify-center md:px-2 md:py-3">
                <img className="rounded-full w-10 h-10" src={userImage} alt={props.name} />
            </div>

            {/* Nombre y Apellido */}
            <div className="hidden md:block md:px-2 md:py-3 md:col-span-2">
                <div className="text-left">
                    <span className="font-medium text-gray-800 dark:text-gray-100">{props.name}</span>
                    <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">{props.last_name}</span>
                </div>
            </div>

            {/* Manzana */}
            <div className="hidden md:block md:px-2 md:py-3">
                <div className="text-center font-medium text-sky-600">{props.manzana}</div>
            </div>

            {/* Dirección (visible solo en lg) */}
            <div className="hidden md:block md:px-2 md:py-3">
                <div className="text-left font-medium text-green-600">{props.address}</div>
            </div>

            {/* Fecha Nacimiento */}
            <div className="hidden md:block md:px-2 md:py-3">
                <div className="text-center text-sm">{props.birth_date}</div>
            </div>

            {/* Fecha Defunción */}
            <div className="hidden md:block md:px-2 md:py-3">
                <div className="text-center text-sm">{props.date_of_end}</div>
            </div> 

                {/* Acciones */}
                <div className="hidden md:flex md:justify-center md:items-center md:px-3 md:py-3">
                    <div className="inline-flex bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 text-white rounded-lg shadow-md transition-colors duration-200 w-1/2 justify-center cursor-pointer">
                        <div className="w-full flex justify-center items-center py-2">
                            <ActionMenu id_user={props.id} />
                        </div>
                    </div>
                </div>
        </div>
    );
}

export default CustomersTableItem;