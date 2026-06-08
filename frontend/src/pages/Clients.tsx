import { Users } from 'lucide-react';

export default function Clients() {
  return (
    <div className="h-[80vh] flex flex-col items-center justify-center text-center">
      <div className="bg-primary-50 dark:bg-primary-500/10 p-4 rounded-full mb-4">
        <Users className="w-12 h-12 text-primary-600 dark:text-primary-500" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Gestión de Clientes
      </h2>
      <p className="text-gray-500 dark:text-gray-400 max-w-md">
        Esta sección se habilitará en la próxima fase del proyecto. Actualmente, los clientes se registran automáticamente vía WhatsApp o al crear pedidos manuales.
      </p>
    </div>
  );
}
