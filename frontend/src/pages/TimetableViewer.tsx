import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Box,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Chip,
  CircularProgress,
  Button,
  IconButton,
  Tooltip,
  Divider,
  TextField,
  InputAdornment
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import SearchIcon from '@mui/icons-material/Search';
import PrintIcon from '@mui/icons-material/Print';
import ShareIcon from '@mui/icons-material/Share';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import { useDataService } from '../services/dataService';
import { useSearchParams } from 'react-router-dom';

import type { Timetable } from '../types/timetable';
import type { ScheduledSession } from '../types/scheduledSession';

const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const TimetableViewer = () => {
  const [searchParams] = useSearchParams();
  const timetableId = searchParams.get('id');
  const dataService = useDataService();
  
  const [selectedView, setSelectedView] = useState<'batch' | 'faculty' | 'classroom'>('batch');
  const [selectedBatch, setSelectedBatch] = useState<string>('');
  const [selectedFaculty, setSelectedFaculty] = useState<string>('');
  const [selectedClassroom, setSelectedClassroom] = useState<string>('');
  const [selectedDay, setSelectedDay] = useState<number | 'all'>('all');
  const [loading, setLoading] = useState(true);
  const [timetableData, setTimetableData] = useState<Timetable | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Mock data
  const mockBatches = [
    { id: 'batch1', name: 'CSE 2023 A' },
    { id: 'batch2', name: 'CSE 2023 B' },
    { id: 'batch3', name: 'ECE 2023 A' }
  ];
  
  const mockFaculty = [
    { id: 'faculty1', name: 'Dr. John Smith' },
    { id: 'faculty2', name: 'Prof. Sarah Johnson' },
    { id: 'faculty3', name: 'Dr. Michael Lee' }
  ];
  
  const mockClassrooms = [
    { id: 'classroom1', name: 'LH-101' },
    { id: 'classroom2', name: 'CS Lab-1' },
    { id: 'classroom3', name: 'Seminar Hall-2' }
  ];
  
  const mockSessions: ScheduledSession[] = [
    {
      id: 'session1',
      subject_id: 'subj1',
      subject_name: 'Data Structures',
      subject_code: 'CS201',
      faculty_id: 'faculty1',
      faculty_name: 'Dr. John Smith',
      batch_id: 'batch1',
      batch_name: 'CSE 2023 A',
      classroom_id: 'classroom1',
      classroom_name: 'LH-101',
      day_of_week: 1, // Monday
      start_time: '09:00:00',
      end_time: '10:00:00',
      session_type: 'lecture'
    },
    {
      id: 'session2',
      subject_id: 'subj2',
      subject_name: 'Database Systems',
      subject_code: 'CS202',
      faculty_id: 'faculty2',
      faculty_name: 'Prof. Sarah Johnson',
      batch_id: 'batch1',
      batch_name: 'CSE 2023 A',
      classroom_id: 'classroom1',
      classroom_name: 'LH-101',
      day_of_week: 1, // Monday
      start_time: '10:00:00',
      end_time: '11:00:00',
      session_type: 'lecture'
    },
    {
      id: 'session3',
      subject_id: 'subj3',
      subject_name: 'Computer Networks',
      subject_code: 'CS203',
      faculty_id: 'faculty3',
      faculty_name: 'Dr. Michael Lee',
      batch_id: 'batch1',
      batch_name: 'CSE 2023 A',
      classroom_id: 'classroom1',
      classroom_name: 'LH-101',
      day_of_week: 2, // Tuesday
      start_time: '09:00:00',
      end_time: '10:00:00',
      session_type: 'lecture'
    },
    {
      id: 'session4',
      subject_id: 'subj1',
      subject_name: 'Data Structures',
      subject_code: 'CS201',
      faculty_id: 'faculty1',
      faculty_name: 'Dr. John Smith',
      batch_id: 'batch2',
      batch_name: 'CSE 2023 B',
      classroom_id: 'classroom1',
      classroom_name: 'LH-101',
      day_of_week: 2, // Tuesday
      start_time: '10:00:00',
      end_time: '11:00:00',
      session_type: 'lecture'
    },
    {
      id: 'session5',
      subject_id: 'subj1L',
      subject_name: 'Data Structures Lab',
      subject_code: 'CS201L',
      faculty_id: 'faculty1',
      faculty_name: 'Dr. John Smith',
      batch_id: 'batch1',
      batch_name: 'CSE 2023 A',
      classroom_id: 'classroom2',
      classroom_name: 'CS Lab-1',
      day_of_week: 3, // Wednesday
      start_time: '14:00:00',
      end_time: '16:00:00',
      session_type: 'practical'
    }
  ];
  
  // Fetch timetable data
  const fetchTimetableData = async () => {
    setLoading(true);
    try {
      if (timetableId) {
        // If we have a timetable ID, fetch real data from the API
        const { data } = await dataService.getTimetable(timetableId);
        setTimetableData(data);
      } else {
        // For demo purposes when no ID is provided, use mock data
        const mockTimetable: Timetable = {
          id: 'tt-default',
          name: 'Fall Semester 2023 Timetable',
          institution_id: 'inst1',
          department_id: 'dept1',
          generated_at: '2023-07-15T14:30:00',
          status: 'draft',
          generation_algorithm: 'Genetic Algorithm',
          sessions: mockSessions
        };
        
        setTimetableData(mockTimetable);
      }
      
      setSelectedBatch(mockBatches[0].id);
      setSelectedFaculty(mockFaculty[0].id);
      setSelectedClassroom(mockClassrooms[0].id);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching timetable data:', err);
      setError('Failed to load timetable data. Please try again.');
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchTimetableData();
  }, [timetableId]);
  
  const handleViewChange = (_: React.SyntheticEvent, newValue: 'batch' | 'faculty' | 'classroom') => {
    setSelectedView(newValue);
  };
  
  const handleBatchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedBatch(event.target.value);
  };
  
  const handleFacultyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFaculty(event.target.value);
  };
  
  const handleClassroomChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedClassroom(event.target.value);
  };
  
  const handleDayChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDay(event.target.value as unknown as number | 'all');
  };
  
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };
  
  const formatTime = (timeString: string) => {
    try {
      const [hours, minutes] = timeString.split(':');
      const hour = parseInt(hours, 10);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour % 12 || 12;
      return `${hour12}:${minutes} ${ampm}`;
    } catch (e) {
      return timeString;
    }
  };
  
  const getSessionChipColor = (sessionType: string) => {
    switch (sessionType) {
      case 'lecture':
        return 'primary';
      case 'tutorial':
        return 'secondary';
      case 'practical':
        return 'success';
      default:
        return 'default';
    }
  };
  
  // Filter sessions based on selected view and filters
  const getFilteredSessions = () => {
    if (!timetableData) return [];
    
    let filtered = [...timetableData.sessions];
    
    // Filter by view type
    if (selectedView === 'batch' && selectedBatch) {
      filtered = filtered.filter(session => {
        const matchesBatch = session.batch_name === mockBatches.find(b => b.id === selectedBatch)?.name;
        return matchesBatch;
      });
    } else if (selectedView === 'faculty' && selectedFaculty) {
      filtered = filtered.filter(session => {
        const matchesFaculty = session.faculty_name === mockFaculty.find(f => f.id === selectedFaculty)?.name;
        return matchesFaculty;
      });
    } else if (selectedView === 'classroom' && selectedClassroom) {
      filtered = filtered.filter(session => {
        const matchesClassroom = session.classroom_name === mockClassrooms.find(c => c.id === selectedClassroom)?.name;
        return matchesClassroom;
      });
    }
    
    // Filter by day
    if (selectedDay !== 'all') {
      filtered = filtered.filter(session => session.day_of_week === selectedDay);
    }
    
    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(session => 
        session.subject_name.toLowerCase().includes(term) ||
        session.subject_code.toLowerCase().includes(term) ||
        session.faculty_name.toLowerCase().includes(term) ||
        session.batch_name.toLowerCase().includes(term) ||
        session.classroom_name.toLowerCase().includes(term)
      );
    }
    
    return filtered;
  };
  
  // Organize sessions by day and time for timetable view
  const getOrganizedSessions = () => {
    const filteredSessions = getFilteredSessions();
    const organized: Record<string, Record<string, ScheduledSession>> = {};
    
    // Initialize days
    daysOfWeek.forEach(day => {
      organized[day] = {};
    });
    
    // Populate sessions
    filteredSessions.forEach(session => {
      const day = daysOfWeek[session.day_of_week];
      const timeSlot = `${formatTime(session.start_time)} - ${formatTime(session.end_time)}`;
      
      if (!organized[day]) {
        organized[day] = {};
      }
      
      organized[day][timeSlot] = session;
    });
    
    return organized;
  };
  
  // Get all unique time slots from the filtered sessions
  const getUniqueTimeSlots = () => {
    const filteredSessions = getFilteredSessions();
    const timeSlots = new Set<string>();
    
    filteredSessions.forEach(session => {
      const timeSlot = `${formatTime(session.start_time)} - ${formatTime(session.end_time)}`;
      timeSlots.add(timeSlot);
    });
    
    return Array.from(timeSlots).sort();
  };
  
  const organizedSessions = getOrganizedSessions();
  const uniqueTimeSlots = getUniqueTimeSlots();
  const filteredDays = selectedDay === 'all' ? daysOfWeek : [daysOfWeek[selectedDay as number]];
  
  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Container>
    );
  }
  
  return (
    <Container sx={{ mb: 4 }}>
      <Box sx={{ mb: 3, mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Timetable Viewer
          </Typography>
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<FileDownloadIcon />}
              sx={{ mr: 1 }}
            >
              Export
            </Button>
            <Button 
              variant="outlined"
              startIcon={<PrintIcon />}
              sx={{ mr: 1 }}
            >
              Print
            </Button>
            <Button 
              variant="outlined"
              startIcon={<ShareIcon />}
              sx={{ mr: 1 }}
            >
              Share
            </Button>
            <Button 
              variant="contained"
              color="primary"
              startIcon={<AssignmentTurnedInIcon />}
            >
              {timetableData?.status === 'draft' ? 'Approve' : 'Publish'} Timetable
            </Button>
          </Box>
        </Box>
        
        {timetableData && (
          <Card variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' } }}>
                <Box sx={{ flex: 2 }}>
                  <Typography variant="h5" gutterBottom>{timetableData.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Generated on: {new Date(timetableData.generated_at).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Algorithm: {timetableData.generation_algorithm}
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                  <Chip 
                    label={timetableData.status.toUpperCase()}
                    color={
                      timetableData.status === 'published' ? 'success' : 
                      timetableData.status === 'approved' ? 'primary' : 
                      'default'
                    }
                    sx={{ fontWeight: 'bold' }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
      
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={selectedView}
            onChange={handleViewChange}
            aria-label="timetable view tabs"
            variant="fullWidth"
          >
            <Tab label="Batch View" value="batch" />
            <Tab label="Faculty View" value="faculty" />
            <Tab label="Classroom View" value="classroom" />
          </Tabs>
        </Box>
        
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ flex: '1 1 300px' }}>
              {selectedView === 'batch' && (
                <FormControl fullWidth>
                  <InputLabel id="batch-select-label">Batch</InputLabel>
                  <Select
                    labelId="batch-select-label"
                    id="batch-select"
                    value={selectedBatch}
                    onChange={handleBatchChange}
                    label="Batch"
                  >
                    {mockBatches.map((batch) => (
                      <MenuItem key={batch.id} value={batch.id}>
                        {batch.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
              
              {selectedView === 'faculty' && (
                <FormControl fullWidth>
                  <InputLabel id="faculty-select-label">Faculty</InputLabel>
                  <Select
                    labelId="faculty-select-label"
                    id="faculty-select"
                    value={selectedFaculty}
                    onChange={handleFacultyChange}
                    label="Faculty"
                  >
                    {mockFaculty.map((faculty) => (
                      <MenuItem key={faculty.id} value={faculty.id}>
                        {faculty.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
              
              {selectedView === 'classroom' && (
                <FormControl fullWidth>
                  <InputLabel id="classroom-select-label">Classroom</InputLabel>
                  <Select
                    labelId="classroom-select-label"
                    id="classroom-select"
                    value={selectedClassroom}
                    onChange={handleClassroomChange}
                    label="Classroom"
                  >
                    {mockClassrooms.map((classroom) => (
                      <MenuItem key={classroom.id} value={classroom.id}>
                        {classroom.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            </Box>
            
            <Box sx={{ flex: '1 1 300px' }}>
              <FormControl fullWidth>
                <InputLabel id="day-select-label">Day</InputLabel>
                <Select
                  labelId="day-select-label"
                  id="day-select"
                  value={selectedDay}
                  onChange={handleDayChange}
                  label="Day"
                >
                  <MenuItem value="all">All Days</MenuItem>
                  {daysOfWeek.map((day, index) => (
                    <MenuItem key={index} value={index}>
                      {day}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            
            <Box sx={{ flex: '2 1 400px' }}>
              <TextField
                fullWidth
                placeholder="Search subjects, faculty, batches..."
                value={searchTerm}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          </Box>
        </Box>
      </Paper>
      
      {error && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>{error}</Typography>
        </Paper>
      )}
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width="12%">Time</TableCell>
              {filteredDays.map((day) => (
                <TableCell key={day} align="center">{day}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {uniqueTimeSlots.length > 0 ? (
              uniqueTimeSlots.map((timeSlot) => (
                <TableRow key={timeSlot}>
                  <TableCell>{timeSlot}</TableCell>
                  {filteredDays.map((day) => {
                    const session = organizedSessions[day]?.[timeSlot];
                    return (
                      <TableCell key={day} align="center">
                        {session ? (
                          <Card variant="outlined" sx={{ p: 1, backgroundColor: 'background.default' }}>
                            <Typography variant="subtitle2">
                              {session.subject_name}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                {session.subject_code}
                              </Typography>
                              <Chip
                                label={session.session_type}
                                size="small"
                                color={getSessionChipColor(session.session_type)}
                              />
                            </Box>
                            <Divider sx={{ my: 1 }} />
                            <Typography variant="body2">
                              {selectedView !== 'faculty' && session.faculty_name}
                              {selectedView !== 'batch' && selectedView !== 'faculty' && <br />}
                              {selectedView !== 'batch' && session.batch_name}
                              {selectedView !== 'classroom' && selectedView !== 'batch' && <br />}
                              {selectedView !== 'classroom' && session.classroom_name}
                            </Typography>
                          </Card>
                        ) : null}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={filteredDays.length + 1} align="center">
                  No scheduled sessions found matching your filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default TimetableViewer;
