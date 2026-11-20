import { useState } from "react";

function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirmar acción",
  message = "¿Está seguro de que desea continuar?",
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  variant = "warning", // warning, danger, info, success
  reverseButtons = false, // Para invertir el orden de los botones
  icon = "default", // default, warning, danger, info, success, question
  showCloseButton = true,
  isProcessing = false,
  details = null // Para mostrar detalles adicionales debajo del mensaje
}) {
  if (!isOpen) return null;

  // Configuración de variantes
  const variants = {
    warning: {
      buttonBg: "bg-yellow-600 hover:bg-yellow-700 dark:hover:bg-yellow-800",
      iconColor: "text-yellow-500",
      bgAccent: "bg-yellow-50 dark:bg-yellow-900/20",
      borderAccent: "border-yellow-100 dark:border-yellow-900/30"
    },
    danger: {
      buttonBg: "bg-rose-600 hover:bg-rose-700 dark:hover:bg-rose-800",
      iconColor: "text-rose-500",
      bgAccent: "bg-rose-50 dark:bg-rose-900/20",
      borderAccent: "border-rose-100 dark:border-rose-900/30"
    },
    info: {
      buttonBg: "bg-blue-600 hover:bg-blue-700 dark:hover:bg-blue-800",
      iconColor: "text-blue-500",
      bgAccent: "bg-blue-50 dark:bg-blue-900/20",
      borderAccent: "border-blue-100 dark:border-blue-900/30"
    },
    success: {
      buttonBg: "bg-green-600 hover:bg-green-700 dark:hover:bg-green-800",
      iconColor: "text-green-500",
      bgAccent: "bg-green-50 dark:bg-green-900/20",
      borderAccent: "border-green-100 dark:border-green-900/30"
    }
  };

  const currentVariant = variants[variant] || variants.warning;

  // Iconos disponibles
  const icons = {
    default: (
      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
    ),
    warning: (
      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
    ),
    danger: (
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
    ),
    info: (
      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
    ),
    success: (
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    ),
    question: (
      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
    )
  };

  const selectedIcon = icons[icon] || icons.default;

  // Botones
  const cancelButton = (
    <button
      onClick={onClose}
      disabled={isProcessing}
      className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {cancelText}
    </button>
  );

  const confirmButton = (
    <button
      onClick={onConfirm}
      disabled={isProcessing}
      className={`px-4 py-2 rounded-lg ${currentVariant.buttonBg} text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center`}
    >
      {isProcessing ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Procesando...
        </>
      ) : (
        confirmText
      )}
    </button>
  );

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md transform transition-all animate-scale-in">
        {/* Encabezado */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          {showCloseButton && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
              disabled={isProcessing}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>

        {/* Cuerpo */}
        <div className="p-6">
          <div className="flex items-start">
            <div className={`flex-shrink-0 h-5 w-5 ${currentVariant.iconColor} mt-0.5`}>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                {selectedIcon}
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <div className="text-gray-800 dark:text-gray-100">
                {typeof message === 'string' ? <p>{message}</p> : message}
              </div>

              {details && (
                <div className={`mt-4 p-3 ${currentVariant.bgAccent} rounded-lg border ${currentVariant.borderAccent}`}>
                  <div className="text-sm text-gray-700 dark:text-gray-300">
                    {details}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pie */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl flex justify-end space-x-3">
          {reverseButtons ? (
            <>
              {confirmButton}
              {cancelButton}
            </>
          ) : (
            <>
              {cancelButton}
              {confirmButton}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConfirmationModal;
