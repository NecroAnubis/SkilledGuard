import { Mail, Phone, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[#1E293B] w-full mt-auto">
      <div className="max-w-[1440px] mx-auto px-[155px] py-6">
        <div className="flex justify-between">
          <div className="flex-1">
            <h2 className="font-['Karma'] font-bold text-[24px] text-white mb-4">
              Skilled Guard
            </h2>
            <p className="font-['Segoe_UI'] text-white mb-8 max-w-[774px]">
              Sistema de registro y control de equipos de cómputo para el SENA. Solución tecnológica para la gestión segura y eficiente de dispositivos personales e institucionales.
            </p>
            <p className="font-['Segoe_UI'] text-white">
              <span>© 2025 </span>
              <span className="font-semibold">Skilled Guard</span>
              <span>. Todos los derechos reservados.</span>
            </p>
          </div>

          <div className="border-l border-blue-600 mx-8" />

          <div>
            <h3 className="font-['Segoe_UI'] font-bold text-[24px] text-white mb-4">
              Soporte
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-white">
                <Mail className="w-6 h-6" />
                <span className="font-['Segoe_UI']">soporte@skilledguard.com.co</span>
              </div>
              <div className="flex items-center gap-3 text-white">
                <Phone className="w-6 h-6" />
                <span className="font-['Segoe_UI']">+57 (1) 800 0000</span>
              </div>
              <div className="flex items-center gap-3 text-white">
                <MapPin className="w-6 h-6" />
                <span className="font-['Segoe_UI']">Bogotá D.C., Colombia</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
