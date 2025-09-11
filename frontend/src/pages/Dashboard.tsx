import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useDataService } from '../services/dataService';
import SchedulerService from '../services/schedulerService';
import SchedulerMonitor from '../components/SchedulerMonitor';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const dataService = useDataService();
  const [loading, setLoading] = useState(true);
  const [scheduleGenerations, setScheduleGenerations] = useState<any[]>([]);
  const [stats, setStats] = useState({
    institutions: 0,
    departments: 0,
    faculty: 0,
    subjects: 0,
    batches: 0,
    classrooms: 0,
    timeSlots: 0,
    timetables: 0
  });
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // In a real app, we'd make a dedicated dashboard API endpoint
        // For now, we'll make multiple requests
        
        const [
          institutionsRes,
          departmentsRes,
          facultyRes,
          subjectsRes,
          batchesRes,
          classroomsRes,
          timeSlotsRes,
          timetablesRes,
          schedulerGenerationsRes
        ] = await Promise.all([
          dataService.getInstitutions(0, 1),
          dataService.getDepartments(0, 1),
          dataService.getFaculty(0, 1),
          dataService.getSubjects(0, 1),
          dataService.getBatches(0, 1),
          dataService.getClassrooms(0, 1),
          dataService.getTimeSlots(0, 1),
          dataService.getTimetables(0, 5),
          SchedulerService.listScheduleGenerations(0, 5)
        ]);
        
        setStats({
          institutions: institutionsRes.total,
          departments: departmentsRes.total,
          faculty: facultyRes.total,
          subjects: subjectsRes.total,
          batches: batchesRes.total,
          classrooms: classroomsRes.total,
          timeSlots: timeSlotsRes.total,
          timetables: timetablesRes.total
        });
        
        setScheduleGenerations(schedulerGenerationsRes.items || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        
        // For demo purposes, set mock data if API fails
        setStats({
          institutions: 3,
          departments: 8,
          faculty: 45,
          subjects: 72,
          batches: 15,
          classrooms: 22,
          timeSlots: 9,
          timetables: 6
        });
        
        // Mock schedule generations for demo purposes
        setScheduleGenerations([
          {
            id: 'gen1',
            name: 'Fall 2023 CSE Department',
            description: 'Complete timetable for CSE department',
            created_at: '2023-08-15T10:30:00',
            status: 'completed',
            algorithm: 'Genetic Algorithm',
            session_count: 24,
            hard_constraint_violations: 0,
            soft_constraint_violations: 2
          },
          {
            id: 'gen2',
            name: 'Spring 2024 ECE Department',
            description: 'Draft timetable for ECE department',
            created_at: '2023-11-05T14:45:00',
            status: 'processing',
            algorithm: 'Constraint Solver',
            session_count: 18,
            hard_constraint_violations: 0,
            soft_constraint_violations: 5
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [dataService]);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        Welcome, {user?.first_name} {user?.last_name}!
      </Typography>

      {/* Stats Overview */}
      <Box sx={{ mb: 4, mt: 2, display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 3 }}>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{stats.departments}</Typography>
          <Typography variant="body1">Departments</Typography>
        </Paper>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{stats.faculty}</Typography>
          <Typography variant="body1">Faculty</Typography>
        </Paper>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{stats.subjects}</Typography>
          <Typography variant="body1">Subjects</Typography>
        </Paper>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{stats.batches}</Typography>
          <Typography variant="body1">Batches</Typography>
        </Paper>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{stats.classrooms}</Typography>
          <Typography variant="body1">Classrooms</Typography>
        </Paper>
        <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="h5">{scheduleGenerations.length}</Typography>
          <Typography variant="body1">Schedules</Typography>
        </Paper>
      </Box>

      {/* Scheduler Monitor */}
      <SchedulerMonitor onRefresh={() => {
        // Refresh schedule generations if needed
        const fetchData = async () => {
          try {
            const response = await SchedulerService.listScheduleGenerations(0, 5);
            setScheduleGenerations(response.items || []);
          } catch (error) {
            console.error("Failed to refresh schedule generations:", error);
          }
        };
        fetchData();
      }} />

      {/* Recent Schedule Generations */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Recent Schedule Generations</Typography>
          <Button variant="contained" color="primary" onClick={() => navigate('/scheduler/new')}>
            Create New Schedule
          </Button>
        </Box>
        
        {scheduleGenerations.length === 0 ? (
          <Typography variant="body1">No schedules generated yet.</Typography>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {scheduleGenerations.map((generation) => (
              <Paper elevation={1} sx={{ p: 2 }} key={generation.id}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="subtitle1">{generation.name}</Typography>
                  <Typography variant="body2">{new Date(generation.created_at).toLocaleDateString()}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {generation.description}
                </Typography>
                <Typography variant="body2">
                  Sessions: {generation.session_count} | 
                  Hard Constraints: {generation.hard_constraint_violations} | 
                  Soft Constraints: {generation.soft_constraint_violations}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Button size="small" onClick={() => navigate(`/scheduler/view/${generation.id}`)}>
                    View Schedule
                  </Button>
                </Box>
              </Paper>
            ))}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Dashboard;
