import React from 'react';

function IdleTimeoutModal({ isOpen, onStay, onLogout, countdown }) {
  if (!isOpen) return null;

  const minutes = Math.floor(countdown / 60);
  const seconds = countdown % 60;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4" aria-modal="true" role="dialog">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 md:p-8 max-w-sm w-full mx-4 text-center transform transition-all animate-fade-in">
        <h2 className="text-xl md:text-2xl font-bold text-gray-800 dark:text-gray-100 mb-3">Tu sesión está a punto de expirar</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Por inactividad, tu sesión se cerrará en:
        </p>
        <div className="text-4xl font-bold text-violet-500 mb-8">
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={onLogout}
            className="w-full px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 font-semibold rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200"
          >
            Cerrar Sesión
          </button>
          <button
            onClick={onStay}
            className="w-full px-4 py-2.5 bg-violet-600 text-white font-semibold rounded-lg hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-colors duration-200"
          >
            Permanecer Conectado
          </button>
        </div>
      </div>
    </div>
  );
}

export default IdleTimeoutModal;