import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Button, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  CircularProgress,
  IconButton,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useDataService } from '../services/dataService';
import { TimePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

interface TimeSlot {
  id: string;
  name: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  institution_id: string;
  created_at: string;
  updated_at: string;
}

interface Institution {
  id: string;
  name: string;
}

interface TimeSlotFormData {
  name: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  institution_id: string;
}

const daysOfWeek = [
  { value: 0, label: 'Sunday' },
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' }
];

const TimeSlots = () => {
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<TimeSlotFormData>({
    name: '',
    day_of_week: 1, // Default to Monday
    start_time: '09:00:00',
    end_time: '10:00:00',
    institution_id: '',
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<dayjs.Dayjs | null>(null);
  const [endTime, setEndTime] = useState<dayjs.Dayjs | null>(null);
  
  const dataService = useDataService();
  
  const fetchTimeSlots = async () => {
    setLoading(true);
    try {
      const response = await dataService.getTimeSlots();
      setTimeSlots(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching time slots:', err);
      setError('Failed to load time slots. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchInstitutions = async () => {
    try {
      const response = await dataService.getInstitutions();
      setInstitutions(response.data);
    } catch (err) {
      console.error('Error fetching institutions:', err);
      setError('Failed to load institutions.');
    }
  };
  
  useEffect(() => {
    Promise.all([fetchTimeSlots(), fetchInstitutions()]);
  }, []);
  
  const handleOpenDialog = (timeSlot?: TimeSlot) => {
    if (timeSlot) {
      setFormData({
        name: timeSlot.name,
        day_of_week: timeSlot.day_of_week,
        start_time: timeSlot.start_time,
        end_time: timeSlot.end_time,
        institution_id: timeSlot.institution_id,
      });
      setStartTime(dayjs(`2023-01-01T${timeSlot.start_time}`));
      setEndTime(dayjs(`2023-01-01T${timeSlot.end_time}`));
      setCurrentId(timeSlot.id);
    } else {
      setFormData({
        name: '',
        day_of_week: 1,
        start_time: '09:00:00',
        end_time: '10:00:00',
        institution_id: institutions.length > 0 ? institutions[0].id : '',
      });
      setStartTime(dayjs('2023-01-01T09:00:00'));
      setEndTime(dayjs('2023-01-01T10:00:00'));
      setCurrentId(null);
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  
  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    if (name) {
      setFormData(prev => ({
        ...prev,
        [name]: name === 'day_of_week' ? Number(value) : value
      }));
    }
  };
  
  const handleStartTimeChange = (newTime: dayjs.Dayjs | null) => {
    if (newTime) {
      setStartTime(newTime);
      setFormData(prev => ({
        ...prev,
        start_time: newTime.format('HH:mm:ss')
      }));
    }
  };
  
  const handleEndTimeChange = (newTime: dayjs.Dayjs | null) => {
    if (newTime) {
      setEndTime(newTime);
      setFormData(prev => ({
        ...prev,
        end_time: newTime.format('HH:mm:ss')
      }));
    }
  };
  
  const handleSubmit = async () => {
    try {
      if (currentId) {
        await dataService.updateTimeSlot(currentId, formData);
      } else {
        await dataService.createTimeSlot(formData);
      }
      handleCloseDialog();
      fetchTimeSlots();
    } catch (err) {
      console.error('Error saving time slot:', err);
      setError('Failed to save time slot. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this time slot?')) {
      try {
        await dataService.deleteTimeSlot(id);
        fetchTimeSlots();
      } catch (err) {
        console.error('Error deleting time slot:', err);
        setError('Failed to delete time slot. Please try again.');
      }
    }
  };
  
  // Helper functions to get names by ID
  const getInstitutionName = (id: string) => {
    const institution = institutions.find(inst => inst.id === id);
    return institution ? institution.name : 'Unknown';
  };
  
  const getDayName = (dayNumber: number) => {
    const day = daysOfWeek.find(d => d.value === dayNumber);
    return day ? day.label : 'Unknown';
  };
  
  const formatTime = (timeString: string) => {
    try {
      return dayjs(`2023-01-01T${timeString}`).format('hh:mm A');
    } catch (e) {
      return timeString;
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
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, mt: 2 }}>
          <Typography variant="h4" component="h1">
            Time Slots
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Time Slot
          </Button>
        </Box>
        
        {error && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
            <Typography>{error}</Typography>
          </Paper>
        )}
        
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Day</TableCell>
                <TableCell>Start Time</TableCell>
                <TableCell>End Time</TableCell>
                <TableCell>Institution</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {timeSlots.length > 0 ? (
                timeSlots.map((timeSlot) => (
                  <TableRow key={timeSlot.id}>
                    <TableCell>{timeSlot.name}</TableCell>
                    <TableCell>{getDayName(timeSlot.day_of_week)}</TableCell>
                    <TableCell>{formatTime(timeSlot.start_time)}</TableCell>
                    <TableCell>{formatTime(timeSlot.end_time)}</TableCell>
                    <TableCell>{getInstitutionName(timeSlot.institution_id)}</TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenDialog(timeSlot)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDelete(timeSlot.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No time slots found. Click "Add Time Slot" to create one.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
          <DialogTitle>{currentId ? 'Edit Time Slot' : 'Add Time Slot'}</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Slot Name"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              margin="normal"
              required
              helperText="e.g., 'Morning 1', 'Period 3'"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel id="day-select-label">Day of Week</InputLabel>
              <Select
                labelId="day-select-label"
                id="day-select"
                name="day_of_week"
                value={formData.day_of_week}
                onChange={handleFormChange}
                label="Day of Week"
                required
              >
                {daysOfWeek.map((day) => (
                  <MenuItem key={day.value} value={day.value}>
                    {day.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Box sx={{ display: 'flex', gap: 2, my: 2 }}>
              <TimePicker
                label="Start Time"
                value={startTime}
                onChange={handleStartTimeChange}
                sx={{ width: '100%' }}
              />
              <TimePicker
                label="End Time"
                value={endTime}
                onChange={handleEndTimeChange}
                sx={{ width: '100%' }}
              />
            </Box>
            <FormControl fullWidth margin="normal">
              <InputLabel id="institution-select-label">Institution</InputLabel>
              <Select
                labelId="institution-select-label"
                id="institution-select"
                name="institution_id"
                value={formData.institution_id}
                onChange={handleFormChange}
                label="Institution"
                required
              >
                {institutions.map((institution) => (
                  <MenuItem key={institution.id} value={institution.id}>
                    {institution.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleSubmit} 
              color="primary" 
              variant="contained"
              disabled={!formData.name || !formData.institution_id}
            >
              {currentId ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </LocalizationProvider>
  );
};

export default TimeSlots;
