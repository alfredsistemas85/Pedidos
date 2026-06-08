import { Settings as SettingsIcon } from 'lucide-react';

export default function Settings() {
  return (
    <div className="h-[80vh] flex flex-col items-center justify-center text-center">
      <div className="bg-gray-100 dark:bg-dark-border p-4 rounded-full mb-4">
        <SettingsIcon className="w-12 h-12 text-gray-500 dark:text-gray-400" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Configuración del Sistema
      </h2>
      <p className="text-gray-500 dark:text-gray-400 max-w-md">
        Las configuraciones del sistema (horarios, zonas de entrega y ajustes avanzados) estarán disponibles próximamente.
      </p>
    </div>
  );
}
