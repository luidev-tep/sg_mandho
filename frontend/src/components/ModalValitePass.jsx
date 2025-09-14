import { useState } from "react";
import { validatePassword } from "../api/api_security";


//Modal muy importante para bloquear distintos recursos
function PasswordVerificationModal({ onClose, onVerificationSuccess, title = "Verificación de Seguridad", message = "Ingrese su contraseña para continuar con esta acción especial." }) {
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleVerifyPassword = async () => {
    if (!password.trim()) {
      setError("La contraseña es requerida");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await validatePassword({ password: password.trim() });
      
      // CORRECCIÓN: Verificar directamente response.data ya que es un boolean
      if (response?.data === true) {
        // Notificar al componente padre que la verificación fue exitosa
        if (onVerificationSuccess) {
          onVerificationSuccess(response.data);
        }
        onClose();
      } else {
        // Si response.data es false o no existe, mostrar error
        setError("Contraseña incorrecta. Verifique e intente nuevamente.");
      }
    } catch (err) {
      console.error('Error en verificación de contraseña:', err);
      setError("Error al verificar la contraseña. Intente nuevamente.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isSubmitting) {
      handleVerifyPassword();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md transform transition-all animate-scale-in">
        {/* Encabezado */}
        <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
            disabled={isSubmitting}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0 h-5 w-5 text-blue-500 mt-0.5">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 w-full">
              <h3 className="text-lg font-medium text-gray-800 dark:text-gray-100 mb-2">
                Autenticación Requerida
              </h3>
              <div className="text-gray-600 dark:text-gray-400 mb-4">
                <p>{message}</p>
              </div>

              {/* Campo de contraseña */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2" htmlFor="password-verification">
                    Contraseña <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input 
                      id="password-verification"
                      className="form-input w-full text-base py-3 px-4 pr-12" 
                      type={showPassword ? "text" : "password"}
                      placeholder="Ingrese su contraseña"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={isSubmitting}
                      autoFocus
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={isSubmitting}
                    >
                      {showPassword ? (
                        <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.543 7-1.275 4.057-5.065 7-9.543 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-300 rounded-lg text-sm border border-red-100 dark:border-red-900/30">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}
        </div>

        {/* Pie */}
        <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/30 rounded-b-2xl flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleVerifyPassword}
            disabled={isSubmitting || !password.trim()}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors disabled:opacity-50 flex items-center"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Verificando...
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Verificar
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default PasswordVerificationModal;