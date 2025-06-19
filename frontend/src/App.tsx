import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider } from "./context/AppContext";
import { UserProvider } from "./context/UserContext";
import LandingPage from "./pages/LandingPage";
import AdminPage from "./pages/AdminPage";
import EvaluatePage from "./pages/EvaluatePage";
import DashboardPage from "./pages/DashboardPage";
import CandidateDetailPage from "./pages/CandidateDetailPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <UserProvider>
          <AppProvider>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/admin" element={<AdminPage />} />
              <Route path="/evaluate" element={<EvaluatePage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/candidate/:email" element={<CandidateDetailPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AppProvider>
        </UserProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
