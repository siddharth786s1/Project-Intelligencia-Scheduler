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

interface Batch {
  id: string;
  name: string;
  year: number;
  department_id: string;
  size: number;
  created_at: string;
  updated_at: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
}

interface BatchFormData {
  name: string;
  year: number;
  department_id: string;
  size: number;
}

const Batches = () => {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<BatchFormData>({
    name: '',
    year: new Date().getFullYear(),
    department_id: '',
    size: 60,
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchBatches = async () => {
    setLoading(true);
    try {
      const response = await dataService.getBatches();
      setBatches(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching batches:', err);
      setError('Failed to load batches. Please try again.');
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
    Promise.all([fetchBatches(), fetchDepartments()]);
  }, []);
  
  const handleOpenDialog = (batch?: Batch) => {
    if (batch) {
      setFormData({
        name: batch.name,
        year: batch.year,
        department_id: batch.department_id,
        size: batch.size,
      });
      setCurrentId(batch.id);
    } else {
      setFormData({
        name: '',
        year: new Date().getFullYear(),
        department_id: departments.length > 0 ? departments[0].id : '',
        size: 60,
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
        [name]: name === 'year' || name === 'size' ? Number(value) : value
      }));
    }
  };
  
  const handleSubmit = async () => {
    try {
      if (currentId) {
        await dataService.updateBatch(currentId, formData);
      } else {
        await dataService.createBatch(formData);
      }
      handleCloseDialog();
      fetchBatches();
    } catch (err) {
      console.error('Error saving batch:', err);
      setError('Failed to save batch. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this batch?')) {
      try {
        await dataService.deleteBatch(id);
        fetchBatches();
      } catch (err) {
        console.error('Error deleting batch:', err);
        setError('Failed to delete batch. Please try again.');
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
          Batches
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Batch
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
              <TableCell>Year</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batches.length > 0 ? (
              batches.map((batch) => (
                <TableRow key={batch.id}>
                  <TableCell>{batch.name}</TableCell>
                  <TableCell>{batch.year}</TableCell>
                  <TableCell>{getDepartmentName(batch.department_id)}</TableCell>
                  <TableCell>{batch.size}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(batch)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(batch.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No batches found. Click "Add Batch" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="sm">
        <DialogTitle>{currentId ? 'Edit Batch' : 'Add Batch'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Batch Name"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            margin="normal"
            required
            helperText="e.g., B.Tech CSE Section A, MCA First Year"
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
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Year"
              name="year"
              type="number"
              value={formData.year}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 2000, max: 2099 }}
            />
            <TextField
              fullWidth
              label="Batch Size"
              name="size"
              type="number"
              value={formData.size}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 1 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.department_id}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Batches;
