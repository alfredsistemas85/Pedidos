import { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  Pizza, 
  ShoppingBag, 
  Users, 
  Settings as SettingsIcon,
  LogOut,
  Moon,
  Sun,
  Menu,
  X
} from 'lucide-react';

export default function AdminLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isDark, setIsDark] = useState(() => localStorage.getItem('theme') === 'dark');
  const { logout, role } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/productos', icon: Pizza, label: 'Productos' },
    { to: '/pedidos', icon: ShoppingBag, label: 'Pedidos' },
    { to: '/clientes', icon: Users, label: 'Clientes' },
    { to: '/configuracion', icon: SettingsIcon, label: 'Configuración' },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50 dark:bg-dark-bg">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-white dark:bg-dark-card border-b dark:border-dark-border">
        <h1 className="text-xl font-bold text-primary-600">Más Pizzas</h1>
        <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2">
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'block' : 'hidden'} md:block w-full md:w-64 bg-white dark:bg-dark-card border-r dark:border-dark-border flex-shrink-0 transition-all`}>
        <div className="h-full flex flex-col">
          <div className="hidden md:flex p-6 items-center justify-center border-b dark:border-dark-border">
            <h1 className="text-2xl font-bold text-primary-600 tracking-tight">Más Pizzas <span className="text-xs text-gray-500 block uppercase">{role}</span></h1>
          </div>
          
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                    isActive 
                      ? 'bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-500' 
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-border'
                  }`
                }
              >
                <item.icon size={20} />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="p-4 border-t dark:border-dark-border space-y-2">
            <button 
              onClick={() => setIsDark(!isDark)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-dark-border transition-colors"
            >
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
              {isDark ? 'Modo Claro' : 'Modo Oscuro'}
            </button>
            <button 
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium text-red-600 hover:bg-red-50 dark:text-red-500 dark:hover:bg-red-500/10 transition-colors"
            >
              <LogOut size={20} />
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-4 md:p-8">
        <Outlet />
      </main>
    </div>
  );
}
