// partials/customers/CustomersTableItem.jsx
import React from 'react';
import Image01 from '../../../images/user-40-01.jpg';
import Image02 from '../../../images/user-40-02.jpg';
import Image03 from '../../../images/user-40-03.jpg';
import Imagen04 from '../../../images/user-40-04.jpg';
import ActionMenu from './ActionMenu';

function DynamicTableItem(props) {
    const imageMap = {
        'Image01': Image01,
        'Image02': Image02,
        'Image03': Imagen04,
        // Añade más imágenes según necesites
    };

    // Determinar qué imagen usar basado props.status_account
    const getImage = () => {
        if (props.status_account && props.status_account.toLowerCase() === 'inactivo') {
            return Image03; // Usuario inactivo
        }
        return imageMap[props.image] || Image01; // Usuario activo o imagen por defecto
    };

    const userImage = getImage();

    return (
        <tr className={props.status_account && props.status_account.toLowerCase() === 'inactivo' 
            ? 'bg-amber-100 dark:bg-amber-900/20 border-l-4 border-amber-500 dark:border-amber-400' 
            : ''}>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="flex items-center justify-center">
                    <div className="w-10 h-10 md:w-12 md:h-12 shrink-0">
                        <img className="rounded-full" src={userImage} width="48" height="48" alt={props.name} />
                    </div>
                </div>
            </td>

            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-left font-medium text-gray-800 dark:text-gray-100 text-base">
                    {props.full_name}
                </div>
            </td>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center font-medium text-sky-600 dark:text-sky-400 text-base">
                    {props.role_name}
                </div>
            </td>
            
            <td className="px-2 md:px-4 py-2 whitespace-nowrap">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium 
                    ${props.status_factura === 'pagado' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' : ''}
                    ${props.status_factura === 'pendiente' ? 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300' : ''}`}>
                    {props.status_factura}
                </div>
            </td>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center text-base">{props.service_type}</div>
            </td>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center text-base">{props.amount.toFixed(2)}</div>
            </td>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="text-center text-base">{props.dim_date}</div>
            </td>
            
            <td className="px-2 first:pl-5 last:pr-5 py-3 whitespace-nowrap">
                <div className="flex justify-center items-center min-h-[44px] min-w-[44px] rounded-md hover:shadow-md transition-shadow duration-200">
                    <ActionMenu 
                        id_user={props.dim_customer_id}
                        serviceName={props.service_name}
                        onUpdate={props.onEditSuccess}
                        props={props}
                    />
                </div>
            </td>
        </tr>
    );
}

export default DynamicTableItem;