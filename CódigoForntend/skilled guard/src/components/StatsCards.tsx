import { Monitor, Users, TrendingUp } from "lucide-react";

export function StatsCards() {
  return (
    <div className="grid grid-cols-3 gap-8 mb-12">
      <div className="bg-white rounded-xl shadow-[0px_4px_15px_0px_rgba(0,0,0,0.12)] p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-['Segoe_UI'] text-slate-800 mb-2">Total Dispositivos</p>
            <p className="font-['Karma'] font-bold text-[32px] text-black">1247</p>
          </div>
          <div className="bg-[#e4ebf3] rounded-2xl w-[46px] h-[46px] flex items-center justify-center">
            <Monitor className="w-8 h-8 text-blue-600" strokeWidth={2} />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-[0px_4px_15px_0px_rgba(0,0,0,0.12)] p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-['Segoe_UI'] text-slate-800 mb-2">Usuarios Activos</p>
            <p className="font-['Karma'] font-bold text-[32px] text-black">1247</p>
          </div>
          <div className="bg-[#e4ebf3] rounded-2xl w-[46px] h-[46px] flex items-center justify-center">
            <Users className="w-8 h-8 text-blue-600" strokeWidth={2} />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-[0px_4px_15px_0px_rgba(0,0,0,0.12)] p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-['Segoe_UI'] text-slate-800 mb-2">Accesos Hoy</p>
            <p className="font-['Karma'] font-bold text-[32px] text-black">1247</p>
          </div>
          <div className="bg-[#e4ebf3] rounded-2xl w-[46px] h-[46px] flex items-center justify-center">
            <TrendingUp className="w-8 h-8 text-blue-600" strokeWidth={2} />
          </div>
        </div>
      </div>
    </div>
  );
}
