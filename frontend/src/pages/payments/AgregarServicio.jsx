import React, { useState, useEffect } from 'react';
import Sidebar from '../../partials/SideBar.jsx';
import Header from '../../partials/Header.jsx';
import PasswordVerificationModal from '../../components/ModalValitePass.jsx';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { generarServicio } from '../../api/pagos/api_generar_servicio.js';
import PayBg from "../../images/pay-bg.jpg";

import Tooltip from '../../components/Tooltip.jsx';


function AgregarServicio() {
  const { moduleName } = useParams();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Estados para el formulario
  const [nombreServicio, setNombreServicio] = useState('');
  const [cantidad, setCantidad] = useState('');
  const [esOpcional, setEsOpcional] = useState(false); // false = No (obligatorio), true = Sí (opcional)
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [isError, setIsError] = useState(false); // Nuevo estado para controlar si es error

  // Estados para la verificación de contraseña
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [isPasswordVerified, setIsPasswordVerified] = useState(false);
  const [pendingFormData, setPendingFormData] = useState(null);

  const currentYear = new Date().getFullYear();
  // Fechas predefinidas no modificables
  const fechaInicioPredefinida = `${currentYear}-01-01`;
  const fechaFinPredefinida = `${currentYear}-12-31`;

  // Efecto para ajustar 'esOpcional' basado en 'moduleName'
  useEffect(() => {
    setEsOpcional(moduleName === 'delegacion');
  }, [moduleName]);

  // Función para regresar a la página anterior
  const handleGoBack = () => {
    navigate(-1);
  };

  // Función para validar nombre del servicio (ahora permite letras, números, espacios y caracteres especiales básicos)
  const handleNombreServicioChange = (e) => {
    const value = e.target.value;
    // Permite letras, números, espacios, acentos y algunos caracteres especiales comunes
    // Se valida que los números no sean negativos
    if (/^[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s.,-]*$/.test(value) || value === '') {
      setNombreServicio(value);
    }
  };

  // Función para validar cantidad (solo números, máximo 5000)
  const handleCantidadChange = (e) => {
    const value = e.target.value;
    // Permite solo números y punto decimal
    if (/^\d*\.?\d*$/.test(value)) {
      const numericValue = parseFloat(value);
      // Valida que no exceda 5000. El mínimo se valida con el atributo 'min' del input para una mejor experiencia de usuario.
      if (numericValue <= 5000 || value === '') {
        setCantidad(value);
      }
    }
  };

  // Función que se ejecuta cuando la contraseña es verificada exitosamente
  const handlePasswordVerificationSuccess = (verificationData) => {

    setIsPasswordVerified(true);
    
    // Si hay datos del formulario pendientes, proceder con el envío
    if (pendingFormData) {
      proceedWithServiceCreation(pendingFormData);
      setPendingFormData(null);
    }
  };

  // Función para crear el servicio (lógica original del handleSubmit)
  const proceedWithServiceCreation = async (formData) => {
    setLoading(true);
    setMensaje('');
    setIsError(false); // Resetear estado de error

    try {

      const response = await generarServicio(formData);
      
      if (response) {
        setMensaje('Servicio creado exitosamente');
        setIsError(false); // No es error
        // Limpiar formulario
        setNombreServicio('');
        setCantidad('');
        // Reset de verificación para próximas acciones
        setIsPasswordVerified(false);
      }

    } catch (error) {
      console.error('Error al crear servicio:', error);
      setMensaje(error.message || 'Error al crear el servicio. Intente nuevamente.');
      setIsError(true); // Es error
      // Reset de verificación en caso de error
      setIsPasswordVerified(false);
    } finally {
      setLoading(false);
    }
  };

  // Función principal para manejar el envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje('');
    setIsError(false); // Resetear estado de error

    // Validaciones del formulario
    if (!nombreServicio.trim()) {
      setMensaje('El nombre del servicio es requerido');
      setIsError(true);
      return;
    }

    if (!cantidad || parseFloat(cantidad) <= 0) {
      setMensaje('La cantidad debe ser mayor a 0');
      setIsError(true);
      return;
    }

    if (parseFloat(cantidad) > 5000) {
      setMensaje('La cantidad no puede exceder 5000');
      setIsError(true);
      return;
    }

    // Preparar el payload
    const payload = {
      ServiceName: moduleName,
      serviceDetailesType: nombreServicio.trim(),
      amount: parseFloat(cantidad),
      year: currentYear,
      isOptional: esOpcional // Nuevo campo booleano
    };

    // Verificar si la contraseña ya fue validada
    if (!isPasswordVerified) {
      // Guardar los datos del formulario y mostrar modal de verificación
      setPendingFormData(payload);
      setShowPasswordModal(true);
    } else {
      // Si ya está verificada, proceder directamente
      proceedWithServiceCreation(payload);
    }
  };

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Content area */}
      <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        {/* Site header */}
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        <main className="grow">
          <div className="relative pt-10">
            <div className="absolute inset-0 bg-gray-800 overflow-hidden" aria-hidden="true">
              <img className="object-cover h-full w-full filter blur-sm opacity-10" src={PayBg} width="575" height="225" alt="Pay background" />
            </div>
            <div className="relative px-5 sm:px-7 lg:px-10 max-w-2xl mx-auto">
              <img className="rounded-t-xl shadow-lg" src={PayBg} width="575" height="225" alt="Pay background" />
            </div>
          </div>

          <div className="relative px-5 sm:px-7 lg:px-10 pb-10 max-w-2xl mx-auto">
            <div className="bg-white dark:bg-gray-800 px-10 pb-8 rounded-b-xl shadow-xs">
              {/* Card header */}
              <div className="text-center mb-8">
                {/* Se tiene que agregar un disenio de colores a este boton.  */}
                {/* Botón para regresar */}
                <div className="flex justify-start mb-4 " >
                  <button
                      onClick={handleGoBack}
                      className="flex items-center px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-blue-600 dark:text-blue-300 font-medium rounded-lg shadow transition-all duration-200 hover:bg-gray-300 dark:hover:bg-gray-600 active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                      {/* El SVG ahora usa 'currentColor' para heredar el color del texto (text-blue-600) */}
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                      </svg>
                      <span className="text-sm">Regresar</span>
                  </button>
                </div>
                
                <h1 className="text-2xl leading-snug text-gray-800 dark:text-gray-100 font-semibold mb-3">
                  Agregar Nuevo Servicio
                </h1>
                <div className="text-base text-gray-600 dark:text-gray-400">
                  {moduleName && `Comitiva de ${moduleName}`}
                </div>
                {/* Indicador de seguridad */}
                <div className="mt-2 flex items-center justify-center text-sm">
                  <svg className="w-4 h-4 text-yellow-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-yellow-600 dark:text-yellow-400">Acción protegida - Verificación requerida</span>
                </div>
              </div>

              {/* Mostrar mensaje de éxito o error */}
              {mensaje && (
                <div className={`mb-6 p-4 rounded-lg text-base font-medium ${
                  isError 
                    ? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-900/50' 
                    : 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-900/50'
                }`}>
                  {mensaje}
                </div>
              )}

              {/* Indicador de estado de verificación */}
              {isPasswordVerified && (
                <div className="mb-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-900/50">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Credenciales verificadas - Puede proceder con la creación
                  </div>
                </div>
              )}

              {/* Formulario */}
              <form onSubmit={handleSubmit}>
                <div className="space-y-6">
                  {/* Nombre del Servicio */}
                  <div>
                    <div className="flex items-center">
                      <label className="block text-base font-medium mb-2" htmlFor="nombre-servicio">
                        Nombre del Servicio <span className="text-red-500">*</span>
                      </label>
                      {/* Tooltip para Nombre del Servicio */}
                      <Tooltip className="ml-2 mb-1">
                        <div className="text-sm">Define el nombre específico para este nuevo tipo de servicio (ej: faena, cooperación, etc.).</div>
                      </Tooltip>
                    </div>
                    <input 
                      id="nombre-servicio" 
                      className="form-input w-full text-base py-3 px-4" 
                      type="text" 
                      placeholder="Ej: faena, comida etc. . ."
                      value={nombreServicio}
                      onChange={handleNombreServicioChange}
                      required
                    />
                    <div className="text-sm text-gray-500 mt-1">
                      Escribe el nombre del servicio (puede incluir letras y números)
                    </div>
                  </div>

                  {/* Cantidad a Cobrar */}
                  <div>
                    <div className="flex items-center">
                      <label className="block text-base font-medium mb-2" htmlFor="cantidad">
                        Cantidad a Cobrar <span className="text-red-500">*</span>
                      </label>
                      {/* Tooltip para Cantidad a Cobrar */}
                      <Tooltip className="ml-2 mb-1">
                        <div className="text-sm">Establece el monto que se cobrará por este servicio. El valor debe ser numérico.</div>
                      </Tooltip>
                    </div>
                    <input 
                      id="cantidad" 
                      className="form-input w-full text-base py-3 px-4" 
                      type="number" 
                      step="1.00"
                      min="10"
                      max="5000"
                      placeholder="0.00"
                      value={cantidad}
                      onChange={handleCantidadChange}
                      onKeyDown={(e) => {
                        // Prevenir el comportamiento por defecto de las flechas
                        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                          e.preventDefault();
                        }
                      }}
                      required
                    />
                    <div className="text-sm text-gray-500 mt-1">
                      Mínimo permitido: $10 , Máximo permitido: $5000. 
                    </div>
                  </div>

                  {/* Participación Opcional */}
                  <div>
                    <div className="flex items-center">
                      <label className="block text-base font-medium mb-2">
                        ¿La participación en este servicio es opcional?
                      </label>
                      {/* Tooltip para Participación Opcional */}
                      <Tooltip className="ml-2 mb-1">
                        <div className="text-sm text-left max-w-xs">
                          Seleccione 'Sí' si los usuarios pueden excusarse de participar (ej: faenas, actividades voluntarias).<br/><br/>
                          Seleccione 'No' si la participación es obligatoria para todos (ej: cooperaciones, cuotas fijas).
                        </div>
                      </Tooltip>
                    </div>
                    <div className="flex items-center space-x-6">
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="radio"
                          name="opcional"
                          className="form-radio h-4 w-4 text-indigo-600"
                          checked={esOpcional === true}
                          disabled={moduleName === 'delegacion' || moduleName === 'agua'}
                          onChange={() => setEsOpcional(true)}
                        />
                        <span className="ml-2 text-base text-gray-700 dark:text-gray-300">Sí</span>
                      </label>
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="radio"
                          name="opcional"
                          className="form-radio h-4 w-4 text-indigo-600"
                          checked={esOpcional === false}
                          disabled={moduleName === 'delegacion' || moduleName === 'agua'}
                          onChange={() => setEsOpcional(false)}
                        />
                        <span className="ml-2 text-base text-gray-700 dark:text-gray-300">No</span>
                      </label>
                    </div>
                  </div>

                  {/* Fechas predefinidas (solo lectura) */}
                  <div className="flex space-x-6">
                    <div className="flex-1">
                      <label className="block text-base font-medium mb-2" htmlFor="fecha-inicio">
                        Fecha de Inicio
                      </label>
                      <input 
                        id="fecha-inicio" 
                        className="form-input w-full text-base py-3 px-4 bg-gray-50 dark:bg-gray-700/50 cursor-not-allowed" 
                        type="date"
                        value={fechaInicioPredefinida}
                        readOnly
                        disabled
                      />
                    </div>
                    <div className="flex-1">
                      <label className="block text-base font-medium mb-2" htmlFor="fecha-fin">
                        Fecha de Fin
                      </label>
                      <input 
                        id="fecha-fin" 
                        className="form-input w-full text-base py-3 px-4 bg-gray-50 dark:bg-gray-700/50 cursor-not-allowed" 
                        type="date"
                        value={fechaFinPredefinida}
                        readOnly
                        disabled
                      />
                    </div>
                  </div>

                  {/* Información automática */}
                  <div className="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg">
                    <h4 className="text-base font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Información del Servicio:
                    </h4>
                    <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                      <li>• <strong>Disponibilidad:</strong> 01/01/{currentYear} - 31/12/{currentYear}</li>
                      <li>• <strong>Año:</strong> {currentYear}</li>
                      <li>• <strong>Estado:</strong> Activo durante todo el año</li>
                    </ul>
                  </div>
                </div>

                <div className="mt-8">
                  <div className="mb-6">
                    <button
                      type="submit"
                      disabled={loading}
                      className={`
                        w-full px-4 py-3 md:px-6 md:py-4
                        bg-gradient-to-r from-gray-800 to-gray-900
                        dark:from-gray-100 dark:to-gray-200
                        text-white dark:text-gray-900
                        font-medium rounded-lg
                        shadow-lg
                        transition-all duration-300
                        transform hover:scale-[1.02]
                        hover:shadow-xl
                        active:scale-95
                        focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50
                        relative overflow-hidden
                        group
                        text-center
                        ${loading ? 'opacity-50 cursor-not-allowed' : ''}
                      `}
                    >
                      <span className="relative z-10 flex items-center justify-center">
                        {loading ? 'Creando Servicio...' : (isPasswordVerified ? 'Crear Servicio' : 'Verificar y Crear')}
                        <span className="ml-2">
                          {loading ? (
                            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          ) : (
                            isPasswordVerified ? '→' : '🔒'
                          )}
                        </span>
                      </span>
                      <span className="
                        absolute inset-0
                        bg-gradient-to-r from-violet-600 to-blue-500
                        dark:from-violet-400 dark:to-blue-300
                        opacity-0
                        group-hover:opacity-100
                        transition-opacity duration-300
                      "></span>
                    </button>
                  </div>
                  <div className="text-sm text-gray-500 italic text-center">
                    El servicio estará disponible durante todo el año {currentYear}
                  </div>
                </div>
              </form>
            </div>
          </div>
        </main>
      </div>


      {/* Modal de verificación de contraseña */}
      {showPasswordModal && (
        <PasswordVerificationModal
          onClose={() => {
            setShowPasswordModal(false);
            setPendingFormData(null);
          }}
          onVerificationSuccess={handlePasswordVerificationSuccess}
          title="Crear Nuevo Servicio"
          message="Esta acción requiere autorización de delegado. Ingrese la contraseña de delegado para continuar creando el nuevo servicio."
          verificationType="default" // Usar la validación de delegado
        />
      )}
    </div>
  );
}

export default AgregarServicio;