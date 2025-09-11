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

interface Classroom {
  id: string;
  name: string;
  capacity: number;
  building: string;
  floor: number;
  room_type_id: string;
  institution_id: string;
  created_at: string;
  updated_at: string;
}

interface Institution {
  id: string;
  name: string;
}

interface RoomType {
  id: string;
  name: string;
}

interface ClassroomFormData {
  name: string;
  capacity: number;
  building: string;
  floor: number;
  room_type_id: string;
  institution_id: string;
}

const Classrooms = () => {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState<ClassroomFormData>({
    name: '',
    capacity: 60,
    building: '',
    floor: 0,
    room_type_id: '',
    institution_id: '',
  });
  const [currentId, setCurrentId] = useState<string | null>(null);
  
  const dataService = useDataService();
  
  const fetchClassrooms = async () => {
    setLoading(true);
    try {
      const response = await dataService.getClassrooms();
      setClassrooms(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching classrooms:', err);
      setError('Failed to load classrooms. Please try again.');
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
  
  const fetchRoomTypes = async () => {
    try {
      // Assuming there's an API endpoint to get room types
      // If not available, can be hardcoded
      const roomTypesData = [
        { id: '1', name: 'Lecture Hall' },
        { id: '2', name: 'Laboratory' },
        { id: '3', name: 'Seminar Room' },
        { id: '4', name: 'Tutorial Room' }
      ];
      setRoomTypes(roomTypesData);
    } catch (err) {
      console.error('Error fetching room types:', err);
      setError('Failed to load room types.');
    }
  };
  
  useEffect(() => {
    Promise.all([fetchClassrooms(), fetchInstitutions(), fetchRoomTypes()]);
  }, []);
  
  const handleOpenDialog = (classroom?: Classroom) => {
    if (classroom) {
      setFormData({
        name: classroom.name,
        capacity: classroom.capacity,
        building: classroom.building,
        floor: classroom.floor,
        room_type_id: classroom.room_type_id,
        institution_id: classroom.institution_id,
      });
      setCurrentId(classroom.id);
    } else {
      setFormData({
        name: '',
        capacity: 60,
        building: '',
        floor: 0,
        room_type_id: roomTypes.length > 0 ? roomTypes[0].id : '',
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
        [name]: name === 'capacity' || name === 'floor' ? Number(value) : value
      }));
    }
  };
  
  const handleSubmit = async () => {
    try {
      if (currentId) {
        await dataService.updateClassroom(currentId, formData);
      } else {
        await dataService.createClassroom(formData);
      }
      handleCloseDialog();
      fetchClassrooms();
    } catch (err) {
      console.error('Error saving classroom:', err);
      setError('Failed to save classroom. Please try again.');
    }
  };
  
  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this classroom?')) {
      try {
        await dataService.deleteClassroom(id);
        fetchClassrooms();
      } catch (err) {
        console.error('Error deleting classroom:', err);
        setError('Failed to delete classroom. Please try again.');
      }
    }
  };
  
  // Helper functions to get names by ID
  const getInstitutionName = (id: string) => {
    const institution = institutions.find(inst => inst.id === id);
    return institution ? institution.name : 'Unknown';
  };
  
  const getRoomTypeName = (id: string) => {
    const roomType = roomTypes.find(rt => rt.id === id);
    return roomType ? roomType.name : 'Unknown';
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
          Classrooms
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Classroom
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
              <TableCell>Building</TableCell>
              <TableCell>Floor</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Institution</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {classrooms.length > 0 ? (
              classrooms.map((classroom) => (
                <TableRow key={classroom.id}>
                  <TableCell>{classroom.name}</TableCell>
                  <TableCell>{classroom.building}</TableCell>
                  <TableCell>{classroom.floor}</TableCell>
                  <TableCell>{getRoomTypeName(classroom.room_type_id)}</TableCell>
                  <TableCell>{classroom.capacity}</TableCell>
                  <TableCell>{getInstitutionName(classroom.institution_id)}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleOpenDialog(classroom)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(classroom.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No classrooms found. Click "Add Classroom" to create one.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>{currentId ? 'Edit Classroom' : 'Add Classroom'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Classroom Name/Number"
            name="name"
            value={formData.name}
            onChange={handleFormChange}
            margin="normal"
            required
            helperText="e.g., LH-101, Lab-A4"
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Building"
              name="building"
              value={formData.building}
              onChange={handleFormChange}
              margin="normal"
              required
              helperText="e.g., Main Building, CS Block"
            />
            <TextField
              fullWidth
              label="Floor"
              name="floor"
              type="number"
              value={formData.floor}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: -2, max: 20 }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="room-type-select-label">Room Type</InputLabel>
              <Select
                labelId="room-type-select-label"
                id="room-type-select"
                name="room_type_id"
                value={formData.room_type_id}
                onChange={handleFormChange}
                label="Room Type"
                required
              >
                {roomTypes.map((roomType) => (
                  <MenuItem key={roomType.id} value={roomType.id}>
                    {roomType.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Capacity"
              name="capacity"
              type="number"
              value={formData.capacity}
              onChange={handleFormChange}
              margin="normal"
              required
              inputProps={{ min: 1 }}
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
            disabled={!formData.name || !formData.building || !formData.room_type_id || !formData.institution_id}
          >
            {currentId ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Classrooms;
