import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  Stack,
} from '@mui/material';
import {
  Home,
  Article,
  Psychology,
  AccessTime,
  ArrowForward,
  FolderOpen,
} from '@mui/icons-material';
import { getRecentResults } from '../services/api';

function ResultsPage() {
  const navigate = useNavigate();

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    fetchResults();
  }, []);


  const fetchResults = async () => {
    try {
      setLoading(true);
      const data = await getRecentResults();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      setError('Failed to load assessments.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Recent';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };


  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" elevation={0}>
        <Container maxWidth="lg">
          <Toolbar sx={{ py: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{ bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 2, p: 0.8, display: 'flex' }}>
                <Psychology sx={{ fontSize: 24 }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Report History
              </Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Button color="inherit" startIcon={<Home />} onClick={() => navigate('/')} sx={{ fontWeight: 500 }}>
              Home
            </Button>
          </Toolbar>
        </Container>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Your Wellness Reports
          </Typography>
          <Typography color="text.secondary">
            View and access your previous wellness assessment reports
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}>
            <CircularProgress size={48} />
          </Box>
        ) : results.length === 0 ? (
          <Paper
            elevation={0}
            sx={{
              p: 6,
              textAlign: 'center',
              borderRadius: 4,
              border: '2px dashed',
              borderColor: 'divider',
              bgcolor: 'white',
            }}
          >
            <FolderOpen sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
              No assessments yet
            </Typography>
            <Typography variant="body2" color="text.disabled" sx={{ mb: 3 }}>
              Start a new wellness session to see your reports here
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/session')}
              endIcon={<ArrowForward />}
            >
              Start Session
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {results.map((result, index) => {
              const segments = Array.isArray(result.wellness_metrics) 
                ? result.wellness_metrics.length 
                : (result.raw_data?.length || 0);
              
              return (
                <Grid item xs={12} md={6} key={result.id || index}>
                  <Card
                    elevation={0}
                    sx={{
                      borderRadius: 3,
                      border: '1px solid',
                      borderColor: 'divider',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        boxShadow: '0 8px 30px -10px rgba(79, 70, 229, 0.2)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    <CardActionArea onClick={() => navigate(`/report/${result.id}`)}>
                      <CardContent sx={{ p: 3 }}>
                        <Stack direction="row" alignItems="flex-start" justifyContent="space-between" mb={2}>
                          <Box
                            sx={{
                              bgcolor: 'primary.main',
                              borderRadius: 2,
                              p: 1.5,
                              display: 'flex',
                            }}
                          >
                            <Article sx={{ color: 'white', fontSize: 24 }} />
                          </Box>
                          <Chip
                            label={`${segments} segments`}
                            size="small"
                            sx={{
                              bgcolor: segments > 2 ? '#e0e7ff' : '#f1f5f9',
                              color: segments > 2 ? '#4338ca' : '#64748b',
                              fontWeight: 600,
                            }}
                          />
                        </Stack>

                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                          Wellness Report
                        </Typography>
                        <Typography variant="caption" color="text.disabled" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 2 }}>
                          <AccessTime sx={{ fontSize: 14 }} />
                          {formatDate(result.created_at)}
                        </Typography>

                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            lineHeight: 1.6,
                          }}
                        >
                          {result.report_text?.substring(0, 200) || 'Wellness insights generated from multimodal behavioral analysis.'}
                        </Typography>

                        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                          <Typography
                            variant="body2"
                            sx={{
                              color: 'primary.main',
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'center',
                              gap: 0.5,
                            }}
                          >
                            View Report <ArrowForward sx={{ fontSize: 16 }} />
                          </Typography>
                        </Box>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
      </Container>
    </Box>
  );
}

export default ResultsPage;
