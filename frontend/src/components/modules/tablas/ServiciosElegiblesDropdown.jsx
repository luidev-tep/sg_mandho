import React, { useState, useRef, useEffect } from 'react';
import Transition from '../../../utils/Transition';
import ServiciosElegiblesModal from './ServiciosElegiblesModal';

function ServiciosElegiblesDropdown({ serviciosValidos, serviceName, onSuccess }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedService, setSelectedService] = useState(null);

  // --- Hooks para manejar el cierre del dropdown ---
  const trigger = useRef(null);
  const dropdown = useRef(null);

  // Imprimir en consola cuando lleguen los datos
  useEffect(() => {
    if (serviciosValidos && serviceName) {
      console.log('📥 Datos recibidos en ServiciosElegiblesDropdown:');
      console.log('serviceName:', serviceName);
      console.log('serviciosValidos.servicios:', serviciosValidos.servicios);
      console.log('serviciosValidos.usuarios:', serviciosValidos.usuarios);
    }
  }, [serviciosValidos, serviceName]);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const clickHandler = ({ target }) => {
      if (!dropdown.current) return;
      if (!dropdownOpen || dropdown.current.contains(target) || trigger.current.contains(target)) return;
      setDropdownOpen(false);
    };
    document.addEventListener('click', clickHandler);
    return () => document.removeEventListener('click', clickHandler);
  });

  // Cerrar al presionar ESC
  useEffect(() => {
    const keyHandler = ({ keyCode }) => {
      if (!dropdownOpen || keyCode !== 27) return;
      setDropdownOpen(false);
    };
    document.addEventListener('keydown', keyHandler);
    return () => document.removeEventListener('keydown', keyHandler);
  });

  const handleSelectService = (service) => {
    setSelectedService(service);
    setIsModalOpen(true);
    setDropdownOpen(false);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedService(null);
    onSuccess(); // Llamar a onSuccess al cerrar el modal
  };

  if (!serviciosValidos || !serviciosValidos.servicios || serviciosValidos.servicios.length === 0) {
    return null;
  }

  return (
    <>
      <div className="relative inline-flex ml-4">
        <button
          ref={trigger}
          className="flex items-center justify-center gap-1 px-3 py-2 text-sm font-medium bg-indigo-100 dark:bg-indigo-900/40 border border-indigo-300 dark:border-indigo-600 rounded-lg shadow-sm hover:bg-indigo-200 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-200 transition-all duration-200"
          aria-haspopup="true"
          onClick={() => setDropdownOpen(!dropdownOpen)}
          aria-expanded={dropdownOpen}
        >
          <svg className="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>Registrar usuarios que asistieron a:</span>
          <svg className={`w-4 h-4 ml-1 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>

        <Transition
          show={dropdownOpen}
          tag="div"
          className="origin-top-right z-20 absolute top-full left-0 min-w-56 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl overflow-hidden mt-1"
          enter="transition ease-out duration-200"
          enterStart="opacity-0 -translate-y-2"
          enterEnd="opacity-100 translate-y-0"
          leave="transition ease-out duration-200"
          leaveStart="opacity-100"
          leaveEnd="opacity-0"
        >
          <div ref={dropdown} className="py-1">
            {serviciosValidos.servicios.map((service, index) => (
              <button
                key={index}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => handleSelectService(service)}
              >
                {service}
              </button>
            ))}
          </div>
        </Transition>
      </div>

      {isModalOpen && selectedService && (
        <ServiciosElegiblesModal
          serviceName={serviceName}
          ServiceDetailType={selectedService}
          users={serviciosValidos.usuarios}
          onClose={handleCloseModal}
          onSuccess={onSuccess}
        />
      )}
    </>
  );
}

export default ServiciosElegiblesDropdown;