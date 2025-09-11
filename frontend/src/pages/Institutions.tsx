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
  Box
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useDataService } from '../services/dataService';

interface Institution {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  created_at: string;
  updated_at: string;
}

interface InstitutionFormData {
  name: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
}

const Institutions = () => {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<InstitutionFormData>({
    name: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: ''
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchInstitutions = async () => {
    setLoading(true);
    try {
      const response = await dataService.getInstitutions();
      setInstitutions(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching institutions:', err);
      setError('Failed to load institutions. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchInstitutions();
  }, []);
  
  const handleOpenDialog = (institution?: Institution) => {
    if (institution) {
      setFormData({
        name: institution.name,
        address: institution.address,
        city: institution.city,
        state: institution.state,
        country: institution.country,
        postal_code: institution.postal_code
      });
      setCurrentId(institution.id);
    } else {
      setFormData({
        name: '',
        address: '',
        city: '',
        state: '',
        country: '',
        postal_code: ''
      });
      setCurrentId(null);
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  
  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async () => {
    try {
      if (currentId) {
        await dataService.updateInstitution(currentId, formData);
      } else {
        await dataService.createInstitution(formData);
      }
      handleCloseDialog();
      fetchInstitutions();
    } catch (err) {
      console.error('Error saving institution:', err);
      setError('Failed to save institution. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this institution?')) {
      try {
        await dataService.deleteInstitution(id);
        fetchInstitutions();
      } catch (err) {
        console.error('Error deleting institution:', err);
        setError('Failed to delete institution. Please try again.');
      }
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
          Institutions
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Institution
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
              <TableCell>City</TableCell>
              <TableCell>State</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {institutions.length > 0 ? (
              institutions.map((institution) => (
                <TableRow key={institution.id}>
                  <TableCell>{institution.name}</TableCell>
                  <TableCell>{institution.city}</TableCell>
                  <TableCell>{institution.state}</TableCell>
                  <TableCell>{institution.country}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(institution)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(institution.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No institutions found. Click "Add Institution" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>{currentId ? 'Edit Institution' : 'Add Institution'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Institution Name"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleFormChange}
            margin="normal"
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="City"
              name="city"
              value={formData.city}
              onChange={handleFormChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="State/Province"
              name="state"
              value={formData.state}
              onChange={handleFormChange}
              margin="normal"
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Country"
              name="country"
              value={formData.country}
              onChange={handleFormChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Postal Code"
              name="postal_code"
              value={formData.postal_code}
              onChange={handleFormChange}
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Institutions;
