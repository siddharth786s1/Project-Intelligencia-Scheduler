import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import SchedulerMonitor from '../components/SchedulerMonitor';
import SchedulerService from '../services/schedulerService';

// Mock SchedulerService
vi.mock('../services/schedulerService', () => ({
  default: {
    getQueueStatus: vi.fn(),
  }
}));

describe('SchedulerMonitor Component', () => {
  const mockQueueStatus = {
    active_jobs: 2,
    queue_size: 3,
    running_workers: 2,
    max_workers: 4,
    system_load: 0.65
  };

  const mockActiveJobs = [
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
  ];

  beforeEach(() => {
    // Setup mocks
    SchedulerService.getQueueStatus.mockResolvedValue({
      ...mockQueueStatus,
      active_jobs: mockActiveJobs
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should render the component with title', async () => {
    render(<SchedulerMonitor />);
    expect(screen.getByText('Scheduler System Status')).toBeInTheDocument();
  });

  it('should fetch queue status on load', async () => {
    render(<SchedulerMonitor />);
    await waitFor(() => {
      expect(SchedulerService.getQueueStatus).toHaveBeenCalledTimes(1);
    });
  });

  it('should display loading state while fetching data', () => {
    render(<SchedulerMonitor />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should display queue metrics when data is loaded', async () => {
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Active Jobs')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument(); // active_jobs count
      expect(screen.getByText('Queue Size')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument(); // queue_size
      expect(screen.getByText('Workers')).toBeInTheDocument();
      expect(screen.getByText('2/4')).toBeInTheDocument(); // running_workers/max_workers
      expect(screen.getByText('System Load')).toBeInTheDocument();
      expect(screen.getByText('65.0%')).toBeInTheDocument(); // system_load as percentage
    });
  });

  it('should display correct system status based on load', async () => {
    // Test with "Busy" status (load between 0.5 and 0.8)
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Busy')).toBeInTheDocument();
    });

    // Cleanup
    vi.clearAllMocks();
    
    // Test with "Normal" status (load < 0.5)
    SchedulerService.getQueueStatus.mockResolvedValue({
      ...mockQueueStatus,
      system_load: 0.3
    });
    
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Normal')).toBeInTheDocument();
    });
    
    // Cleanup
    vi.clearAllMocks();
    
    // Test with "Overloaded" status (load > 0.8)
    SchedulerService.getQueueStatus.mockResolvedValue({
      ...mockQueueStatus,
      system_load: 0.9
    });
    
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Overloaded')).toBeInTheDocument();
    });
  });

  it('should refresh data when refresh button is clicked', async () => {
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(SchedulerService.getQueueStatus).toHaveBeenCalledTimes(1);
    });
    
    // Click refresh button
    fireEvent.click(screen.getByText('Refresh'));
    
    await waitFor(() => {
      expect(SchedulerService.getQueueStatus).toHaveBeenCalledTimes(2);
    });
  });

  it('should call onRefresh callback when data is refreshed', async () => {
    const onRefreshMock = vi.fn();
    render(<SchedulerMonitor onRefresh={onRefreshMock} />);
    
    await waitFor(() => {
      expect(SchedulerService.getQueueStatus).toHaveBeenCalledTimes(1);
      expect(onRefreshMock).toHaveBeenCalledTimes(1);
    });
    
    // Click refresh button
    fireEvent.click(screen.getByText('Refresh'));
    
    await waitFor(() => {
      expect(onRefreshMock).toHaveBeenCalledTimes(2);
    });
  });

  it('should display error message when API call fails', async () => {
    const errorMessage = 'Failed to fetch queue status';
    SchedulerService.getQueueStatus.mockRejectedValue(new Error(errorMessage));
    
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should display active jobs when they exist', async () => {
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('Active Jobs')).toBeInTheDocument();
      expect(screen.getByText('Genetic Algorithm')).toBeInTheDocument();
      expect(screen.getByText('Constraint Solver')).toBeInTheDocument();
      expect(screen.getByText('processing')).toBeInTheDocument();
      expect(screen.getByText('waiting')).toBeInTheDocument();
    });
  });

  it('should show progress bar for processing jobs', async () => {
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      // The processing job should have a progress bar
      expect(screen.getByText('65%')).toBeInTheDocument();
      // And it should have a progress bar element
      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars.length).toBeGreaterThan(1); // At least one for loading and one for job progress
    });
  });

  it('should display "No active jobs" message when there are no active jobs', async () => {
    SchedulerService.getQueueStatus.mockResolvedValue({
      ...mockQueueStatus,
      active_jobs: 0
    });
    
    render(<SchedulerMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText('No active jobs at the moment')).toBeInTheDocument();
    });
  });
});
