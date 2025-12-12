import { ShieldCheck, Calendar } from "lucide-react";

export function WelcomeSection() {
  return (
    <div className="pt-12 pb-8">
      <h2 className="font-['Karma'] font-bold text-[32px] text-slate-800 mb-4">
        ¡Hola, Nombre Usuario!
      </h2>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="bg-[#ffe2e2] rounded-lg px-4 py-1.5 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-800" />
            <span className="font-['Segoe_UI'] text-slate-800">Administrador</span>
          </div>
          <span className="font-['Segoe_UI'] text-[#5d7192]">usuario@email.com</span>
        </div>
        
        <div className="flex items-center gap-2 text-[#5d7192]">
          <Calendar className="w-4 h-4" />
          <span className="font-['Segoe_UI']">domingo, 21 de septiembre de 2025</span>
        </div>
      </div>
    </div>
  );
}
