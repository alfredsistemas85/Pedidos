import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Plus, Edit2, Trash2, X, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';
import type { Product } from '../types';

const productSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  descripcion: z.string().optional(),
  precio: z.number().min(0, 'El precio debe ser positivo'),
  categoria: z.string().min(1, 'La categoría es requerida'),
  imagen_url: z.string().url('URL inválida').optional().or(z.literal('')),
  stock_controlado: z.boolean(),
  stock: z.number().min(0),
});

type ProductForm = z.infer<typeof productSchema>;

export default function Products() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<ProductForm>({
    resolver: zodResolver(productSchema),
    defaultValues: { stock_controlado: false, stock: 0 }
  });

  const stockControlado = watch('stock_controlado');

  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const { data } = await api.get<Product[]>('/products');
      return data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (newProduct: ProductForm) => api.post('/products', newProduct),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Producto creado exitosamente');
      closeModal();
    },
    onError: () => toast.error('Error al crear el producto'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProductForm }) => api.patch(`/products/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Producto actualizado exitosamente');
      closeModal();
    },
    onError: () => toast.error('Error al actualizar el producto'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/products/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Producto eliminado');
      setDeletingId(null);
    },
    onError: () => toast.error('Error al eliminar el producto'),
  });

  const openModal = (product?: Product) => {
    if (product) {
      setEditingProduct(product);
      reset({
        nombre: product.nombre,
        descripcion: product.descripcion,
        precio: product.precio,
        categoria: product.categoria,
        imagen_url: product.imagen_url || '',
        stock_controlado: product.stock_controlado,
        stock: product.stock,
      });
    } else {
      setEditingProduct(null);
      reset({});
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
    reset();
  };

  const onSubmit = (data: ProductForm) => {
    if (editingProduct) {
      updateMutation.mutate({ id: editingProduct.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Productos</h1>
        <button
          onClick={() => openModal()}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-700 transition"
        >
          <Plus size={20} />
          Nuevo Producto
        </button>
      </div>

      <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-100 dark:border-dark-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400">
            <thead className="bg-gray-50 dark:bg-dark-bg text-gray-700 dark:text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium">Producto</th>
                <th className="px-6 py-4 font-medium">Categoría</th>
                <th className="px-6 py-4 font-medium">Precio</th>
                <th className="px-6 py-4 font-medium">Stock</th>
                <th className="px-6 py-4 font-medium text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-dark-border">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div></td>
                    <td className="px-6 py-4"><div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div></td>
                    <td className="px-6 py-4"></td>
                  </tr>
                ))
              ) : products?.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50 dark:hover:bg-dark-bg/50 transition">
                  <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    {product.nombre}
                  </td>
                  <td className="px-6 py-4">{product.categoria}</td>
                  <td className="px-6 py-4">${product.precio.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    {product.stock_controlado ? (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${product.stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {product.stock} un.
                      </span>
                    ) : (
                      <span className="text-gray-400">Sin límite</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right space-x-3">
                    <button onClick={() => openModal(product)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400">
                      <Edit2 size={18} />
                    </button>
                    <button onClick={() => setDeletingId(product.id)} className="text-red-600 hover:text-red-800 dark:text-red-400">
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!isLoading && products?.length === 0 && (
            <div className="p-8 text-center text-gray-500">No hay productos registrados.</div>
          )}
        </div>
      </div>

      {/* Modal Crear/Editar */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-dark-card rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b dark:border-dark-border">
              <h2 className="text-xl font-bold dark:text-white">
                {editingProduct ? 'Editar Producto' : 'Nuevo Producto'}
              </h2>
              <button onClick={closeModal} className="text-gray-500 hover:text-gray-700 dark:text-gray-400"><X size={24} /></button>
            </div>
            <form onSubmit={handleSubmit((data) => onSubmit(data as ProductForm))} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nombre</label>
                <input {...register('nombre')} className="mt-1 w-full rounded-md border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white px-3 py-2 border focus:ring-primary-500 focus:border-primary-500" />
                {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Categoría</label>
                <input {...register('categoria')} className="mt-1 w-full rounded-md border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white px-3 py-2 border focus:ring-primary-500 focus:border-primary-500" />
                {errors.categoria && <p className="text-red-500 text-xs mt-1">{errors.categoria.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Precio</label>
                <input type="number" step="0.01" {...register('precio', { valueAsNumber: true })} className="mt-1 w-full rounded-md border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white px-3 py-2 border focus:ring-primary-500 focus:border-primary-500" />
                {errors.precio && <p className="text-red-500 text-xs mt-1">{errors.precio.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Descripción</label>
                <textarea {...register('descripcion')} className="mt-1 w-full rounded-md border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white px-3 py-2 border focus:ring-primary-500 focus:border-primary-500" rows={3}></textarea>
              </div>

              <div className="flex items-center gap-2">
                <input type="checkbox" id="stock_controlado" {...register('stock_controlado')} className="rounded text-primary-600 focus:ring-primary-500" />
                <label htmlFor="stock_controlado" className="text-sm text-gray-700 dark:text-gray-300">Controlar Stock</label>
              </div>

              {stockControlado && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Cantidad en Stock</label>
                  <input type="number" {...register('stock', { valueAsNumber: true })} className="mt-1 w-full rounded-md border-gray-300 dark:border-dark-border dark:bg-dark-bg dark:text-white px-3 py-2 border focus:ring-primary-500 focus:border-primary-500" />
                </div>
              )}

              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={closeModal} className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition">Cancelar</button>
                <button type="submit" disabled={createMutation.isPending || updateMutation.isPending} className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deletingId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-dark-card rounded-xl max-w-sm w-full p-6 text-center space-y-4">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-500/10">
              <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-500" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">¿Eliminar producto?</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Esta acción no se puede deshacer de forma visual.</p>
            <div className="flex gap-3 justify-center mt-6">
              <button onClick={() => setDeletingId(null)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">Cancelar</button>
              <button onClick={() => deleteMutation.mutate(deletingId)} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
