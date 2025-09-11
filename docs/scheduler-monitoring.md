# Scheduler Monitoring System

This document provides an overview of the scheduler monitoring system implemented in the Project Intelligencia Scheduler application.

## Overview

The scheduler monitoring system provides real-time visibility into the state of the timetable generation process, including active jobs, queue status, and system health metrics. This enables administrators to track the progress of scheduling jobs and manage system resources effectively.

## Components

### 1. SchedulerMonitor Component

The `SchedulerMonitor` component (`/frontend/src/components/SchedulerMonitor.tsx`) is a reusable React component that displays:

- System status with visual indicators (normal, busy, overloaded)
- Queue statistics (active jobs, queue size, worker count)
- System load percentage
- List of active scheduling jobs with progress indicators

Features:
- Auto-refresh functionality (every 30 seconds)
- Manual refresh via a refresh button
- Visual status indicators using color-coded chips
- Progress tracking for active jobs

### 2. Dashboard Integration

The Dashboard (`/frontend/src/pages/Dashboard.tsx`) incorporates the SchedulerMonitor component to provide system-wide visibility into:

- Overall statistics (departments, faculty, subjects, batches, classrooms)
- Scheduler system status
- Recent schedule generations

The integration creates a seamless monitoring experience where updates to the scheduler status also refresh the list of recent schedule generations.

## API Integration

The monitoring system relies on the following API endpoints through the SchedulerService:

- `getQueueStatus()`: Retrieves current queue metrics
- `listScheduleGenerations(offset, limit)`: Lists recently generated schedules

## Scheduler Status States

The system monitors the following states:

1. **Normal** (Green): System load < 50%
2. **Busy** (Yellow): System load between 50% and 80%
3. **Overloaded** (Red): System load > 80%

## Job Status Types

Individual jobs can have the following statuses:

- **Completed**: Job has successfully finished
- **Processing**: Job is currently running
- **Waiting**: Job is in queue waiting to be processed
- **Failed**: Job encountered an error during processing

## Usage

Administrators can use the monitoring system to:

1. Monitor the health of the scheduling system
2. Track the progress of ongoing schedule generations
3. View details of recent schedules
4. Cancel in-progress jobs if needed
5. Identify system bottlenecks during peak usage periods

## Future Enhancements

Potential improvements to the monitoring system:

1. Detailed job analytics and historical performance metrics
2. Email/notification alerts for failed jobs or system overload
3. Resource usage optimization recommendations
4. Scheduling job prioritization controls
5. Detailed error logging and troubleshooting tools
