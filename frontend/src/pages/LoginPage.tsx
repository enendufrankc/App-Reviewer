import React from 'react';
import { Navigate } from 'react-router-dom';
import Layout from '../components/Layout';
import LoginForm from '../components/LoginForm';
import { useApp } from '../context/AppContext';

const LoginPage: React.FC = () => {
  const { user, setUser, setCurrentUser } = useApp();

  const handleLogin = async (email: string, password: string): Promise<boolean> => {
    // Simulate authentication - in a real app, this would call an API
    if (email && password.length >= 3) {
      const userData = {
        id: `user_${Date.now()}`,
        email: email,
        name: email.split('@')[0],
        created_at: new Date().toISOString()
      };
      
      setUser(userData);
      setCurrentUser(userData); // Set current user for evaluations
      return true;
    }
    return false;
  };

  // If already logged in, redirect to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Layout>
      <div className="min-h-[60vh] flex items-center justify-center py-12">
        <LoginForm onLogin={handleLogin} />
      </div>
    </Layout>
  );
};

export default LoginPage;
