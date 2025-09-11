import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Button, 
  Box,
  Step,
  StepLabel,
  Stepper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Chip
} from '@mui/material';
import ScheduleIcon from '@mui/icons-material/Schedule';
import SchoolIcon from '@mui/icons-material/School';
import SettingsIcon from '@mui/icons-material/Settings';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useDataService } from '../services/dataService';

const steps = ['Select Departments & Batches', 'Configure Algorithm Settings', 'Generate Timetable'];

const TimetableGenerator = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);
  const [selectedBatches, setSelectedBatches] = useState<string[]>([]);
  const [algorithmType, setAlgorithmType] = useState<'csp' | 'genetic'>('csp');
  const [algorithmParams, setAlgorithmParams] = useState({
    maxIterations: 1000,
    populationSize: 100,
    mutationRate: 0.05,
    timeLimit: 60
  });
  const [loading, setLoading] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationSuccess, setGenerationSuccess] = useState<boolean | null>(null);
  const [generatedTimetableId, setGeneratedTimetableId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setGenerationSuccess(null);
    setGeneratedTimetableId(null);
    setError(null);
    setGenerationProgress(0);
  };
  
  const handleDepartmentChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedDepartments(event.target.value as string[]);
  };
  
  const handleBatchChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedBatches(event.target.value as string[]);
  };
  
  const handleAlgorithmParamChange = (param: string, value: number) => {
    setAlgorithmParams({
      ...algorithmParams,
      [param]: value
    });
  };
  
  const { generateTimetable: apiGenerateTimetable, getGenerationStatus } = useDataService();
  
  const generateTimetable = async () => {
    setLoading(true);
    setGenerationProgress(0);
    setGenerationSuccess(null);
    setError(null);
    
    try {
      // Prepare the timetable generation options
      const options: TimetableGenerationOptions = {
        departments: selectedDepartments,
        batches: selectedBatches,
        algorithm: algorithmType,
        parameters: algorithmParams
      };
      
      // Call the API to start the timetable generation job
      const { data } = await apiGenerateTimetable(options);
      const jobId = data.job_id;
      
      // Poll for job status
      const statusCheckInterval = setInterval(async () => {
        try {
          const { data: statusData } = await getGenerationStatus(jobId);
          
          // Update progress
          if (statusData.progress !== undefined) {
            setGenerationProgress(statusData.progress);
          }
          
          // Check if job is completed or failed
          if (statusData.status === 'completed') {
            clearInterval(statusCheckInterval);
            setGenerationSuccess(true);
            setGeneratedTimetableId(statusData.timetable_id);
            setGenerationProgress(100);
            setLoading(false);
          } else if (statusData.status === 'failed') {
            clearInterval(statusCheckInterval);
            setGenerationSuccess(false);
            setError(statusData.message || 'Timetable generation failed');
            setLoading(false);
          }
        } catch (err) {
          console.error('Error checking job status:', err);
          clearInterval(statusCheckInterval);
          setError('Failed to check job status');
          setGenerationSuccess(false);
          setLoading(false);
        }
      }, 2000); // Check status every 2 seconds
    } catch (err) {
      console.error('Error generating timetable:', err);
      setError('Failed to generate timetable. Please try again.');
      setGenerationSuccess(false);
      setLoading(false);
    }
  };
  
  // Fetch real data from API
  const { getDepartments, getBatches } = useDataService();
  const [departments, setDepartments] = useState<any[]>([]);
  const [batches, setBatches] = useState<any[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState<string | null>(null);
  
  // Load departments and batches
  useEffect(() => {
    const loadData = async () => {
      setDataLoading(true);
      try {
        // Load departments
        const { data: deptsData } = await getDepartments(0, 100);
        setDepartments(deptsData);
        
        // Load batches
        const { data: batchesData } = await getBatches(0, 100);
        setBatches(batchesData);
        
        setDataLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setDataError('Failed to load departments and batches');
        setDataLoading(false);
      }
    };
    
    loadData();
  }, []);
  
  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            {dataLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
              </Box>
            ) : dataError ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                {dataError}
              </Alert>
            ) : (
              <>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="departments-select-label">Departments</InputLabel>
                  <Select
                    labelId="departments-select-label"
                    id="departments-select"
                    multiple
                    value={selectedDepartments}
                    onChange={handleDepartmentChange}
                    label="Departments"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(selected as string[]).map((value) => {
                          const dept = departments.find(d => d.id === value);
                          return <Chip key={value} label={dept?.name || value} />;
                        })}
                      </Box>
                    )}
                  >
                    {departments.map((dept) => (
                      <MenuItem key={dept.id} value={dept.id}>
                        {dept.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal">
                  <InputLabel id="batches-select-label">Batches</InputLabel>
                  <Select
                    labelId="batches-select-label"
                    id="batches-select"
                    multiple
                    value={selectedBatches}
                    onChange={handleBatchChange}
                    label="Batches"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(selected as string[]).map((value) => {
                          const batch = batches.find(b => b.id === value);
                          return <Chip key={value} label={batch?.name || value} />;
                        })}
                      </Box>
                    )}
                  >
                    {batches
                      .filter(batch => selectedDepartments.length === 0 || selectedDepartments.includes(batch.department_id))
                      .map((batch) => (
                        <MenuItem key={batch.id} value={batch.id}>
                          {batch.name}
                        </MenuItem>
                      ))}
                  </Select>
                </FormControl>
              </>
            )}
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel id="algorithm-select-label">Algorithm Type</InputLabel>
                  <Select
                    labelId="algorithm-select-label"
                    id="algorithm-select"
                    value={algorithmType}
                    onChange={(e) => setAlgorithmType(e.target.value as 'csp' | 'genetic')}
                    label="Algorithm Type"
                  >
                    <MenuItem value="csp">Constraint Satisfaction Problem (CSP)</MenuItem>
                    <MenuItem value="genetic">Genetic Algorithm</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="time-limit-label">Time Limit (seconds)</InputLabel>
                  <Select
                    labelId="time-limit-label"
                    id="time-limit-select"
                    value={algorithmParams.timeLimit}
                    onChange={(e) => handleAlgorithmParamChange('timeLimit', Number(e.target.value))}
                    label="Time Limit (seconds)"
                  >
                    <MenuItem value={30}>30 seconds</MenuItem>
                    <MenuItem value={60}>1 minute</MenuItem>
                    <MenuItem value={300}>5 minutes</MenuItem>
                    <MenuItem value={600}>10 minutes</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              {algorithmType === 'genetic' && (
                <>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="population-size-label">Population Size</InputLabel>
                      <Select
                        labelId="population-size-label"
                        id="population-size-select"
                        value={algorithmParams.populationSize}
                        onChange={(e) => handleAlgorithmParamChange('populationSize', Number(e.target.value))}
                        label="Population Size"
                      >
                        <MenuItem value={50}>Small (50)</MenuItem>
                        <MenuItem value={100}>Medium (100)</MenuItem>
                        <MenuItem value={200}>Large (200)</MenuItem>
                        <MenuItem value={500}>Very Large (500)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="iterations-label">Max Iterations</InputLabel>
                      <Select
                        labelId="iterations-label"
                        id="iterations-select"
                        value={algorithmParams.maxIterations}
                        onChange={(e) => handleAlgorithmParamChange('maxIterations', Number(e.target.value))}
                        label="Max Iterations"
                      >
                        <MenuItem value={500}>500 iterations</MenuItem>
                        <MenuItem value={1000}>1000 iterations</MenuItem>
                        <MenuItem value={2000}>2000 iterations</MenuItem>
                        <MenuItem value={5000}>5000 iterations</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="mutation-rate-label">Mutation Rate</InputLabel>
                      <Select
                        labelId="mutation-rate-label"
                        id="mutation-rate-select"
                        value={algorithmParams.mutationRate}
                        onChange={(e) => handleAlgorithmParamChange('mutationRate', Number(e.target.value))}
                        label="Mutation Rate"
                      >
                        <MenuItem value={0.01}>Low (1%)</MenuItem>
                        <MenuItem value={0.05}>Medium (5%)</MenuItem>
                        <MenuItem value={0.1}>High (10%)</MenuItem>
                        <MenuItem value={0.2}>Very High (20%)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </>
              )}
              
              {algorithmType === 'csp' && (
                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        CSP Algorithm Settings
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        The Constraint Satisfaction Problem solver will attempt to find a valid solution that
                        satisfies all hard constraints and optimizes for soft constraints. The solver will run
                        until it finds a solution or reaches the specified time limit.
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 3 }}>
            {loading || generationProgress > 0 ? (
              <Box sx={{ width: '100%', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body1" sx={{ flexGrow: 1 }}>
                    {generationProgress < 100 ? 'Generating Timetable...' : 'Timetable Generation Complete'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {Math.floor(generationProgress)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={generationProgress} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
                
                {generationProgress === 100 && (
                  <Box sx={{ mt: 2 }}>
                    {generationSuccess === true && generatedTimetableId && (
                      <Alert 
                        severity="success"
                        icon={<CheckCircleIcon fontSize="inherit" />}
                        sx={{ mb: 2 }}
                        action={
                          <Button 
                            color="inherit" 
                            size="small"
                            onClick={() => window.location.href = `/timetable-viewer?id=${generatedTimetableId}`}
                          >
                            View Timetable
                          </Button>
                        }
                      >
                        Timetable successfully generated! You can now view or export the timetable.
                      </Alert>
                    )}
                    
                    {generationSuccess === false && (
                      <Alert 
                        severity="error" 
                        sx={{ mb: 2 }}
                      >
                        {error || 'An error occurred while generating the timetable. Please try again.'}
                      </Alert>
                    )}
                  </Box>
                )}
              </Box>
            ) : (
              <Box>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">Selected Departments & Batches</Typography>
                    </Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2">Departments:</Typography>
                        <List dense>
                          {selectedDepartments.map(deptId => {
                            const dept = departments.find(d => d.id === deptId);
                            return (
                              <ListItem key={deptId}>
                                <ListItemText primary={dept?.name || deptId} />
                              </ListItem>
                            );
                          })}
                        </List>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2">Batches:</Typography>
                        <List dense>
                          {selectedBatches.map(batchId => {
                            const batch = batches.find(b => b.id === batchId);
                            return (
                              <ListItem key={batchId}>
                                <ListItemText primary={batch?.name || batchId} />
                              </ListItem>
                            );
                          })}
                        </List>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
                
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SettingsIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">Algorithm Settings</Typography>
                    </Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Algorithm: {algorithmType === 'csp' ? 'Constraint Satisfaction Problem' : 'Genetic Algorithm'}
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Time Limit" 
                          secondary={`${algorithmParams.timeLimit} seconds`}
                        />
                      </ListItem>
                      {algorithmType === 'genetic' && (
                        <>
                          <ListItem>
                            <ListItemText 
                              primary="Population Size" 
                              secondary={algorithmParams.populationSize}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText 
                              primary="Max Iterations" 
                              secondary={algorithmParams.maxIterations}
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText 
                              primary="Mutation Rate" 
                              secondary={`${algorithmParams.mutationRate * 100}%`}
                            />
                          </ListItem>
                        </>
                      )}
                    </List>
                  </CardContent>
                </Card>
                
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    startIcon={<PlayArrowIcon />}
                    onClick={generateTimetable}
                    disabled={selectedBatches.length === 0}
                  >
                    Generate Timetable
                  </Button>
                </Box>
              </Box>
            )}
            
            {generatedTimetableId && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button 
                  variant="contained"
                  color="secondary"
                  startIcon={<ScheduleIcon />}
                  href={`/timetable-viewer?id=${generatedTimetableId}`}
                >
                  View Generated Timetable
                </Button>
              </Box>
            )}
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container>
      <Box sx={{ mb: 4, mt: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Timetable Generator
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate optimized timetables for your institution using advanced scheduling algorithms.
        </Typography>
      </Box>
      
      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box sx={{ mt: 3 }}>
          {getStepContent(activeStep)}
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            color="inherit"
            disabled={activeStep === 0 || loading}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep === steps.length - 1 ? (
            generationSuccess && (
              <Button onClick={handleReset} disabled={loading}>
                Start New Generation
              </Button>
            )
          ) : (
            <Button 
              variant="contained" 
              onClick={handleNext}
              disabled={
                (activeStep === 0 && selectedBatches.length === 0) || 
                loading
              }
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default TimetableGenerator;
