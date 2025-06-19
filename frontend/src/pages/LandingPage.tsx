import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Settings, FileSpreadsheet, BarChart3, ArrowRight, Sparkles, Users, Shield, LogOut } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { useUser } from '../context/UserContext';
import { useApp } from '../context/AppContext';
import { Button } from '@/components/ui/button';
import LoginForm from '../components/LoginForm';

const LandingPage = () => {
  const { userEmail, userName, isAuthenticated, login, logout } = useUser();
  const { user, setUser } = useApp(); 
  const navigate = useNavigate();

  // Sync user contexts but don't auto-redirect - let users stay on landing page
  useEffect(() => {
    if (isAuthenticated && userEmail && !user) {
      // Sync the user context
      const userData = {
        id: `user_${Date.now()}`,
        email: userEmail,
        name: userName || userEmail.split('@')[0],
        created_at: new Date().toISOString()
      };
      setUser(userData);
    }
  }, [isAuthenticated, userEmail, user, setUser, userName]);

  const features = [
    {
      icon: Settings,
      title: 'Admin Setup',
      description: 'Configure Google Drive credentials and define eligibility criteria for YTP candidate evaluation',
      href: '/admin',
      color: 'bg-blue-500'
    },
    {
      icon: FileSpreadsheet,
      title: 'Evaluate Candidates',
      description: 'Upload CSV files and let AI evaluate YTP applicants against program criteria',
      href: '/evaluate',
      color: 'bg-green-500'
    },
    {
      icon: BarChart3,
      title: 'View Results',
      description: 'Review evaluation results, view detailed applicant profiles and export data',
      href: '/dashboard',
      color: 'bg-purple-500'
    }
  ];

  const stats = [
    { label: 'AI-Powered', value: '100%', icon: Sparkles },
    { label: 'Accurate', value: '99%', icon: Shield },
    { label: 'Efficient', value: '10x', icon: Users }
  ];

  const handleLogin = async (email: string, password: string): Promise<boolean> => {
    // Enhanced login validation
    if (email && password.length >= 3) {
      // Call the UserContext login
      const success = await login(email, password);
      
      if (success) {
        // Also set the AppContext user
        const userData = {
          id: `user_${Date.now()}`,
          email: email,
          name: email.split('@')[0],
          created_at: new Date().toISOString()
        };
        setUser(userData);
        
        // Don't auto-redirect - let user choose where to go
        return true;
      }
    }
    return false;
  };

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  // Show login form if not authenticated
  if (!isAuthenticated && !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
        <header className="relative overflow-hidden bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col items-center mb-8">
              <div className="text-center mb-8">
                <div className="flex items-center justify-center mb-6">
                  <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                    <Sparkles className="h-8 w-8 text-white" />
                  </div>
                </div>
                <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-4 leading-tight">
                  LBS Young Talent Program Evaluator
                </h1>
                <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed font-light">
                  Streamline your Young Talents Programme application evaluation with intelligent AI-powered assessment for Lagos Business School
                </p>
              </div>
              
              <LoginForm onLogin={handleLogin} />
            </div>
          </div>
        </header>

        <footer className="bg-gray-900 text-white py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-gray-400">
              © 2024 Lagos Business School Young Talent Program Evaluator. Powered by advanced AI technology.
            </p>
          </div>
        </footer>
      </div>
    );
  }

  // Show authenticated landing page (when user is logged in)
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <header className="relative overflow-hidden bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">YTP Evaluator</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Welcome, {user?.name || user?.email}</span>
              <Button onClick={handleLogout} variant="outline" size="sm">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
          
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-6 leading-tight">
              Welcome to YTP Evaluator
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Transform your Young Talents Programme evaluation process with our comprehensive AI-powered assessment system
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="group hover:shadow-xl transition-all duration-300 border-0 bg-white/70 backdrop-blur-sm hover:bg-white/90">
              <CardContent className="p-8">
                <div className="text-center">
                  <div className={`inline-flex p-4 rounded-2xl ${feature.color} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-8 leading-relaxed">
                    {feature.description}
                  </p>
                  <Link
                    to={feature.href}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-300 group-hover:scale-105"
                  >
                    Get Started
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Transform Your YTP Evaluation?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Start with setting up your system configuration for the Young Talents Programme
          </p>
          <Link
            to="/admin"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 font-bold rounded-xl hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            Begin Setup
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 Lagos Business School Young Talent Program Evaluator. Powered by advanced AI technology.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;