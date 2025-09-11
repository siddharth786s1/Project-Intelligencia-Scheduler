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

interface Department {
  id: string;
  name: string;
  code: string;
  institution_id: string;
  created_at: string;
  updated_at: string;
}

interface Institution {
  id: string;
  name: string;
}

interface DepartmentFormData {
  name: string;
  code: string;
  institution_id: string;
}

const Departments = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<DepartmentFormData>({
    name: '',
    code: '',
    institution_id: '',
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchDepartments = async () => {
    setLoading(true);
    try {
      const response = await dataService.getDepartments();
      setDepartments(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching departments:', err);
      setError('Failed to load departments. Please try again.');
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
    Promise.all([fetchDepartments(), fetchInstitutions()]);
  }, []);
  
  const handleOpenDialog = (department?: Department) => {
    if (department) {
      setFormData({
        name: department.name,
        code: department.code,
        institution_id: department.institution_id,
      });
      setCurrentId(department.id);
    } else {
      setFormData({
        name: '',
        code: '',
        institution_id: institutions.length > 0 ? institutions[0].id : '',
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
      if (currentId) {
        await dataService.updateDepartment(currentId, formData);
      } else {
        await dataService.createDepartment(formData);
      }
      handleCloseDialog();
      fetchDepartments();
    } catch (err) {
      console.error('Error saving department:', err);
      setError('Failed to save department. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this department?')) {
      try {
        await dataService.deleteDepartment(id);
        fetchDepartments();
      } catch (err) {
        console.error('Error deleting department:', err);
        setError('Failed to delete department. Please try again.');
      }
    }
  };
  
  // Helper function to get institution name by ID
  const getInstitutionName = (id: string) => {
    const institution = institutions.find(inst => inst.id === id);
    return institution ? institution.name : 'Unknown';
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
          Departments
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Department
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
              <TableCell>Code</TableCell>
              <TableCell>Institution</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {departments.length > 0 ? (
              departments.map((department) => (
                <TableRow key={department.id}>
                  <TableCell>{department.name}</TableCell>
                  <TableCell>{department.code}</TableCell>
                  <TableCell>{getInstitutionName(department.institution_id)}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(department)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(department.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No departments found. Click "Add Department" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="sm">
        <DialogTitle>{currentId ? 'Edit Department' : 'Add Department'}</DialogTitle>
        <DialogContent>
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
          <TextField
            fullWidth
            label="Department Name"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Department Code"
            name="code"
            value={formData.code}
            onChange={handleFormChange}
            margin="normal"
            required
            helperText="Short unique code (e.g., CS, EE)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.code || !formData.institution_id}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Departments;
