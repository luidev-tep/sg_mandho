import { createContext, useContext, useReducer, useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import IdleTimeoutModal from './IdleTimeoutModal';

const AuthContext = createContext();

// Cargar usuario desde localStorage si no ha expirado (máximo 3 horas)
function loadUserFromStorage() {
  try {
    const stored = localStorage.getItem('usuario');
    if (!stored) return null;

    const { usuario, timestamp } = JSON.parse(stored);
    const now = Date.now();
    const threeHours = 3 * 60 * 60 * 1000;

    if (now - timestamp > threeHours) {
      localStorage.removeItem('usuario');
      return null;
    }

    return usuario;
  } catch {
    return null;
  }
}

// Cargar tokens desde localStorage
function loadTokensFromStorage() {
  try {
    const stored = localStorage.getItem('tokens');
    if (!stored) return null;

    const { tokens, refreshTokenTimestamp } = JSON.parse(stored);
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;

    // Si el refresh token tiene más de un día, lo consideramos expirado
    if (now - refreshTokenTimestamp > oneDay) {
      localStorage.removeItem('usuario');
      localStorage.removeItem('tokens');
      return null;
    }

    return tokens;
  } catch {
    return null;
  }
}

function authReducer(state, action) {
  switch (action.type) {
    case "SET_USER":
      const usuario = action.payload;
      localStorage.setItem('usuario', JSON.stringify({
        usuario,
        timestamp: Date.now()
      }));
      return { ...state, usuario };
    case "SET_TOKENS":
      const tokens = action.payload;
      localStorage.setItem('tokens', JSON.stringify({
        tokens,
        refreshTokenTimestamp: Date.now() // Guardamos timestamp para el refresh token
      }));
      return { ...state, tokens };
    case "SET_USER_AND_TOKENS":
      const { usuario: user, tokens: userTokens } = action.payload;
      localStorage.setItem('usuario', JSON.stringify({
        usuario: user,
        timestamp: Date.now(),
      }));
      // Guardamos los tokens junto con el timestamp para el refresh token
      localStorage.setItem('tokens', JSON.stringify({
        tokens: userTokens,
        refreshTokenTimestamp: Date.now()
      }));
      return { ...state, usuario: user, tokens: userTokens };
    case "CLEAR_USER":
      localStorage.removeItem('usuario');
      localStorage.removeItem('tokens');
      return { ...state, usuario: null, tokens: null };
    default:
      return state;
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, {
    usuario: loadUserFromStorage(),
    tokens: loadTokensFromStorage()
  });

  const navigate = useNavigate();
  const location = useLocation();

  // --- Lógica de Inactividad ---
  const [showIdleModal, setShowIdleModal] = useState(false);
  const [countdown, setCountdown] = useState(180); // 3 minutos en segundos
  const idleTimer = useRef(null);
  const countdownTimer = useRef(null);

  const INACTIVITY_TIMEOUT = 10 * 60 * 1000; // 10 minutos
  const COUNTDOWN_SECONDS = 3 * 60; // 3 minutos

  const handleLogout = useCallback(() => {
    setShowIdleModal(false);
    clearTimeout(idleTimer.current);
    clearInterval(countdownTimer.current);
    dispatch({ type: 'CLEAR_USER' });
    navigate('/Signup', { replace: true });
  }, [dispatch, navigate]);

  const handleStay = () => {
    setShowIdleModal(false);
    clearInterval(countdownTimer.current);
    setCountdown(COUNTDOWN_SECONDS);
    resetIdleTimer();
  };

  const startWarning = () => {
    setCountdown(COUNTDOWN_SECONDS); // Reinicia el contador cada vez que se muestra el modal
    setShowIdleModal(true);
    countdownTimer.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(countdownTimer.current);
          handleLogout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const resetIdleTimer = useCallback(() => {
    clearTimeout(idleTimer.current);
    if (state.usuario) {
      idleTimer.current = setTimeout(startWarning, INACTIVITY_TIMEOUT);
    }
  }, [state.usuario, INACTIVITY_TIMEOUT]);

  useEffect(() => {
    const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'];
    
    if (state.usuario) {
      events.forEach(event => window.addEventListener(event, resetIdleTimer));
      resetIdleTimer();
    }

    return () => {
      events.forEach(event => window.removeEventListener(event, resetIdleTimer));
      clearTimeout(idleTimer.current);
      clearInterval(countdownTimer.current);
    };
  }, [resetIdleTimer, state.usuario]);
  // --- Fin Lógica de Inactividad ---

  // Efecto para redirigir al login si no hay usuario
  useEffect(() => {
    // Si no hay usuario ni tokens, y no estamos ya en la página de login, redirigimos.
    if (!state.usuario && !state.tokens && location.pathname !== '/Signup') {
      console.log("Sesión no válida o expirada. Redirigiendo a la página de login...");
      navigate('/Signup', { replace: true });
    }
  }, [state.usuario, state.tokens, location.pathname, navigate]);

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      <IdleTimeoutModal
        isOpen={showIdleModal}
        onStay={handleStay}
        onLogout={handleLogout}
        countdown={countdown}
      />
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}