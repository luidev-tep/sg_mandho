import React, { useState, useEffect } from 'react';
import BarraBusquedaAutomatica from '../components/customers/BarraBusqueda';
import { getOwners } from '../api/api_administrador';
import { createOwner } from '../api/api_administrador';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Link, useNavigate } from 'react-router-dom';
import Sidebar from '../partials/SideBar';
import Header from '../partials/Header';

const schema = yup.object().shape({
    clienteId: yup.string().required('Debe seleccionar un cliente.'),
    username: yup.string()
        .required('El nombre de usuario es requerido.')
        .matches(/^\S*$/, 'El nombre de usuario no debe contener espacios.'),
    password: yup.string()
        .required('La contraseña es requerida.')
        .min(8, 'La contraseña debe tener al menos 8 caracteres.')
        .matches(/^\S*$/, 'La contraseña no debe contener espacios.')
        .matches(/[a-z]/, 'Debe tener al menos una letra minúscula.')
        .matches(/[A-Z]/, 'Debe tener al menos una letra mayúscula.')
        .matches(/[0-9]/, 'Debe tener al menos un dígito numérico.')
        .matches(/[^A-Za-z0-9]/, 'Debe tener al menos un carácter especial.'),
    confirmPassword: yup.string()
        .required('Debe confirmar la contraseña.')
        .oneOf([yup.ref('password'), null], 'Las contraseñas deben coincidir.'),
    RoleName: yup.string().required('El rol es requerido.'),
    serviceName: yup.string().required('El servicio es requerido.'),
});

