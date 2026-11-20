// ActionMenu.jsx
import React, { useState, useRef, useEffect } from 'react';
import AccountsTableModal from '../accounts/AccounsTable';
import EditCustomerModal from './CustomerEdit';
import DesactivateModal from './DesactivateModal';
import UserReportModal from './CustomerReport';

function ActionMenu({ onUpdate, id_user }) {
  const [isOpen, setIsOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [desactivateUserOpen, setDesactivateUserOpen] = useState(false);
  const [accountsModalOpen, setAccountsModalOpen] = useState(false);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);
  useEffect(() => {
    if (!isOpen) return;
    const outside = (event) => { if (!menuRef.current?.contains(event.target)) setIsOpen(false); };
    const key = (event) => { if (event.key === 'Escape') { setIsOpen(false); buttonRef.current?.focus(); } };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', key);
    return () => { document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', key); };
  }, [isOpen]);

  const handleEditClick = (e) => {
    e.stopPropagation();
    setEditModalOpen(true);
    setIsOpen(false); 
  };

  return (
    <div className="relative w-full" ref={menuRef}>
      {/* Botón del menú */}
      <button
        ref={buttonRef}
        type="button"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        className="w-full flex items-center justify-center text-white"
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
          if (!isOpen) requestAnimationFrame(() => menuRef.current?.querySelector('[role="menuitem"]')?.focus());
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
        <div role="menu" onKeyDown={(event) => {
          if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
          event.preventDefault();
          const items = Array.from(event.currentTarget.querySelectorAll('[role="menuitem"]'));
          const index = items.indexOf(document.activeElement);
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1 : (index + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
          items[next]?.focus();
        }} className="absolute right-0 z-10 mt-1 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
          <button role="menuitem" type="button"
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setEditModalOpen(true);
              setIsOpen(false);
            }}
          >
            Editar
          </button>
          <button role="menuitem" type="button"
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setDesactivateUserOpen(true);
              setIsOpen(false);
            }}
          >
            Marcar como Fallecido
          </button>
          <button role="menuitem" type="button"
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setAccountsModalOpen(true);
              setIsOpen(false);
            }}
          >
            Ver Cuentas
          </button>
          <button role="menuitem" type="button"
            className="block w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setReportModalOpen(true);
              setIsOpen(false);
            }}
          >
            Ver Reporte
          </button>
        </div>
      )}

      {/* Modal de Edición (sin cambios) */}
      {editModalOpen && (
        <EditCustomerModal
          id_user={id_user}
          onClose={() => setEditModalOpen(false)}
          onUpdate={onUpdate}
        />
      )}

      {desactivateUserOpen && (
        <DesactivateModal 
          id_user={id_user} 
          onClose={() => setDesactivateUserOpen(false)}
          onUpdate={onUpdate} // Pasamos la prop onSuccess al modal
        />
      )}

      {/* Modal de Ver Cuentas (sin cambios) */}
      {accountsModalOpen && (
        <AccountsTableModal
          id_user={id_user}
          onClose={() => setAccountsModalOpen(false)}
        />
      )}

      {/* Modal de Ver Reporte */}
      {reportModalOpen && (
        <UserReportModal
          id_user={id_user}
          onClose={() => setReportModalOpen(false)}
        />
      )}
    </div>
  );
}

export default ActionMenu;