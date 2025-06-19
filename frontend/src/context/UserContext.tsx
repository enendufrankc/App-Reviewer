import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  userEmail: string;
  userName: string;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  setUserName: (name: string) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userEmail, setUserEmail] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    // Load user data from localStorage on app start
    const savedEmail = localStorage.getItem('userEmail');
    const savedName = localStorage.getItem('userName');
    const authStatus = localStorage.getItem('isAuthenticated');
    
    if (savedEmail && authStatus === 'true') {
      setUserEmail(savedEmail);
      setUserName(savedName || '');
      setIsAuthenticated(true);
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      // For now, we'll use a simple client-side validation
      // In a real app, this would make an API call to authenticate
      
      // Basic validation rules for demo purposes
      if (!email || !password) {
        return false;
      }
      
      if (!email.includes('@')) {
        return false;
      }
      
      if (password.length < 3) {
        return false;
      }
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo: accept any email/password combination that meets basic criteria
      setUserEmail(email);
      setUserName(email.split('@')[0]); // Use email prefix as name
      setIsAuthenticated(true);
      
      // Store in localStorage
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', email.split('@')[0]);
      localStorage.setItem('isAuthenticated', 'true');
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    setUserEmail('');
    setUserName('');
    setIsAuthenticated(false);
    
    // Clear localStorage
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    localStorage.removeItem('isAuthenticated');
  };

  const handleSetUserName = (name: string) => {
    setUserName(name);
    localStorage.setItem('userName', name);
  };

  return (
    <UserContext.Provider value={{
      userEmail,
      userName,
      isAuthenticated,
      login,
      logout,
      setUserName: handleSetUserName
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
