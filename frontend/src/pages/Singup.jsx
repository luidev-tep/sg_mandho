import { useForm } from 'react-hook-form';
import { useState } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';
import { ObtenerUsuario } from '../api/api_auth';
import AuthImage from "../images/auth-image.jpg";
import { useAuth } from '../utils/AuthContext';
import { useNavigate } from 'react-router-dom';

function Signup() {
  const { 
    register, 
    handleSubmit, 
    formState: { errors }, 
    setValue
  } = useForm({
    mode: 'onChange'
  });

  const { dispatch } = useAuth();
  const navigate = useNavigate();
  const [recaptchaError, setRecaptchaError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const [isThrottled, setIsThrottled] = useState(false);

  const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY;

  const onSubmit = handleSubmit(async (data) => {
    if (isThrottled) return;

    setIsThrottled(true);
    setTimeout(() => setIsThrottled(false), 1000);

    if (!data.recaptcha) {
      setRecaptchaError("Por favor completa el reCAPTCHA");
      return;
    }

    setIsSubmitting(true); 
    setApiError(null);
    setLoginSuccess(false);

    try {
      const response = await ObtenerUsuario(data);

      dispatch({ 
        type: "SET_USER_AND_TOKENS", 
        payload: {
          usuario: response.data,
          tokens: response.tokens
        }
      });

      setLoginSuccess(true);
      setTimeout(() => {
        navigate('/');
      }, 1500);

    } catch (error) {
      console.error("Error al obtener datos del usuario:", error);
      const errorMessage = error.response?.data?.message || error.message || "Error al iniciar sesión. Verifique sus credenciales.";
      setApiError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  });

  const onRecaptchaChange = (value) => {
    setValue('recaptcha', value);
    setRecaptchaError(null);
    setApiError(null);
  };

  return (
    <main className="bg-white dark:bg-gray-900">
      <div className="relative md:flex">
        {/* Content */}
        <div className="md:w-1/2">
          <div className="min-h-[100dvh] h-full flex flex-col after:flex-1">
            <div className="flex-1">
              <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
                <svg className="fill-violet-500" xmlns="http://www.w3.org/2000/svg" width={32} height={32}>
                  <path d="M31.956 14.8C31.372 6.92 25.08.628 17.2.044V5.76a9.04 9.04 0 0 0 9.04 9.04h5.716ZM14.8 26.24v5.716C6.92 31.372.63 25.08.044 17.2H5.76a9.04 9.04 0 0 1 9.04 9.04Zm11.44-9.04h5.716c-.584 7.88-6.876 14.172-14.756 14.756V26.24a9.04 9.04 0 0 1 9.04-9.04ZM.044 14.8C.63 6.92 6.92.628 14.8.044V5.76a9.04 9.04 0 0 1-9.04 9.04H.044Z" />
                </svg>
              </div>
            </div>

            <div className="max-w-sm mx-auto w-full px-4 py-8">
              <center><h1 className="text-3xl text-gray-800 dark:text-gray-100 font-bold mb-6">Bienvenido</h1></center>

              <form onSubmit={onSubmit}>
                {/* Mensaje de éxito */}
                {loginSuccess && (
                  <div className="mb-4 p-3 bg-green-100 dark:bg-green-900/50 border border-green-400 dark:border-green-700 text-green-900 dark:text-white rounded-lg text-center animate-fade-in">
                    ¡Inicio de sesión exitoso! Redirigiendo...
                  </div>
                )}

                {/* Mensaje de error de la API */}
                {apiError && (
                  <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/50 border border-red-400 dark:border-red-700 text-red-900 dark:text-white rounded-lg text-center animate-fade-in">
                    {apiError}
                  </div>
                )}

                {/* Mensaje de error de reCAPTCHA */}
                {recaptchaError && (
                  <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/50 border border-red-400 dark:border-red-700 text-red-900 dark:text-white rounded-lg text-center animate-fade-in">
                    {recaptchaError}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="name">
                      Usuario <span className="text-red-500">*</span>
                    </label>
                    <input 
                      id="name" 
                      className={`text-gray-900 dark:bg-gray-100 dark:text-gray-700 form-input w-full ${errors.name ? 'border-red-500' : ''}`} 
                      type="text"
                      {...register("name", {
                        required: 'El usuario es requerido',
                        pattern: {
                          value: /^[A-Za-zÁÉÍÓÚáéíóúñÑ0-9]+$/i,
                          message: 'Solo se permiten letras sin espacios'
                        }
                      })}
                      onChange={() => setApiError(null)}
                    />
                    {errors.name && (
                      <span className="text-red-500 text-sm">{errors.name.message}</span>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="role">
                      Rol <span className="text-red-500">*</span>
                    </label>
                    <select 
                      id="role" 
                      className="text-gray-900 dark:bg-gray-100 dark:text-gray-700 form-select w-full"
                      {...register("role", { required: 'Selecciona un rol' })}
                      onChange={() => setApiError(null)}
                    >
                      <option value="">Selecciona un rol</option>
                      <option value="delegado">Delegado</option>
                      <option value="subdelegado">Subdelegado</option>
                      <option value="comitiva">Comitiva</option>
                      <option value="vecino">Vecino</option>
                    </select>
                    {errors.role && (
                      <span className="text-red-500 text-sm">{errors.role.message}</span>
                    )}
                  </div>
                  
                  {/* Manzana */}
                  <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="manzana">
                      Manzana <span className="text-red-500">*</span>
                    </label>
                    <select 
                      id="manzana" 
                      className={`form-select dark:text-gray-800 w-full rounded-lg ${errors.manzana ? 'border-red-500' : 'border-gray-300'} ${isSubmitting ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                      {...register("manzana", { 
                        required: 'La manzana es requerida',
                        validate: value => [
                          'tepetate', 
                          'cerritos', 
                          'garambullo', 
                          'yhonda', 
                          'centro', 
                          'buenavista'
                        ].includes(value) || 'Seleccione una manzana válida'
                      })}
                      onChange={() => setApiError(null)}
                      disabled={isSubmitting}
                    >
                      <option value="">Seleccione una opción</option>
                      <option value="tepetate">Tepetate</option>
                      <option value="cerritos">Cerritos</option>
                      <option value="garambullo">Garambullo</option>
                      <option value="yhonda">Yhonda</option>
                      <option value="centro">Centro</option>
                      <option value="buenavista">Buena Vista</option>
                    </select>
                    {errors.manzana && (
                      <span className="text-red-500 text-sm mt-1 block animate-fade-in">
                        {errors.manzana.message}
                      </span>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="password">
                      Contraseña <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input 
                        id="password" 
                        className={`text-gray-900 dark:bg-gray-100 dark:text-gray-700 form-input w-full pr-10 ${errors.password ? 'border-red-500' : ''}`} 
                        type="password" 
                        autoComplete="on"
                        {...register("password", {
                          required: 'La contraseña es requerida',
                          minLength: {
                            value: 8,
                            message: 'La contraseña debe tener al menos 8 caracteres'
                          }
                        })}
                        onChange={() => setApiError(null)}
                      />
                      <button 
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-600 dark:text-gray-400"
                        onClick={() => {
                          const passwordInput = document.getElementById('password');
                          if (passwordInput.type === 'password') {
                            passwordInput.type = 'text';
                          } else {
                            passwordInput.type = 'password';
                          }
                        }}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                    </div>
                    {errors.password && (
                      <span className="text-red-500 text-sm">{errors.password.message}</span>
                    )}
                  </div>
                </div>
                <div className="mt-6">
                  <div className="scale-80 origin-left mb-4">
                    <ReCAPTCHA
                      sitekey={RECAPTCHA_SITE_KEY}
                      onChange={onRecaptchaChange}
                    />
                  </div>
                  <button 
                    type="submit" 
                    className="w-full px-6 py-3 bg-gradient-to-r from-gray-800 to-gray-900 text-white font-medium rounded-lg shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isSubmitting || loginSuccess || isThrottled}
                  >
                    <span className="relative z-10">
                      {isSubmitting ? 'Procesando...' : 'Ingresar'}
                    </span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div className="hidden md:block absolute top-0 bottom-0 right-0 md:w-1/2">
          <img className="object-cover object-center w-full h-full" src={AuthImage} width="760" height="1024" alt="Authentication" />
        </div>
      </div>
    </main>
  );
}

export default Signup;