import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import type { DashboardMetrics } from '../types';
import { DollarSign, ShoppingBag, MessageCircle } from 'lucide-react';

export default function Dashboard() {
  const { data: metrics, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get<DashboardMetrics>('/admin/dashboard');
      return response.data;
    },
    refetchInterval: 60000, // Auto refresh every minute
  });

  if (isError) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded-lg">
        Error al cargar métricas del dashboard.
      </div>
    );
  }

  const cards = [
    { title: 'Ventas de Hoy', value: metrics?.ventas_hoy, icon: DollarSign, isCurrency: true },
    { title: 'Pedidos Activos', value: metrics?.pedidos_activos, icon: ShoppingBag, isCurrency: false },
    { title: 'Mensajes Bot', value: metrics?.mensajes_bot, icon: MessageCircle, isCurrency: false },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resumen del Día</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card, idx) => (
          <div key={idx} className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-100 dark:border-dark-border p-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.title}</p>
              {isLoading ? (
                <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mt-2"></div>
              ) : (
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {card.isCurrency ? '$' : ''}{card.value?.toLocaleString() || '0'}
                </p>
              )}
            </div>
            <div className="h-12 w-12 rounded-full bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center text-primary-600 dark:text-primary-500">
              <card.icon size={24} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
