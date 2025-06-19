import React, { createContext, useContext, useReducer, ReactNode, useState } from 'react';
import { AppState, CredentialsInfo, CandidateResult, EvaluationSummary, User } from '../types';
import { toast } from 'sonner';

type AppAction = 
  | { type: 'SET_CREDENTIALS_LOADING'; payload: boolean }
  | { type: 'SET_CREDENTIALS_INFO'; payload: CredentialsInfo | null }
  | { type: 'SET_CRITERIA_LOADING'; payload: boolean }
  | { type: 'SET_CRITERIA_CONTENT'; payload: string }
  | { type: 'SET_EVALUATION_LOADING'; payload: boolean }
  | { type: 'SET_EVALUATION_RESULTS'; payload: { results: CandidateResult[]; summary: EvaluationSummary } };

const initialState: AppState = {
  credentials: {
    isConfigured: false,
    info: null,
    loading: false,
  },
  criteria: {
    content: '', // Ensure this is always a string, never undefined
    loading: false,
  },
  evaluation: {
    results: [],
    summary: null,
    loading: false,
  },
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CREDENTIALS_LOADING':
      return {
        ...state,
        credentials: { ...state.credentials, loading: action.payload }
      };
    case 'SET_CREDENTIALS_INFO':
      return {
        ...state,
        credentials: {
          ...state.credentials,
          info: action.payload,
          isConfigured: !!action.payload,
          loading: false
        }
      };
    case 'SET_CRITERIA_LOADING':
      return {
        ...state,
        criteria: { ...state.criteria, loading: action.payload }
      };
    case 'SET_CRITERIA_CONTENT':
      return {
        ...state,
        criteria: { 
          ...state.criteria, 
          content: action.payload || '', // Ensure it's never undefined
          loading: false 
        }
      };
    case 'SET_EVALUATION_LOADING':
      return {
        ...state,
        evaluation: { ...state.evaluation, loading: action.payload }
      };
    case 'SET_EVALUATION_RESULTS':
      return {
        ...state,
        evaluation: {
          ...state.evaluation,
          results: action.payload.results,
          summary: action.payload.summary,
          loading: false
        }
      };
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  showNotification: (message: string, type?: 'success' | 'error' | 'info') => void;
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;
  user: User | null;  // Add this for compatibility
  setUser: (user: User | null) => void;  // Add this for compatibility
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    if (type === 'success') {
      toast.success(message);
    } else if (type === 'error') {
      toast.error(message);
    } else {
      toast.info(message);
    }
  };

  // For compatibility, use the same state for both user and currentUser
  const setUser = (user: User | null) => {
    setCurrentUser(user);
  };

  const value: AppContextType = {
    state,
    dispatch,
    showNotification,
    currentUser,
    setCurrentUser,
    user: currentUser,  // Same as currentUser
    setUser,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);

  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
