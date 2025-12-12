import { Activity, Clock } from "lucide-react";

export function ActivitySection() {
  const activities = [
    {
      title: "Dispositivo registrado",
      device: "Laptop Dell #LP001",
      time: "Hace 2 minutos",
    },
    {
      title: "Dispositivo registrado",
      device: "Laptop Dell #LP001",
      time: "Hace 2 minutos",
    },
    {
      title: "Dispositivo registrado",
      device: "Laptop Dell #LP001",
      time: "Hace 2 minutos",
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-[0px_4px_15px_0px_rgba(0,0,0,0.12)] p-6">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-6 h-6 text-blue-600" />
        <h3 className="font-['Segoe_UI'] font-semibold text-slate-800">
          Actividad Reciente
        </h3>
      </div>

      <div className="space-y-3 mb-6">
        {activities.map((activity, index) => (
          <div key={index} className="bg-slate-100 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-600 mt-2 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="font-['Segoe_UI'] font-semibold text-slate-800 mb-1">
                  {activity.title}
                </h4>
                <p className="font-['Segoe_UI'] text-slate-800 mb-2">
                  {activity.device}
                </p>
                <div className="flex items-center gap-1.5 text-[#5d7192]">
                  <Clock className="w-3 h-3" />
                  <span className="font-['Segoe_UI'] text-xs">{activity.time}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button className="w-full border-[1.5px] border-blue-600 rounded-lg py-2.5 text-blue-600 font-['Segoe_UI'] font-semibold hover:bg-blue-50 transition-colors">
        Ver Todos los Registros
      </button>
    </div>
  );
}
