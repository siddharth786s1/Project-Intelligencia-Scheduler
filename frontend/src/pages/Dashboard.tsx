import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  School as SchoolIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  MeetingRoom as ClassroomIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
  Assessment as AssessmentIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useDataService } from '../services/dataService';
import { useNavigate } from 'react-router-dom';
import type { Timetable } from '../types/timetable';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const dataService = useDataService();
  const [loading, setLoading] = useState(true);
  const [recentTimetables, setRecentTimetables] = useState<Timetable[]>([]);
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
          timetablesRes
        ] = await Promise.all([
          dataService.getInstitutions(0, 1),
          dataService.getDepartments(0, 1),
          dataService.getFaculty(0, 1),
          dataService.getSubjects(0, 1),
          dataService.getBatches(0, 1),
          dataService.getClassrooms(0, 1),
          dataService.getTimeSlots(0, 1),
          dataService.getTimetables(0, 5)
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
        
        setRecentTimetables(timetablesRes.data);
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
        
        // Mock timetables for demo purposes
        setRecentTimetables([
          {
            id: 'tt1',
            name: 'Fall 2023 CSE Department',
            description: 'Complete timetable for CSE department',
            institution_id: 'inst1',
            department_id: 'dept1',
            generated_at: '2023-08-15T10:30:00',
            status: 'published',
            generation_algorithm: 'Genetic Algorithm',
            sessions: []
          },
          {
            id: 'tt2',
            name: 'Spring 2024 ECE Department',
            description: 'Draft timetable for ECE department',
            institution_id: 'inst1',
            department_id: 'dept2',
            generated_at: '2023-11-05T14:45:00',
            status: 'draft',
            generation_algorithm: 'Constraint Solver',
            sessions: []
          },
          {
            id: 'tt3',
            name: 'Fall 2023 MBA Program',
            description: 'Approved timetable for MBA program',
            institution_id: 'inst1',
            department_id: 'dept3',
            generated_at: '2023-09-20T09:15:00',
            status: 'approved',
            generation_algorithm: 'Simulated Annealing',
            sessions: []
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [dataService]);
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'approved':
        return 'primary';
      case 'draft':
        return 'default';
      default:
        return 'default';
    }
  };

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
      <Grid container spacing={3} sx={{ mb: 4, mt: 2 }}>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{stats.departments}</Typography>
            <Typography variant="body1">Departments</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{stats.faculty}</Typography>
            <Typography variant="body1">Faculty</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{stats.subjects}</Typography>
            <Typography variant="body1">Subjects</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{stats.batches}</Typography>
            <Typography variant="body1">Batches</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{stats.classrooms}</Typography>
            <Typography variant="body1">Classrooms</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4} md={2}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5">{scheduleGenerations.length}</Typography>
            <Typography variant="body1">Schedules</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Queue Status */}
      {queueStatus && (
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h6" gutterBottom>Job Queue Status</Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="body2">Active Jobs: {queueStatus.active_jobs}</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2">Queue Size: {queueStatus.queue_size}</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2">Running Workers: {queueStatus.running_workers}/{queueStatus.max_workers}</Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

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
          <Grid container spacing={2}>
            {scheduleGenerations.map((generation) => (
              <Grid item xs={12} key={generation.id}>
                <Paper elevation={1} sx={{ p: 2 }}>
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
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
    </Container>
  );
};

export default Dashboard;
