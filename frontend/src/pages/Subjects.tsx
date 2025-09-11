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
  MenuItem
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useDataService } from '../services/dataService';

interface Subject {
  id: string;
  name: string;
  code: string;
  credits: number;
  lecture_hours_per_week: number;
  tutorial_hours_per_week: number;
  practical_hours_per_week: number;
  department_id: string;
  created_at: string;
  updated_at: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
}

interface SubjectFormData {
  name: string;
  code: string;
  credits: number;
  lecture_hours_per_week: number;
  tutorial_hours_per_week: number;
  practical_hours_per_week: number;
  department_id: string;
}

const Subjects = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<SubjectFormData>({
    name: '',
    code: '',
    credits: 4,
    lecture_hours_per_week: 3,
    tutorial_hours_per_week: 1,
    practical_hours_per_week: 0,
    department_id: '',
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchSubjects = async () => {
    setLoading(true);
    try {
      const response = await dataService.getSubjects();
      setSubjects(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching subjects:', err);
      setError('Failed to load subjects. Please try again.');
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
    Promise.all([fetchSubjects(), fetchDepartments()]);
  }, []);
  
  const handleOpenDialog = (subject?: Subject) => {
    if (subject) {
      setFormData({
        name: subject.name,
        code: subject.code,
        credits: subject.credits,
        lecture_hours_per_week: subject.lecture_hours_per_week,
        tutorial_hours_per_week: subject.tutorial_hours_per_week,
        practical_hours_per_week: subject.practical_hours_per_week,
        department_id: subject.department_id,
      });
      setCurrentId(subject.id);
    } else {
      setFormData({
        name: '',
        code: '',
        credits: 4,
        lecture_hours_per_week: 3,
        tutorial_hours_per_week: 1,
        practical_hours_per_week: 0,
        department_id: departments.length > 0 ? departments[0].id : '',
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
        [name]: name.includes('_hours') || name === 'credits' ? Number(value) : value
      }));
    }
  };
  
  const handleSubmit = async () => {
    try {
      if (currentId) {
        await dataService.updateSubject(currentId, formData);
      } else {
        await dataService.createSubject(formData);
      }
      handleCloseDialog();
      fetchSubjects();
    } catch (err) {
      console.error('Error saving subject:', err);
      setError('Failed to save subject. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this subject?')) {
      try {
        await dataService.deleteSubject(id);
        fetchSubjects();
      } catch (err) {
        console.error('Error deleting subject:', err);
        setError('Failed to delete subject. Please try again.');
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
          Subjects
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Subject
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
              <TableCell>Code</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Credits</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Hours/Week (L-T-P)</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {subjects.length > 0 ? (
              subjects.map((subject) => (
                <TableRow key={subject.id}>
                  <TableCell>{subject.code}</TableCell>
                  <TableCell>{subject.name}</TableCell>
                  <TableCell>{subject.credits}</TableCell>
                  <TableCell>{getDepartmentName(subject.department_id)}</TableCell>
                  <TableCell>
                    {`${subject.lecture_hours_per_week}-${subject.tutorial_hours_per_week}-${subject.practical_hours_per_week}`}
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(subject)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(subject.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No subjects found. Click "Add Subject" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>{currentId ? 'Edit Subject' : 'Add Subject'}</DialogTitle>
        <DialogContent>
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
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Subject Name"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Subject Code"
              name="code"
              value={formData.code}
              onChange={handleFormChange}
              margin="normal"
              required
              helperText="e.g., CS101, PHY202"
            />
          </Box>
          <TextField
            fullWidth
            label="Credits"
            name="credits"
            type="number"
            value={formData.credits}
            onChange={handleFormChange}
            margin="normal"
            required
            inputProps={{ min: 0 }}
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Lecture Hours/Week"
              name="lecture_hours_per_week"
              type="number"
              value={formData.lecture_hours_per_week}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 0 }}
            />
            <TextField
              fullWidth
              label="Tutorial Hours/Week"
              name="tutorial_hours_per_week"
              type="number"
              value={formData.tutorial_hours_per_week}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 0 }}
            />
            <TextField
              fullWidth
              label="Practical Hours/Week"
              name="practical_hours_per_week"
              type="number"
              value={formData.practical_hours_per_week}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 0 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.code || !formData.department_id}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Subjects;
