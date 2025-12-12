import { FileText, UserPlus, QrCode, BarChart3 } from "lucide-react";

export function ActionsSection() {
  const actions = [
    {
      title: "Registrar Dispositivo",
      description: "Agregar nuevos equipos al sistema",
      icon: FileText,
    },
    {
      title: "Registrar Usuario",
      description: "Crear nuevos usuarios y asignar roles",
      icon: UserPlus,
    },
    {
      title: "Verificar por QR",
      description: "Escanear códigos QR para acceso",
      icon: QrCode,
    },
    {
      title: "Reportes Completos",
      description: "Ver todos los reportes y estadísticas",
      icon: BarChart3,
    },
  ];

  return (
    <div className="mb-12">
      <h3 className="font-['Karma'] font-bold text-[24px] text-slate-800 mb-2">
        Acciones Disponibles
      </h3>
      <p className="font-['Segoe_UI'] text-black mb-6">
        Funciones habilitadas para tu rol de administrador
      </p>

      <div className="grid grid-cols-2 gap-6">
        {actions.map((action, index) => (
          <button
            key={index}
            className="bg-white rounded-xl shadow-[0px_4px_15px_0px_rgba(0,0,0,0.12)] p-6 text-left hover:shadow-xl transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className="bg-[#e4ebf3] rounded-2xl w-[46px] h-[46px] flex items-center justify-center flex-shrink-0">
                <action.icon className="w-8 h-8 text-blue-600" strokeWidth={1.75} />
              </div>
              <div>
                <h4 className="font-['Segoe_UI'] font-semibold text-slate-800 mb-1">
                  {action.title}
                </h4>
                <p className="font-['Segoe_UI'] text-slate-800">
                  {action.description}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
