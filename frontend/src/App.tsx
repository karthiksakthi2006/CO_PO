import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CourseOutcomesPage } from './pages/CourseOutcomesPage';
import { CoPoMappingPage } from './pages/CoPoMappingPage';
import { AssessmentsPage } from './pages/AssessmentsPage';
import { MarksImportPage } from './pages/MarksImportPage';
import { AttainmentCalculationPage } from './pages/AttainmentCalculationPage';
import { GapAnalysisPage } from './pages/GapAnalysisPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { InterventionsPage } from './pages/InterventionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { SemesterTrendsPage } from './pages/SemesterTrendsPage';
import { StudentDirectoryPage } from './pages/StudentDirectoryPage';
import { CoursesPage } from './pages/CoursesPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { InstitutionsPage } from './pages/InstitutionsPage';
import { CalendarPage } from './pages/CalendarPage';
import { UsersPage } from './pages/UsersPage';
import { StudentDetailPage } from './pages/StudentDetailPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { ProfileSettingsPage } from './pages/ProfileSettingsPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#070b14] flex items-center justify-center text-slate-400 text-sm">
        Verifying session credentials...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="semester-trends" element={<SemesterTrendsPage />} />
            <Route path="outcomes/cos" element={<CourseOutcomesPage />} />
            <Route path="outcomes/mapping" element={<CoPoMappingPage />} />
            <Route path="courses" element={<CoursesPage />} />
            <Route path="assessments" element={<AssessmentsPage />} />
            <Route path="marks/import" element={<MarksImportPage />} />
            <Route path="attainment" element={<AttainmentCalculationPage />} />
            <Route path="gaps" element={<GapAnalysisPage />} />
            <Route path="recommendations" element={<RecommendationsPage />} />
            <Route path="interventions" element={<InterventionsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="students" element={<StudentDirectoryPage />} />
            <Route path="students/:id" element={<StudentDetailPage />} />
            <Route path="my-performance" element={<StudentDetailPage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="institutions" element={<InstitutionsPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="audit" element={<AuditLogPage />} />
            <Route path="profile" element={<ProfileSettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
