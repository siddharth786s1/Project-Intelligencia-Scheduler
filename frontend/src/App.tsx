import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { DataServiceProvider } from './contexts/DataServiceContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import './App.css';

// Additional pages we need to implement
import Institutions from './pages/Institutions';
import Departments from './pages/Departments';
import Faculty from './pages/Faculty';
import Subjects from './pages/Subjects';
import Batches from './pages/Batches';
import Classrooms from './pages/Classrooms';
import TimeSlots from './pages/TimeSlots';
import Constraints from './pages/Constraints';
import TimetableGenerator from './pages/TimetableGenerator';
import TimetableViewer from './pages/TimetableViewer';

function App() {
  return (
    <Router>
      <AuthProvider>
        <DataServiceProvider>
          <Layout>
            <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/institutions" element={
              <ProtectedRoute>
                <Institutions />
              </ProtectedRoute>
            } />
            <Route path="/departments" element={
              <ProtectedRoute>
                <Departments />
              </ProtectedRoute>
            } />
            <Route path="/faculty" element={
              <ProtectedRoute>
                <Faculty />
              </ProtectedRoute>
            } />
            <Route path="/subjects" element={
              <ProtectedRoute>
                <Subjects />
              </ProtectedRoute>
            } />
            <Route path="/batches" element={
              <ProtectedRoute>
                <Batches />
              </ProtectedRoute>
            } />
            <Route path="/classrooms" element={
              <ProtectedRoute>
                <Classrooms />
              </ProtectedRoute>
            } />
            <Route path="/time-slots" element={
              <ProtectedRoute>
                <TimeSlots />
              </ProtectedRoute>
            } />
            <Route path="/constraints" element={
              <ProtectedRoute>
                <Constraints />
              </ProtectedRoute>
            } />
            <Route path="/timetable-generator" element={
              <ProtectedRoute>
                <TimetableGenerator />
              </ProtectedRoute>
            } />
            <Route path="/timetable-viewer" element={
              <ProtectedRoute>
                <TimetableViewer />
              </ProtectedRoute>
            } />
            
            {/* Redirect to login for root */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Not found - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          </Layout>
        </DataServiceProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
