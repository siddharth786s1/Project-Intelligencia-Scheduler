import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  CardActions,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';
import SchedulerService from '../services/schedulerService';

interface Job {
  id: string;
  status: string;
  progress: number;
  created_at: string;
  algorithm: string;
}

interface QueueStatus {
  active_jobs: number;
  queue_size: number;
  running_workers: number;
  max_workers: number;
  system_load: number;
}

interface SchedulerMonitorProps {
  onRefresh?: () => void;
}

const SchedulerMonitor: React.FC<SchedulerMonitorProps> = ({ onRefresh }) => {
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [activeJobs, setActiveJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQueueStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const status = await SchedulerService.getQueueStatus();
      setQueueStatus(status);
      
      // For a real implementation, we would fetch active jobs as well
      // For now, we'll use mock data
      setActiveJobs([
        {
          id: 'job-123',
          status: 'processing',
          progress: 65,
          created_at: new Date().toISOString(),
          algorithm: 'Genetic Algorithm'
        },
        {
          id: 'job-124',
          status: 'waiting',
          progress: 0,
          created_at: new Date().toISOString(),
          algorithm: 'Constraint Solver'
        }
      ]);
    } catch (err: any) {
      console.error('Error fetching queue status:', err);
      setError(err.message || 'Failed to fetch queue status');
      
      // Mock data for development
      setQueueStatus({
        active_jobs: 2,
        queue_size: 3,
        running_workers: 2,
        max_workers: 4,
        system_load: 0.65
      });
    } finally {
      setLoading(false);
      if (onRefresh) onRefresh();
    }
  };

  useEffect(() => {
    fetchQueueStatus();
    
    // Set up auto-refresh every 30 seconds
    const intervalId = setInterval(fetchQueueStatus, 30000);
    
    return () => clearInterval(intervalId);
  }, []);

  const getSystemStatusColor = () => {
    if (!queueStatus) return 'default';
    
    const load = queueStatus.system_load;
    if (load < 0.5) return 'success';
    if (load < 0.8) return 'warning';
    return 'error';
  };

  const getSystemStatusIcon = () => {
    const status = getSystemStatusColor();
    
    if (status === 'success') return <CheckCircleIcon color="success" />;
    if (status === 'warning') return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'waiting':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ mr: 2 }}>Scheduler System Status</Typography>
          {queueStatus && (
            <Chip
              icon={getSystemStatusIcon()}
              label={queueStatus.system_load < 0.5 ? "Normal" : queueStatus.system_load < 0.8 ? "Busy" : "Overloaded"}
              color={getSystemStatusColor() as any}
              variant="outlined"
              size="small"
            />
          )}
        </Box>
        <Button
          startIcon={<RefreshIcon />}
          onClick={fetchQueueStatus}
          disabled={loading}
          size="small"
        >
          Refresh
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      {queueStatus && (
        <>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(4, 1fr)' }, gap: 2, mb: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">Active Jobs</Typography>
              <Typography variant="h6">{queueStatus.active_jobs}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Queue Size</Typography>
              <Typography variant="h6">{queueStatus.queue_size}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Workers</Typography>
              <Typography variant="h6">{queueStatus.running_workers}/{queueStatus.max_workers}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">System Load</Typography>
              <Typography variant="h6">{(queueStatus.system_load * 100).toFixed(1)}%</Typography>
            </Box>
          </Box>
          
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="subtitle1" sx={{ mb: 2 }}>Active Jobs</Typography>
          
          {activeJobs.length === 0 ? (
            <Typography variant="body2">No active jobs at the moment</Typography>
          ) : (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
              {activeJobs.map((job) => (
                <Card variant="outlined" key={job.id}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2">{job.algorithm}</Typography>
                      <Chip
                        label={job.status}
                        size="small"
                        color={getJobStatusColor(job.status) as any}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      ID: {job.id}
                    </Typography>
                    {job.status === 'processing' && (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress variant="determinate" value={job.progress} />
                        </Box>
                        <Box sx={{ minWidth: 35 }}>
                          <Typography variant="body2" color="text.secondary">{`${Math.round(job.progress)}%`}</Typography>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button size="small">View Details</Button>
                    {job.status === 'processing' && (
                      <Button size="small" color="error">Cancel</Button>
                    )}
                    <Box sx={{ flexGrow: 1 }} />
                    <Tooltip title="More options">
                      <IconButton size="small">
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              ))}
            </Box>
          )}
        </>
      )}
    </Paper>
  );
};

export default SchedulerMonitor;
