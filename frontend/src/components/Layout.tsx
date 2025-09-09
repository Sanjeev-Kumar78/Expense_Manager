import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContextMock';
import { Button } from './ui/button';
import { 
  Home, 
  CreditCard, 
  BarChart3, 
  User, 
  LogOut, 
  DollarSign,
  Menu,
  X
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Expenses', href: '/expenses', icon: CreditCard },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Profile', href: '/profile', icon: User },
  ];

  return (
    <div className="h-screen flex bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-300 ease-in-out
        md:translate-x-0 md:static md:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-border">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-primary" />
            <span className="ml-2 text-xl font-bold text-foreground">ExpenseManager</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="mt-8 px-4">
          <div className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary text-primary-foreground' 
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                    }
                  `}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>

          <div className="mt-8 pt-4 border-t border-border">
            <div className="px-4 py-2">
              <p className="text-sm text-muted-foreground">Welcome,</p>
              <p className="text-sm font-medium text-foreground">{user?.full_name || user?.username}</p>
            </div>
            <Button
              variant="ghost"
              className="w-full justify-start mt-2 text-muted-foreground hover:text-foreground"
              onClick={handleLogout}
            >
              <LogOut className="mr-3 h-5 w-5" />
              Logout
            </Button>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top navigation */}
        <header className="bg-card border-b border-border h-16 flex items-center justify-between px-6">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-muted-foreground">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;