import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';
import type { Order, OrderStatus } from '../types';

const STATUS_COLORS: Record<OrderStatus, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREPARACION: 'bg-purple-100 text-purple-800',
  LISTO: 'bg-indigo-100 text-indigo-800',
  EN_CAMINO: 'bg-orange-100 text-orange-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
};

const STATUS_OPTIONS: OrderStatus[] = [
  'PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION', 'LISTO', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO'
];

export default function Orders() {
  const queryClient = useQueryClient();
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const { data: response, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: async () => {
      const { data } = await api.get<{data: Order[], total: number}>('/orders?page=1&limit=100');
      return data;
    },
    refetchInterval: 15000, // Refresh every 15s for realtime feel
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: OrderStatus }) => 
      api.patch(`/orders/${id}/status`, { estado: status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      toast.success('Estado actualizado');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al actualizar el estado');
    }
  });

  const orders = response?.data || [];
  const filteredOrders = filterStatus === 'ALL' ? orders : orders.filter(o => o.estado === filterStatus);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pedidos</h1>
        <select 
          value={filterStatus} 
          onChange={(e) => setFilterStatus(e.target.value)}
          className="border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="ALL">Todos los estados</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
      </div>

      <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-100 dark:border-dark-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
            <thead className="bg-gray-50 dark:bg-dark-bg text-gray-700 dark:text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium"># Pedido</th>
                <th className="px-6 py-4 font-medium">Origen</th>
                <th className="px-6 py-4 font-medium">Total</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Fecha</th>
                <th className="px-6 py-4 font-medium text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-dark-border">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div></td>
                    <td className="px-6 py-4"></td>
                  </tr>
                ))
              ) : filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-dark-bg/50 transition">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    #{order.numero || order.id.slice(0,8)}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-xs font-semibold uppercase">{order.origen}</span>
                  </td>
                  <td className="px-6 py-4 font-bold text-gray-900 dark:text-white">
                    ${order.total.toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={order.estado}
                      onChange={(e) => updateStatusMutation.mutate({ id: order.id, status: e.target.value as OrderStatus })}
                      className={`text-xs font-bold rounded-full px-2 py-1 outline-none border-0 cursor-pointer ${STATUS_COLORS[order.estado]}`}
                    >
                      {STATUS_OPTIONS.map(s => <option key={s} value={s} className="bg-white text-gray-900">{s.replace('_', ' ')}</option>)}
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {new Date(order.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {/* Placeholder para ver detalle */}
                    <button className="text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition" title="Ver Detalle">
                      <Eye size={20} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!isLoading && filteredOrders.length === 0 && (
            <div className="p-8 text-center text-gray-500">No hay pedidos para mostrar.</div>
          )}
        </div>
      </div>
    </div>
  );
}
