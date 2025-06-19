import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Settings, FileSpreadsheet, BarChart3, LogOut, Sparkles, Home } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useUser } from '../context/UserContext';
import { Button } from './ui/button';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, setUser } = useApp();
  const { logout: userLogout } = useUser();

  const handleLogout = () => {
    // Clear both contexts
    setUser(null);
    userLogout();
    // Navigate to landing page
    navigate('/');
  };

  const navigationItems = [
    {
      name: 'Home',
      href: '/',
      icon: Home,
      description: 'Go to landing page'
    },
    {
      name: 'Admin Setup',
      href: '/admin',
      icon: Settings,
      description: 'Configure system settings'
    },
    {
      name: 'Evaluate Candidates',
      href: '/evaluate',
      icon: FileSpreadsheet,
      description: 'Upload and evaluate applications'
    },
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: BarChart3,
      description: 'View evaluation results'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo - Always navigate to home */}
            <Link to="/" className="flex items-center gap-2">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">LBS YTP Evaluator</span>
            </Link>

            {/* Navigation - Only show if logged in */}
            {user && (
              <nav className="hidden md:flex items-center space-x-8">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.href;
                  
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* User menu */}
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  Welcome, <strong>{user.name || user.email.split('@')[0]}</strong>
                </span>
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button
                onClick={() => navigate('/')}
                variant="default"
                size="sm"
              >
                Sign In
              </Button>
            )}
          </div>

          {/* Mobile Navigation */}
          {user && (
            <div className="md:hidden border-t pt-4 pb-4">
              <nav className="flex flex-col space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.href;
                  
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;
