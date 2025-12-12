import { Header } from "./components/Header";
import { WelcomeSection } from "./components/WelcomeSection";
import { StatsCards } from "./components/StatsCards";
import { ActionsSection } from "./components/ActionsSection";
import { ActivitySection } from "./components/ActivitySection";
import { Footer } from "./components/Footer";

export default function App() {
  return (
    <div className="bg-gradient-to-b from-[#f5f8fe] min-h-screen relative to-[#e4ebf3]">
      <Header />
      <main className="max-w-[1440px] mx-auto px-[155px] pb-12">
        <WelcomeSection />
        <StatsCards />
        <ActionsSection />
        <ActivitySection />
      </main>
      <Footer />
    </div>
  );
}
