import { createContext, useContext, useReducer, useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import IdleTimeoutModal from './IdleTimeoutModal';
import { RefrescarToken } from './../api/api_auth';
import { setupInterceptors } from '../api/axiosInstance';

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
      // Si el usuario expira, también eliminar los tokens
      localStorage.removeItem('usuario');
      localStorage.removeItem('tokens');
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
      // Si los tokens expiran, también eliminar el usuario
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
        refreshTokenTimestamp: Date.now()
      }));
      return { ...state, tokens };
    case "SET_USER_AND_TOKENS":
      const { usuario: user, tokens: userTokens } = action.payload;
      localStorage.setItem('usuario', JSON.stringify({
        usuario: user,
        timestamp: Date.now(),
      }));
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

  // Configurar interceptores de Axios una sola vez
  useEffect(() => {
    setupInterceptors({ dispatch });
  }, []);

  const navigate = useNavigate();
  const location = useLocation();

  // --- Lógica de Inactividad ---
  const [showIdleModal, setShowIdleModal] = useState(false);
  const [countdown, setCountdown] = useState(180);
  const idleTimer = useRef(null);
  const countdownTimer = useRef(null);
  const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutos
  const COUNTDOWN_SECONDS = 3 * 60; // 3 minutos

  const handleLogout = useCallback(() => {
    setShowIdleModal(false);
    clearTimeout(idleTimer.current);
    clearInterval(countdownTimer.current);
    dispatch({ type: 'CLEAR_USER' });
    navigate('/Signup', { replace: true });
  }, [navigate]);

  const handleStay = () => {
    setShowIdleModal(false);
    clearInterval(countdownTimer.current);
    setCountdown(COUNTDOWN_SECONDS);
    resetIdleTimer();
  };

  const startWarning = () => {
    setCountdown(COUNTDOWN_SECONDS);
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
  }, [state.usuario]);

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

  // --- RENOVACIÓN DE TOKEN ---
  const tokenRenewalIntervalRef = useRef(null);
  const lastRenewalTimeRef = useRef(Date.now());

  const renewToken = useCallback(async () => {
    try {
      const tokensString = localStorage.getItem('tokens');
      if (!tokensString) {
        handleLogout();
        return;
      }

      const storedData = JSON.parse(tokensString);
      const tokens = storedData?.tokens;
      const refreshToken = tokens?.refresh_token;

      if (!refreshToken) {
        handleLogout();
        return;
      }
      
      const newAccessToken = await RefrescarToken(refreshToken);
      
      const newTokens = {
        access_token: newAccessToken,
        refresh_token: refreshToken,
      };

      dispatch({ type: 'SET_TOKENS', payload: newTokens });
      lastRenewalTimeRef.current = Date.now();

    } catch (error) {
      console.error('Error al renovar token:', error);
      handleLogout();
    }
  }, [handleLogout]);

  useEffect(() => {
    const RENEWAL_INTERVAL = 15 * 60 * 1000; // 15 minutos (renovar antes de que expire a los 20 min)

    if (tokenRenewalIntervalRef.current) {
      clearInterval(tokenRenewalIntervalRef.current);
    }

    if (state.tokens?.access_token && state.tokens?.refresh_token) {
      const timeSinceLastRenewal = Date.now() - lastRenewalTimeRef.current;
      
      if (timeSinceLastRenewal >= RENEWAL_INTERVAL) {
        renewToken();
      }

      tokenRenewalIntervalRef.current = setInterval(() => {
        renewToken();
      }, RENEWAL_INTERVAL);
    }

    return () => {
      if (tokenRenewalIntervalRef.current) {
        clearInterval(tokenRenewalIntervalRef.current);
      }
    };
  }, [state.tokens?.access_token, state.tokens?.refresh_token, renewToken]);

  // Efecto para redirigir al login si no hay usuario O no hay tokens
  useEffect(() => {
    // Verificar que AMBOS existan, si falta cualquiera de los dos, redirigir
    if ((!state.usuario || !state.tokens) && location.pathname !== '/Signup') {
      // Si hay inconsistencia (uno existe pero el otro no), limpiar todo
      if (state.usuario || state.tokens) {
        dispatch({ type: 'CLEAR_USER' });
      }
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