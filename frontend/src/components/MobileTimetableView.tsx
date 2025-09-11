import React from 'react';
import { Box, Typography, Card, CardContent, Chip, Divider, Stack } from '@mui/material';
import type { ScheduledSession } from '../types/scheduledSession';

interface MobileTimetableViewProps {
  sessions: ScheduledSession[];
  selectedDay: number | 'all';
  daysOfWeek: string[];
  formatTime: (time: string) => string;
  getSessionChipColor: (sessionType: string) => "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning";
  selectedView: 'batch' | 'faculty' | 'classroom';
}

const MobileTimetableView: React.FC<MobileTimetableViewProps> = ({
  sessions,
  selectedDay,
  daysOfWeek,
  formatTime,
  getSessionChipColor,
  selectedView
}) => {
  // Group sessions by day
  const sessionsByDay = React.useMemo(() => {
    const grouped: Record<string, ScheduledSession[]> = {};
    
    // If a specific day is selected, only show that day
    const daysToShow = selectedDay === 'all' 
      ? daysOfWeek
      : [daysOfWeek[selectedDay as number]];
      
    daysToShow.forEach(day => {
      grouped[day] = [];
    });
    
    // Group sessions by day and sort by time
    sessions.forEach(session => {
      const day = daysOfWeek[session.day_of_week];
      if (grouped[day]) {
        grouped[day].push(session);
      }
    });
    
    // Sort sessions by start time
    Object.keys(grouped).forEach(day => {
      grouped[day].sort((a, b) => {
        return a.start_time.localeCompare(b.start_time);
      });
    });
    
    return grouped;
  }, [sessions, selectedDay, daysOfWeek]);

  // If no sessions, show empty state
  if (Object.values(sessionsByDay).flat().length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary">
          No scheduled sessions found matching your filters.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      {Object.keys(sessionsByDay).map(day => (
        <Box key={day} sx={{ mb: 3 }}>
          {selectedDay === 'all' && (
            <Typography variant="h6" component="h2" sx={{ mb: 1, fontWeight: 'bold', borderBottom: '2px solid', borderColor: 'primary.main', pb: 0.5 }}>
              {day}
            </Typography>
          )}
          
          <Stack spacing={2}>
            {sessionsByDay[day].map(session => (
              <Card key={session.id} variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" component="h3">
                      {session.subject_name}
                    </Typography>
                    <Chip
                      label={session.session_type}
                      size="small"
                      color={getSessionChipColor(session.session_type)}
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {session.subject_code}
                  </Typography>
                  
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    backgroundColor: 'action.hover', 
                    borderRadius: 1,
                    px: 2, 
                    py: 1,
                    mb: 2
                  }}>
                    <Typography variant="body2" fontWeight="medium">
                      {formatTime(session.start_time)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      to
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {formatTime(session.end_time)}
                    </Typography>
                  </Box>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Stack spacing={1}>
                    {selectedView !== 'faculty' && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          Faculty
                        </Typography>
                        <Typography variant="body2">
                          {session.faculty_name}
                        </Typography>
                      </Box>
                    )}
                    
                    {selectedView !== 'batch' && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          Batch
                        </Typography>
                        <Typography variant="body2">
                          {session.batch_name}
                        </Typography>
                      </Box>
                    )}
                    
                    {selectedView !== 'classroom' && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">
                          Classroom
                        </Typography>
                        <Typography variant="body2">
                          {session.classroom_name}
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>
      ))}
    </Box>
  );
};

export default MobileTimetableView;
