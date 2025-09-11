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
  Checkbox,
  Chip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useDataService } from '../services/dataService';

interface SchedulingConstraint {
  id: string;
  name: string;
  description: string;
  constraint_type: string;
  priority: number;
  parameters: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface ConstraintFormData {
  name: string;
  description: string;
  constraint_type: string;
  priority: number;
  parameters: Record<string, any>;
}

const constraintTypes = [
  { value: 'faculty_unavailability', label: 'Faculty Unavailability' },
  { value: 'room_unavailability', label: 'Room Unavailability' },
  { value: 'batch_unavailability', label: 'Batch Unavailability' },
  { value: 'faculty_preference', label: 'Faculty Preference' },
  { value: 'same_time', label: 'Same Time' },
  { value: 'different_time', label: 'Different Time' },
  { value: 'consecutive_sessions', label: 'Consecutive Sessions' },
  { value: 'room_requirement', label: 'Room Requirement' }
];

const Constraints = () => {
  const [constraints, setConstraints] = useState<SchedulingConstraint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<ConstraintFormData>({
    name: '',
    description: '',
    constraint_type: 'faculty_unavailability',
    priority: 1,
    parameters: {},
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchConstraints = async () => {
    setLoading(true);
    try {
      // Assuming there's an API endpoint for constraints
      // If not available, can be mocked
      const mockConstraints: SchedulingConstraint[] = [
        {
          id: '1',
          name: 'Prof. Smith Unavailable on Fridays',
          description: 'Prof. Smith cannot teach on Fridays due to research commitments',
          constraint_type: 'faculty_unavailability',
          priority: 2,
          parameters: {
            faculty_id: 'faculty123',
            days: [5] // Friday
          },
          created_at: '2023-07-01T10:00:00',
          updated_at: '2023-07-01T10:00:00'
        },
        {
          id: '2',
          name: 'Computer Lab Maintenance',
          description: 'Computer Lab is unavailable on Monday mornings for maintenance',
          constraint_type: 'room_unavailability',
          priority: 1,
          parameters: {
            room_id: 'room456',
            days: [1],
            start_time: '08:00:00',
            end_time: '12:00:00'
          },
          created_at: '2023-07-02T10:00:00',
          updated_at: '2023-07-02T10:00:00'
        },
      ];
      
      setConstraints(mockConstraints);
      setError(null);
    } catch (err) {
      console.error('Error fetching constraints:', err);
      setError('Failed to load scheduling constraints. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchConstraints();
  }, []);
  
  const handleOpenDialog = (constraint?: SchedulingConstraint) => {
    if (constraint) {
      setFormData({
        name: constraint.name,
        description: constraint.description,
        constraint_type: constraint.constraint_type,
        priority: constraint.priority,
        parameters: constraint.parameters,
      });
      setCurrentId(constraint.id);
    } else {
      setFormData({
        name: '',
        description: '',
        constraint_type: 'faculty_unavailability',
        priority: 1,
        parameters: {},
      });
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
        [name]: name === 'priority' ? Number(value) : value
      }));
    }
  };
  
  const handleParameterChange = (paramName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [paramName]: value
      }
    }));
  };
  
  const handleSubmit = async () => {
    try {
      // In a real app, you would call your API service here
      // For now, we'll just update the local state
      if (currentId) {
        const updatedConstraints = constraints.map(c => 
          c.id === currentId ? { ...c, ...formData, updated_at: new Date().toISOString() } : c
        );
        setConstraints(updatedConstraints);
      } else {
        const newConstraint: SchedulingConstraint = {
          id: `new-${Date.now()}`,
          ...formData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setConstraints([...constraints, newConstraint]);
      }
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving constraint:', err);
      setError('Failed to save constraint. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this constraint?')) {
      try {
        // In a real app, you would call your API service here
        const filteredConstraints = constraints.filter(c => c.id !== id);
        setConstraints(filteredConstraints);
      } catch (err) {
        console.error('Error deleting constraint:', err);
        setError('Failed to delete constraint. Please try again.');
      }
    }
  };
  
  // Helper function to render constraint type
  const getConstraintTypeLabel = (type: string) => {
    const constraintType = constraintTypes.find(t => t.value === type);
    return constraintType ? constraintType.label : type;
  };
  
  // Helper function to render parameters in a human-readable format
  const renderParametersSummary = (parameters: Record<string, any>) => {
    const paramParts: string[] = [];
    
    if (parameters.faculty_id) {
      paramParts.push(`Faculty ID: ${parameters.faculty_id}`);
    }
    
    if (parameters.room_id) {
      paramParts.push(`Room ID: ${parameters.room_id}`);
    }
    
    if (parameters.days && parameters.days.length) {
      const dayNames = parameters.days.map((day: number) => {
        const dayMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return dayMap[day];
      });
      paramParts.push(`Days: ${dayNames.join(', ')}`);
    }
    
    if (parameters.start_time && parameters.end_time) {
      paramParts.push(`Time: ${parameters.start_time} - ${parameters.end_time}`);
    }
    
    return paramParts.join(' | ');
  };
  
  // Dynamic parameter inputs based on constraint type
  const renderParameterInputs = () => {
    switch(formData.constraint_type) {
      case 'faculty_unavailability':
        return (
          <>
            <TextField
              fullWidth
              label="Faculty ID"
              name="faculty_id"
              value={formData.parameters.faculty_id || ''}
              onChange={e => handleParameterChange('faculty_id', e.target.value)}
              margin="normal"
              required
            />
            <FormControl fullWidth margin="normal">
              <Typography variant="body2" gutterBottom>Days Unavailable</Typography>
              <FormGroup row>
                {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((day, index) => (
                  <FormControlLabel
                    key={index}
                    control={
                      <Checkbox
                        checked={formData.parameters.days?.includes(index) || false}
                        onChange={e => {
                          const days = formData.parameters.days || [];
                          const newDays = e.target.checked 
                            ? [...days, index]
                            : days.filter(d => d !== index);
                          handleParameterChange('days', newDays);
                        }}
                      />
                    }
                    label={day}
                  />
                ))}
              </FormGroup>
            </FormControl>
          </>
        );
      case 'room_unavailability':
        return (
          <>
            <TextField
              fullWidth
              label="Room ID"
              name="room_id"
              value={formData.parameters.room_id || ''}
              onChange={e => handleParameterChange('room_id', e.target.value)}
              margin="normal"
              required
            />
            <FormControl fullWidth margin="normal">
              <Typography variant="body2" gutterBottom>Days Unavailable</Typography>
              <FormGroup row>
                {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((day, index) => (
                  <FormControlLabel
                    key={index}
                    control={
                      <Checkbox
                        checked={formData.parameters.days?.includes(index) || false}
                        onChange={e => {
                          const days = formData.parameters.days || [];
                          const newDays = e.target.checked 
                            ? [...days, index]
                            : days.filter(d => d !== index);
                          handleParameterChange('days', newDays);
                        }}
                      />
                    }
                    label={day}
                  />
                ))}
              </FormGroup>
            </FormControl>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Start Time"
                name="start_time"
                value={formData.parameters.start_time || ''}
                onChange={e => handleParameterChange('start_time', e.target.value)}
                margin="normal"
                type="time"
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="End Time"
                name="end_time"
                value={formData.parameters.end_time || ''}
                onChange={e => handleParameterChange('end_time', e.target.value)}
                margin="normal"
                type="time"
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </>
        );
      default:
        return (
          <Typography color="text.secondary" sx={{ my: 2 }}>
            Additional parameters for this constraint type will be added soon.
          </Typography>
        );
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
    <Container>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, mt: 2 }}>
        <Typography variant="h4" component="h1">
          Scheduling Constraints
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Constraint
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
              <TableCell>Type</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Parameters</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {constraints.length > 0 ? (
              constraints.map((constraint) => (
                <TableRow key={constraint.id}>
                  <TableCell>
                    <Typography variant="body1">{constraint.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {constraint.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={getConstraintTypeLabel(constraint.constraint_type)} 
                      color="primary" 
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{constraint.priority}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {renderParametersSummary(constraint.parameters)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(constraint)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(constraint.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No constraints found. Click "Add Constraint" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>{currentId ? 'Edit Constraint' : 'Add Constraint'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleFormChange}
            margin="normal"
            multiline
            rows={2}
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="constraint-type-label">Constraint Type</InputLabel>
              <Select
                labelId="constraint-type-label"
                id="constraint-type"
                name="constraint_type"
                value={formData.constraint_type}
                onChange={handleFormChange}
                label="Constraint Type"
                required
              >
                {constraintTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Priority"
              name="priority"
              type="number"
              value={formData.priority}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 1, max: 5 }}
              helperText="1 (Low) to 5 (High)"
            />
          </Box>
          
          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
            Constraint Parameters
          </Typography>
          
          {renderParameterInputs()}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.constraint_type}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Constraints;
