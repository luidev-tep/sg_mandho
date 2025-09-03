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
        // Añade más imágenes según necesites
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
        <tr>
            {/* Imagen del usuario */}
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="flex items-center justify-center">
                    <div className="w-8 h-8 md:w-10 md:h-10 shrink-0">
                        <img className="rounded-full" src={userImage} width="40" height="40" alt={props.name} />
                    </div>
                </div>
            </td>

            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-left font-medium text-gray-800 dark:text-gray-100">
                    {props.name}
                    <div className="md:hidden text-sm text-gray-600">{props.last_name}</div>
                </div>
            </td>
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap hidden md:table-cell">
                <div className="text-left">{props.last_name}</div>
            </td>
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center font-medium text-sky-600">{props.manzana}</div>
            </td>
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap hidden lg:table-cell">
                <div className="text-left font-medium text-green-600">{props.address}</div>
            </td>
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center text-sm md:text-base">{props.birth_date}</div>
            </td>
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center text-sm md:text-base">{props.date_of_end}</div>
            </td>

            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                {/* Menu button with larger click area */}
                <div className="flex justify-center items-center min-h-[44px] min-w-[44px] rounded-md hover:shadow-md transition-shadow duration-200">
                    <ActionMenu 
                        id_user={props.id}
                    />
                </div>
            </td>
        </tr>
    );
}

export default CustomersTableItem;