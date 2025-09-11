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
  Chip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useDataService } from '../services/dataService';

interface Faculty {
  id: string;
  name: string;
  email: string;
  department_id: string;
  max_hours_per_week: number;
  specializations: string[];
  created_at: string;
  updated_at: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
}

interface FacultyFormData {
  name: string;
  email: string;
  department_id: string;
  max_hours_per_week: number;
  specializations: string;
}

const Faculty = () => {
  const [faculty, setFaculty] = useState<Faculty[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<FacultyFormData>({
    name: '',
    email: '',
    department_id: '',
    max_hours_per_week: 40,
    specializations: '',
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchFaculty = async () => {
    setLoading(true);
    try {
      const response = await dataService.getFaculty();
      setFaculty(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching faculty:', err);
      setError('Failed to load faculty data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchDepartments = async () => {
    try {
      const response = await dataService.getDepartments();
      setDepartments(response.data);
    } catch (err) {
      console.error('Error fetching departments:', err);
      setError('Failed to load departments.');
    }
  };
  
  useEffect(() => {
    Promise.all([fetchFaculty(), fetchDepartments()]);
  }, []);
  
  const handleOpenDialog = (facultyMember?: Faculty) => {
    if (facultyMember) {
      setFormData({
        name: facultyMember.name,
        email: facultyMember.email,
        department_id: facultyMember.department_id,
        max_hours_per_week: facultyMember.max_hours_per_week,
        specializations: facultyMember.specializations.join(', '),
      });
      setCurrentId(facultyMember.id);
    } else {
      setFormData({
        name: '',
        email: '',
        department_id: departments.length > 0 ? departments[0].id : '',
        max_hours_per_week: 40,
        specializations: '',
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
        [name]: value
      }));
    }
  };
  
  const handleSubmit = async () => {
    try {
      const formattedData = {
        ...formData,
        max_hours_per_week: Number(formData.max_hours_per_week),
        specializations: formData.specializations.split(',').map(s => s.trim()).filter(s => s),
      };
      
      if (currentId) {
        await dataService.updateFaculty(currentId, formattedData);
      } else {
        await dataService.createFaculty(formattedData);
      }
      handleCloseDialog();
      fetchFaculty();
    } catch (err) {
      console.error('Error saving faculty member:', err);
      setError('Failed to save faculty member. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this faculty member?')) {
      try {
        await dataService.deleteFaculty(id);
        fetchFaculty();
      } catch (err) {
        console.error('Error deleting faculty member:', err);
        setError('Failed to delete faculty member. Please try again.');
      }
    }
  };
  
  // Helper function to get department name by ID
  const getDepartmentName = (id: string) => {
    const department = departments.find(dept => dept.id === id);
    return department ? department.name : 'Unknown';
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
          Faculty
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Faculty Member
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
              <TableCell>Email</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Max Hours/Week</TableCell>
              <TableCell>Specializations</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {faculty.length > 0 ? (
              faculty.map((member) => (
                <TableRow key={member.id}>
                  <TableCell>{member.name}</TableCell>
                  <TableCell>{member.email}</TableCell>
                  <TableCell>{getDepartmentName(member.department_id)}</TableCell>
                  <TableCell>{member.max_hours_per_week}</TableCell>
                  <TableCell>
                    {member.specializations.map(spec => (
                      <Chip 
                        key={spec} 
                        label={spec} 
                        size="small" 
                        sx={{ mr: 0.5, mb: 0.5 }} 
                      />
                    ))}
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(member)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(member.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No faculty members found. Click "Add Faculty Member" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>{currentId ? 'Edit Faculty Member' : 'Add Faculty Member'}</DialogTitle>
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
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleFormChange}
            margin="normal"
            required
          />
          <FormControl fullWidth margin="normal">
            <InputLabel id="department-select-label">Department</InputLabel>
            <Select
              labelId="department-select-label"
              id="department-select"
              name="department_id"
              value={formData.department_id}
              onChange={handleFormChange}
              label="Department"
              required
            >
              {departments.map((department) => (
                <MenuItem key={department.id} value={department.id}>
                  {department.name} ({department.code})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Maximum Hours per Week"
            name="max_hours_per_week"
            type="number"
            value={formData.max_hours_per_week}
            onChange={handleFormChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Specializations"
            name="specializations"
            value={formData.specializations}
            onChange={handleFormChange}
            margin="normal"
            helperText="Enter specializations separated by commas (e.g., Data Structures, Algorithms, Database Systems)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.email || !formData.department_id}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Faculty;
