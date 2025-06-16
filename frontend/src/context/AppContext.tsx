
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { AppState, CredentialsInfo, CandidateResult, EvaluationSummary } from '../types';
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
    content: '',
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
        criteria: { ...state.criteria, content: action.payload, loading: false }
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
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    if (type === 'success') {
      toast.success(message);
    } else if (type === 'error') {
      toast.error(message);
    } else {
      toast.info(message);
    }
  };

  return (
    <AppContext.Provider value={{ state, dispatch, showNotification }}>
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
