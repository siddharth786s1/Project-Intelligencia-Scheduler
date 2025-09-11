# Responsive Design Guidelines for Timetable Scheduler

This document outlines the responsive design patterns and practices to ensure a consistent user experience across all devices.

## Breakpoints

We follow Material UI's default breakpoints:

| Breakpoint | Width     | Description         |
|------------|-----------|---------------------|
| xs         | < 600px   | Extra small (mobile)|
| sm         | ≥ 600px   | Small (tablet)      |
| md         | ≥ 960px   | Medium (laptop)     |
| lg         | ≥ 1280px  | Large (desktop)     |
| xl         | ≥ 1920px  | Extra large         |

## Core Principles

1. **Mobile-First Approach**
   - Design for mobile devices first, then progressively enhance for larger screens
   - Use the `sx` prop with responsive values for dynamic styling

2. **Flexible Grid System**
   - Use Material UI's Grid component with appropriate breakpoints
   - Implement container/item pattern for consistent spacing

3. **Responsive Typography**
   - Use the theme's responsive typography scales
   - Avoid fixed font sizes

4. **Touch-Friendly Interface**
   - Ensure all interactive elements are at least 48x48px on touch devices
   - Provide adequate spacing between clickable elements

5. **Adaptive Content Display**
   - Use conditional rendering to show/hide content based on screen size
   - Implement alternative layouts for complex components on mobile

## Implementation Patterns

### Responsive Grid Layout

```jsx
<Grid container spacing={{ xs: 1, sm: 2, md: 3 }}>
  <Grid item xs={12} sm={6} md={4} lg={3}>
    {/* Content that goes from full width on mobile to 3 columns on large screens */}
  </Grid>
</Grid>
```

### Responsive Typography

```jsx
<Typography 
  variant="h1"
  sx={{ 
    fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' } 
  }}
>
  Responsive Heading
</Typography>
```

### Adaptive Components

```jsx
<Box sx={{ display: { xs: 'block', md: 'flex' } }}>
  <Box sx={{ width: { xs: '100%', md: '50%' } }}>
    {/* First column */}
  </Box>
  <Box sx={{ 
    width: { xs: '100%', md: '50%' },
    mt: { xs: 2, md: 0 },
    ml: { xs: 0, md: 2 }
  }}>
    {/* Second column */}
  </Box>
</Box>
```

### Component-Specific Patterns

#### Navigation

- Use drawer navigation for mobile
- Use horizontal navigation for desktop
- Hide less important navigation items on smaller screens

```jsx
{/* Desktop Navigation */}
<Box sx={{ display: { xs: 'none', md: 'block' } }}>
  <Tabs value={activeTab} onChange={handleTabChange}>
    <Tab label="Dashboard" />
    <Tab label="Timetables" />
    {/* More tabs */}
  </Tabs>
</Box>

{/* Mobile Navigation */}
<Box sx={{ display: { xs: 'block', md: 'none' } }}>
  <IconButton onClick={toggleDrawer}>
    <MenuIcon />
  </IconButton>
  <Drawer open={drawerOpen} onClose={toggleDrawer}>
    {/* Drawer content */}
  </Drawer>
</Box>
```

#### Tables and Data Grids

- Use cards for mobile view of tabular data
- Show fewer columns on smaller screens
- Allow horizontal scrolling when necessary, but try to avoid it

```jsx
{/* Responsive Table */}
<TableContainer sx={{ overflowX: 'auto' }}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>Name</TableCell>
        <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Description</TableCell>
        <TableCell>Status</TableCell>
        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Created</TableCell>
        <TableCell>Actions</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {/* Table rows */}
    </TableBody>
  </Table>
</TableContainer>

{/* Alternative Card View for Mobile */}
<Box sx={{ display: { xs: 'block', sm: 'none' } }}>
  {data.map(item => (
    <Card key={item.id} sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6">{item.name}</Typography>
        <Typography variant="body2" color="text.secondary">Status: {item.status}</Typography>
        <Box sx={{ mt: 1 }}>
          <Button size="small">View</Button>
          <Button size="small">Edit</Button>
        </Box>
      </CardContent>
    </Card>
  ))}
</Box>
```

## Timetable Viewer-Specific Patterns

The timetable component presents unique challenges for responsive design:

1. **Time Grid View**
   - On desktop: Show full week with all time slots
   - On tablet: Show fewer days or collapse time slots
   - On mobile: Switch to a single day view with vertical orientation

2. **Filter Controls**
   - Desktop: Show all filters inline
   - Mobile: Use expandable accordion or dialog for filters

3. **Legend & Controls**
   - Stack controls vertically on mobile
   - Use iconography to save space

4. **Batch/Faculty/Room Switching**
   - Use full-width selects on mobile
   - Show more compact version on desktop

## Testing Responsive Design

1. Use Chrome DevTools device emulation
2. Test on actual devices when possible
3. Verify interactions work with touch input
4. Check loading states and performance on lower-end devices

## Accessibility Considerations

1. Ensure text meets contrast requirements at all sizes
2. Maintain proper focus states for keyboard navigation
3. Test with screen readers
4. Ensure touch targets are adequately sized