function AgregarUsuario() {
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [owners, setOwners] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');
    const [submitSuccess, setSubmitSuccess] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [selectedCustomer, setSelectedCustomer] = useState(null);

    // CORRECCIÓN: Se agrega 'watch' para observar cambios en los campos del formulario.
    const { register, handleSubmit, setValue, reset, watch, formState: { errors } } = useForm({
        resolver: yupResolver(schema),
        mode: 'onBlur',
        reValidateMode: 'onChange',
        defaultValues: {
            RoleName: 'comitiva',
            serviceName: 'agua'
        }
    });

    // Observamos el valor actual del campo 'RoleName'
    const selectedRole = watch('RoleName');

    // CORRECCIÓN: Lógica para auto-seleccionar el servicio basado en el rol.
    useEffect(() => {
        if (selectedRole === 'delegado') {
            setValue('serviceName', 'delegado', { shouldValidate: true });
        } else if (selectedRole === 'subdelegado') {
            setValue('serviceName', 'personas', { shouldValidate: true });
        } else if (selectedRole === 'comitiva') {
            // Si el servicio actual no es válido para comitiva, se resetea a 'agua'
            const validComitivaServices = ['agua', 'panteon', 'delegacion', 'feria'];
            const currentService = watch('serviceName');
            if (!validComitivaServices.includes(currentService)) {
                setValue('serviceName', 'agua', { shouldValidate: true });
            }
        }
    }, [selectedRole, setValue, watch]);


    const fetchOwners = async () => {
        try {
            setLoading(true);
            const data = {
                get_onwers_info: true
            }
            const response = await getOwners(data);

            const roleOrder = {
                'delegado': 1,
                'subdelegado': 2,
                'comitiva': 3
            };

            const sortedData = response.data.sort((a, b) => {
                const roleA = a.RoleName ? a.RoleName.toLowerCase() : '';
                const roleB = b.RoleName ? b.RoleName.toLowerCase() : '';
                const orderA = roleOrder[roleA] || 99;
                const orderB = roleOrder[roleB] || 99;
                return orderA - orderB;
            });

            setOwners(sortedData);
            setSubmitError('');
        } catch (err) {
            setSubmitError(err.message || 'Error al obtener los propietarios');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOwners();
    }, []);

    const handleCustomerSelect = (customer) => {
        setSelectedCustomer(customer);
        setValue('clienteId', customer.id, { shouldValidate: true });
    };

    const onSubmit = async (data) => {
        setSubmitError('');
        setSubmitSuccess('');
        setIsSubmitting(true);

        if (!selectedCustomer) {
            setSubmitError('Por favor, seleccione un cliente.');
            setIsSubmitting(false);
            return;
        }

        const payload = {
            'DIM_CustomerId': data.clienteId,
            'CustomerFraction': selectedCustomer.manzana,
            ...data
        };

        try {
            const response = await createOwner({ create_onwer: payload });
            if (response.status === 'success') {
                setSubmitSuccess(response.message || 'Usuario creado exitosamente.');
                setSelectedCustomer(null);
                reset({
                    clienteId: '',
                    username: '',
                    password: '',
                    confirmPassword: '',
                    RoleName: 'comitiva',
                    serviceName: 'agua'
                });
                fetchOwners();
            } else {
                setSubmitError(response.message || 'Ocurrió un error al crear el usuario.');
            }
        } catch (err) {
            setSubmitError(err.message || 'Error al enviar la petición.');
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex h-[100dvh] overflow-hidden">
            <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} variant="v2" />
            <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden bg-white dark:bg-gray-900">
                <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} variant="v3" />
                <main className="grow">
                    <div className="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto">
                        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
                            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Usuarios con Acceso al Sistema</h2>
                            {loading ? <p className="text-center dark:text-gray-300">Cargando usuarios...</p> : (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                        <thead className="bg-gray-50 dark:bg-gray-700">
                                            <tr>
                                                {['Nombre Completo', 'Rol', 'Servicio', 'Fracción', 'Estatus', 'Inicio', 'Fin'].map(header => (
                                                    <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{header}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                            {owners.length > 0 ? owners.map((owner, index) => (
                                                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">{owner.fullname}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{owner.RoleName}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{owner.ServiceName}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{owner.CustomerFraction}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${owner.StatusName && owner.StatusName.toLowerCase() === 'activo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                            {owner.StatusName}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{owner.StartDate}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{owner.EndDate}</td>
                                                </tr>
                                            )) : (
                                                <tr>
                                                    <td colSpan="7" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">No hay usuarios para mostrar.</td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="px-4 sm:px-6 lg:px-8 py-8 w-full max-w-9xl mx-auto">
                        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 md:p-8">
                            <div className="mb-8 text-center">
                                <h1 className="text-2xl md:text-3xl text-gray-800 dark:text-gray-100 font-bold">Crear Usuario de Sistema</h1>
                                <p className="text-gray-600 dark:text-gray-400 mt-1">Asigna roles y permisos a un miembro de la comunidad.</p>
                            </div>

                            {submitSuccess && (
                                <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg flex items-center animate-fade-in">
                                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                                    <span>{submitSuccess}</span>
                                </div>
                            )}
                            {submitError && (
                                <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center animate-fade-in">
                                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
                                    <span>{submitError}</span>
                                </div>
                            )}

                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-3xl mx-auto">
                                <div>
                                    <label className="block text-sm font-black mb-1" htmlFor="clienteId">Buscar y Seleccionar Cliente <span className="text-red-500">*</span></label>
                                    <BarraBusquedaAutomatica onCustomerSelect={handleCustomerSelect} selectedClient={selectedCustomer} setSelectedClient={setSelectedCustomer} name="clienteId" register={register} errors={errors} setValue={setValue} disabled={isSubmitting} />
                                    {errors.clienteId && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.clienteId.message}</p>}
                                    {selectedCustomer && (
                                        <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                                            <p className="text-sm text-gray-800 dark:text-gray-200">Cliente: <span className="font-semibold">{selectedCustomer.nombre_completo}</span></p>
                                            <p className="text-sm text-gray-800 dark:text-gray-200">Fracción: <span className="font-semibold">{selectedCustomer.manzana}</span></p>
                                        </div>
                                    )}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-black mb-1" htmlFor="username">Usuario <span className="text-red-500">*</span></label>
                                        <input type="text" {...register("username")} id="username" placeholder="ej: juan.perez" className={`form-input w-full rounded-lg ${errors.username ? 'border-red-500' : 'border-gray-300'} ${isSubmitting ? 'bg-gray-100' : ''}`} disabled={isSubmitting} />
                                        {errors.username && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.username.message}</p>}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="relative">
                                        <label className="block text-sm font-black mb-1" htmlFor="password">Contraseña <span className="text-red-500">*</span></label>
                                        <input type={showPassword ? 'text' : 'password'} {...register("password")} id="password" placeholder="Mínimo 8 caracteres" className={`form-input w-full rounded-lg pr-10 ${errors.password ? 'border-red-500' : 'border-gray-300'} ${isSubmitting ? 'bg-gray-100' : ''}`} disabled={isSubmitting} />
                                        <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center text-sm leading-5">
                                            {showPassword ? <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg> : <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7 1.274-4.057 5.064-7 9.542-7 .847 0 1.67 .127 2.458 .362M17.999 11.18C18.623 11.51 19.2 12 20 12c1.274 4.057-5.064 7-9.542 7-1.136 0-2.23-.16-3.273-.452M9 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
                                        </button>
                                        {errors.password && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.password.message}</p>}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-black mb-1" htmlFor="confirmPassword">Confirmar Contraseña <span className="text-red-500">*</span></label>
                                        <input type={showPassword ? 'text' : 'password'} {...register("confirmPassword")} id="confirmPassword" placeholder="Repite la contraseña" className={`form-input w-full rounded-lg ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'} ${isSubmitting ? 'bg-gray-100' : ''}`} disabled={isSubmitting} />
                                        {errors.confirmPassword && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.confirmPassword.message}</p>}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-black mb-1" htmlFor="RoleName">Rol <span className="text-red-500">*</span></label>
                                        <select {...register("RoleName")} id="RoleName" className={`form-select w-full rounded-lg ${errors.RoleName ? 'border-red-500' : 'border-gray-300'} ${isSubmitting ? 'bg-gray-100' : ''}`} disabled={isSubmitting}>
                                            <option value="comitiva">Comitiva</option>
                                            <option value="subdelegado">Subdelegado</option>
                                            <option value="delegado">Delegado</option>
                                            {/* Se elimina la opción de Administrador */}
                                        </select>
                                        {errors.RoleName && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.RoleName.message}</p>}
                                    </div>
                                    <div>
                                        <label className="block text-sm font-black mb-1" htmlFor="serviceName">Servicio Asignado <span className="text-red-500">*</span></label>
                                        {/* CORRECCIÓN: El select se deshabilita y sus opciones cambian según el rol */}
                                        <select
                                            {...register("serviceName")}
                                            id="serviceName"
                                            className={`form-select w-full rounded-lg ${errors.serviceName ? 'border-red-500' : 'border-gray-300'} ${isSubmitting || selectedRole === 'delegado' || selectedRole === 'subdelegado' ? 'bg-gray-100' : ''}`}
                                            disabled={isSubmitting || selectedRole === 'delegado' || selectedRole === 'subdelegado'}
                                        >
                                            {selectedRole === 'comitiva' && (
                                                <>
                                                    <option value="agua">Agua</option>
                                                    <option value="panteon">Panteón</option>
                                                    <option value="delegacion">Delegación</option>
                                                    <option value="feria">Feria</option>
                                                </>
                                            )}
                                            {selectedRole === 'subdelegado' && (
                                                <option value="personas">Personas</option>
                                            )}
                                            {selectedRole === 'delegado' && (
                                                <option value="delegado">Delegado</option>
                                            )}
                                        </select>
                                        {errors.serviceName && <p className="text-red-500 text-sm mt-1 animate-fade-in">{errors.serviceName.message}</p>}
                                    </div>
                                </div>

                                <div className="flex items-center justify-between gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
                                    <Link to="/Analytics/delegado" className={`flex-1 px-6 py-3 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 text-gray-900 dark:text-white font-medium rounded-lg shadow-lg transition-all duration-300 transform hover:scale-[1.02] hover:shadow-xl active:scale-95 focus:outline-none relative overflow-hidden group text-center ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`} onClick={(e) => isSubmitting && e.preventDefault()}>
                                        <span className="relative z-10 flex items-center justify-center">
                                            <span className="mr-1">&lt;-</span> Regresar
                                        </span>
                                    </Link>

                                    <button type="submit" disabled={isSubmitting} className={`flex-1 px-6 py-3 bg-gradient-to-r from-gray-800 to-gray-900 dark:from-gray-100 dark:to-gray-200 text-white dark:text-gray-900 font-medium rounded-lg shadow-lg transition-all duration-300 relative overflow-hidden group ${isSubmitting ? 'cursor-not-allowed' : 'hover:scale-[1.02] hover:shadow-xl'} active:scale-95 focus:outline-none`}>
                                        {isSubmitting ? (
                                            <span className="flex items-center justify-center">
                                                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                                Creando...
                                            </span>
                                        ) : (
                                            <span className="relative z-10 flex items-center justify-center">
                                                Crear Usuario <span className="ml-1">-&gt;</span>
                                            </span>
                                        )}
                                        {!isSubmitting && (
                                            <span className="absolute inset-0 bg-gradient-to-r from-violet-600 to-blue-500 dark:from-violet-400 dark:to-blue-300 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default AgregarUsuario;