// ActionMenu.jsx
import React, { useState, useRef } from 'react';
import { useAuth } from '../../../utils/AuthContext';
import AccountsTableModal from '../../accounts/AccounsTable';
import PaymentsTableModal from './PagosUsuario';
import FinishPayment from '../TerminarPago';
//import DesactivateModal from './DesactivateModal';

function ActionMenu({ onUpdate, id_user, serviceName, props }) {
  const { state } = useAuth();
  const userRole = state.usuario?.RoleName?.toLowerCase();
  const [isOpen, setIsOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [desactivateUserOpen, setDesactivateUserOpen] = useState(false);
  const [accountsModalOpen, setAccountsModalOpen] = useState(false);
  const menuRef = useRef(null);

  const handleEditClick = (e) => {
    e.stopPropagation();
    setEditModalOpen(true);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full" ref={menuRef}>
      {/* Botón del menú */}
      <button
        className="w-full flex items-center justify-center text-white"
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
      >
        <span className="sr-only">Mas opciones</span>
        <svg className="w-8 h-8 fill-current" viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="2" />
          <circle cx="10" cy="16" r="2" />
          <circle cx="22" cy="16" r="2" />
        </svg>
      </button>

      {/* Menú desplegable (sin cambios) */}
      {isOpen && (
        <div className="absolute right-0 z-10 mt-1 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
          <button
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation(); 
              setEditModalOpen(true);
              setIsOpen(false);
            }}
          >
            Ver detalles de pago
          </button>
          {userRole !== 'delegado' && (
            <button
              className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={(e) => {
                e.stopPropagation();
                setDesactivateUserOpen(true);
                setIsOpen(false);
              }}
            >
              Terminar Pago
            </button>
          )}
          <button
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setAccountsModalOpen(true);
              setIsOpen(false);
            }}
          >
            Ver Cuentas
          </button>
        </div>
      )}

      {/* Modal de Edición (sin cambios) */}
      {editModalOpen && (
        <PaymentsTableModal
          id_user={id_user}
          serviceName={serviceName}
          onClose={() => setEditModalOpen(false)}
          service_type={props.service_type}
          Year={props.dim_date}
          onUpdate={onUpdate}
          
        />
      )}

      {desactivateUserOpen && (
        <FinishPayment 
          onClose={() => setDesactivateUserOpen(false)}
          onUpdate={onUpdate} // Pasamos la prop onUpdate al modal
          props={props}
        />
      )}

      {/* Modal de Ver Cuentas (sin cambios) */}
      {accountsModalOpen && (
        <AccountsTableModal
          id_user={id_user}
          onClose={() => setAccountsModalOpen(false)}
        />
      )}
    </div>
  );
}

export default ActionMenu;