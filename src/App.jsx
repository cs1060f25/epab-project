import { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Box,
  AppBar,
  Toolbar,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Security
} from '@mui/icons-material';
import { mockAlerts } from './mockData';
import './App.css';

function App() {
  const [alerts, setAlerts] = useState(mockAlerts);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <Error />;
      case 'high': return <Warning />;
      case 'medium': return <Info />;
      case 'low': return <CheckCircle />;
      default: return <Info />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'error';
      case 'investigating': return 'warning';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    const severityMatch = severityFilter === 'all' || alert.severity === severityFilter;
    const statusMatch = statusFilter === 'all' || alert.status === statusFilter;
    return severityMatch && statusMatch;
  });

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Security sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Unified Security Alert Dashboard
          </Typography>
          <Typography variant="body2">
            Alex (SOC Analyst)
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Correlated Security Incidents
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Showing {filteredAlerts.length} incidents from multiple data sources (IdP, EDR, Payments, Email)
          </Typography>
        </Box>

        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              value={severityFilter}
              label="Severity"
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="new">New</MenuItem>
              <MenuItem value="investigating">Investigating</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
            </Select>
          </FormControl>
        </Stack>

        <Grid container spacing={3}>
          {filteredAlerts.map((alert) => (
            <Grid item xs={12} md={6} key={alert.id}>
              <Card elevation={3}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ mr: 1 }}>
                      {getSeverityIcon(alert.severity)}
                    </Box>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                      {alert.title}
                    </Typography>
                    <Chip
                      label={alert.severity.toUpperCase()}
                      color={getSeverityColor(alert.severity)}
                      size="small"
                    />
                  </Box>

                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Chip
                      label={alert.status.toUpperCase()}
                      color={getStatusColor(alert.status)}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={`${alert.signalCount} signals`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={`Confidence: ${(alert.confidence * 100).toFixed(0)}%`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Stack>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>ID:</strong> {alert.id} | <strong>User:</strong> {alert.user}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Time:</strong> {new Date(alert.timestamp).toLocaleString()}
                  </Typography>

                  <Typography variant="body2" sx={{ mt: 2, mb: 1 }}>
                    <strong>Signals Detected:</strong>
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {alert.signals.map((signal, idx) => (
                      <li key={idx}>
                        <Typography variant="body2">{signal}</Typography>
                      </li>
                    ))}
                  </ul>

                  <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
                    {alert.description}
                  </Typography>
                </CardContent>

                <CardActions>
                  <Button size="small" color="primary" variant="contained">
                    Investigate
                  </Button>
                  <Button size="small" color="error">
                    Escalate
                  </Button>
                  <Button size="small">
                    Dismiss
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </>
  );
}

export default App;
