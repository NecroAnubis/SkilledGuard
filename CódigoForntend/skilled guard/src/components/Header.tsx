import { Monitor, Users, QrCode, FileText, ChevronDown, User } from "lucide-react";

export function Header() {
  return (
    <header className="bg-[#1E293B] h-16 w-full sticky top-0 z-50">
      <div className="max-w-[1440px] mx-auto px-[84px] h-full flex items-center justify-between">
        <h1 className="text-white font-['Karma'] font-bold text-[32px]">
          Skilled Guard
        </h1>
        
        <nav className="flex items-center gap-6">
          <button className="bg-slate-800 rounded-xl px-4 py-2 flex items-center gap-2 text-white hover:bg-slate-700 transition-colors">
            <Monitor className="w-5 h-5" />
            <span className="font-['Segoe_UI'] font-semibold">Dispositivos</span>
          </button>
          
          <button className="bg-slate-800 rounded-xl px-4 py-2 flex items-center gap-2 text-white hover:bg-slate-700 transition-colors">
            <Users className="w-5 h-5" />
            <span className="font-['Segoe_UI'] font-semibold">Usuarios</span>
          </button>
          
          <button className="bg-slate-800 rounded-xl px-4 py-2 flex items-center gap-2 text-white hover:bg-slate-700 transition-colors">
            <QrCode className="w-5 h-5" />
            <span className="font-['Segoe_UI'] font-semibold">Registros</span>
          </button>
          
          <button className="bg-slate-800 rounded-xl px-4 py-2 flex items-center gap-2 text-white hover:bg-slate-700 transition-colors">
            <FileText className="w-5 h-5" />
            <span className="font-['Segoe_UI'] font-semibold">Reportes</span>
          </button>
        </nav>

        <button className="bg-slate-800 h-14 px-4 flex items-center gap-3 text-white hover:bg-slate-700 transition-colors">
          <div className="bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center">
            <User className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-['Segoe_UI'] font-semibold">Nombre Usuario</div>
            <div className="font-['Segoe_UI'] text-xs">Administrador</div>
          </div>
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
