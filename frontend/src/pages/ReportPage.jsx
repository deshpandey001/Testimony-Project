import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
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
  Divider,
  Chip,
  Card,
  CardContent,
  Grid,
  Stack,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Home,
  Article,
  GetApp,
  Print,
  Psychology,
  CheckCircle,
  Info,
  AccessTime,
  RecordVoiceOver,
  Warning,
  Analytics,
  Timeline,
  Insights,
} from '@mui/icons-material';
import { getAnalysisById } from '../services/api';
import {
  WellnessGauge,
  StressMapChart,
  EmotionalTrendChart,
  ConsistencyPanel,
} from '../components';

function ReportPage() {
  const params = useParams();
  const itemId = params.report_id || params.itemId || params.id;
  const location = useLocation();

  const navigate = useNavigate();

  const [report, setReport] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);


  useEffect(() => {
    if (location.state?.report_text) {
      setReport({
        session_id: itemId,
        report_text: location.state.report_text,
        raw_data: location.state.raw_data,
        created_at: new Date().toISOString(),
      });
      // Set analytics if available from navigation state
      if (location.state?.analytics) {
        setAnalytics(location.state.analytics);
      }
      setLoading(false);
    } else if (itemId && itemId !== 'null') {
      fetchReport(itemId);
    } else {
      setLoading(false);
      setError('No report data available.');
    }
  }, [itemId, location.state]);


  const fetchReport = async (id) => {
    try {
      setLoading(true);
      const data = await getAnalysisById(id);
      setReport(data || null);
    } catch (err) {
      console.error(err);
      setError('Failed to load insights from database.');
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `wellness-report-${itemId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Just now';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getAlertIcon = (type) => {
    if (type?.toLowerCase().includes('stable') || type?.toLowerCase().includes('fluent')) {
      return <CheckCircle sx={{ color: '#10b981', fontSize: 20 }} />;
    }
    return <Warning sx={{ color: '#f59e0b', fontSize: 20 }} />;
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
                Wellness Report
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
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
            <CircularProgress size={48} />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ borderRadius: 2 }}>{error}</Alert>
        ) : !report ? (
          <Alert severity="info" sx={{ borderRadius: 2 }}>No insights found for this session.</Alert>
        ) : (
          <Grid container spacing={3}>
            {/* Main Report */}
            <Grid item xs={12} lg={8}>
              <Card elevation={0} sx={{ borderRadius: 4, border: '1px solid', borderColor: 'divider', mb: 3 }}>
                <Box
                  sx={{
                    background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #818cf8 100%)',
                    p: 4,
                    color: 'white',
                  }}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                        Communication & Wellness Summary
                      </Typography>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <AccessTime sx={{ fontSize: 16, opacity: 0.8 }} />
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          {formatDate(report.created_at)}
                        </Typography>
                      </Stack>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<GetApp />}
                        onClick={downloadJSON}
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.2)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                          boxShadow: 'none',
                        }}
                      >
                        Export
                      </Button>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Print />}
                        onClick={() => window.print()}
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.2)',
                          '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                          boxShadow: 'none',
                        }}
                      >
                        Print
                      </Button>
                    </Stack>
                  </Stack>
                </Box>

                <CardContent sx={{ p: 4 }}>
                  {/* Tabs for switching views */}
                  <Tabs
                    value={activeTab}
                    onChange={(e, val) => setActiveTab(val)}
                    sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
                  >
                    <Tab
                      icon={<Article sx={{ fontSize: 18 }} />}
                      iconPosition="start"
                      label="AI Insights"
                      sx={{ fontWeight: 600, minHeight: 48 }}
                    />
                    <Tab
                      icon={<Analytics sx={{ fontSize: 18 }} />}
                      iconPosition="start"
                      label="Research Analytics"
                      sx={{ fontWeight: 600, minHeight: 48 }}
                    />
                  </Tabs>

                  {/* Tab Content */}
                  {activeTab === 0 && (
                    <>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Insights sx={{ color: 'primary.main' }} />
                        AI-Generated Insights
                      </Typography>
                      <Paper
                        elevation={0}
                        sx={{
                          p: 3,
                          borderRadius: 3,
                          bgcolor: '#f8fafc',
                          border: '1px solid',
                          borderColor: 'divider',
                        }}
                      >
                        <Typography
                          sx={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.8,
                            color: 'text.primary',
                            fontSize: '0.95rem',
                          }}
                        >
                          {report.report_text || 'No insights available.'}
                        </Typography>
                      </Paper>
                    </>
                  )}

                  {activeTab === 1 && (
                    <Stack spacing={3}>
                      <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Timeline sx={{ color: 'primary.main' }} />
                        Research-Grade Analytics
                      </Typography>

                      {analytics ? (
                        <Grid container spacing={3}>
                          {/* Wellness Gauge */}
                          <Grid item xs={12} md={6}>
                            <WellnessGauge
                              score={analytics.wellness?.score}
                              interpretation={analytics.wellness?.interpretation}
                            />
                          </Grid>

                          {/* Consistency Panel */}
                          <Grid item xs={12} md={6}>
                            <ConsistencyPanel inconsistencies={analytics.inconsistencies} />
                          </Grid>

                          {/* Stress Map */}
                          <Grid item xs={12}>
                            <StressMapChart
                              stressMap={analytics.stress_map}
                              peakStressQuestion={analytics.peak_stress_question}
                              stressTrend={analytics.stress_trend}
                            />
                          </Grid>

                          {/* Emotional Timeline */}
                          <Grid item xs={12}>
                            <EmotionalTrendChart timeline={analytics.emotional_timeline} />
                          </Grid>
                        </Grid>
                      ) : (
                        <Paper
                          elevation={0}
                          sx={{
                            p: 4,
                            borderRadius: 3,
                            bgcolor: '#f8fafc',
                            textAlign: 'center',
                            border: '1px solid',
                            borderColor: 'divider',
                          }}
                        >
                          <Analytics sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                          <Typography color="text.secondary">
                            Analytics data not available for this session.
                          </Typography>
                          <Typography variant="caption" color="text.disabled">
                            Complete a new assessment to see research-grade analytics.
                          </Typography>
                        </Paper>
                      )}
                    </Stack>
                  )}
                </CardContent>
              </Card>

              {/* Disclaimer */}
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 3,
                  bgcolor: '#eff6ff',
                  border: '1px solid #bfdbfe',
                }}
              >
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <Info sx={{ color: '#3b82f6', mt: 0.3 }} />
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e40af', mb: 0.5 }}>
                      Important Notice
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#1e3a8a' }}>
                      This report provides supportive behavioral insights for communication improvement
                      and psychological wellness research. It is not intended for diagnostic or
                      forensic decision-making.
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} lg={4}>
              {/* Session Info Card */}
              <Card elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider', mb: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
                    SESSION DETAILS
                  </Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="caption" color="text.disabled">Assessment ID</Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {itemId?.slice(0, 20)}...
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.disabled">Segments Analyzed</Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {Array.isArray(report.raw_data) ? report.raw_data.length : 0} responses
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>

              {/* Signals Card */}
              {report.raw_data && Array.isArray(report.raw_data) && report.raw_data.length > 0 && (
                <Card elevation={0} sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
                      OBSERVED SIGNALS
                    </Typography>
                    <Stack spacing={2}>
                      {report.raw_data.map((item, i) => (
                        <Paper
                          key={i}
                          elevation={0}
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            bgcolor: '#f8fafc',
                            border: '1px solid',
                            borderColor: 'divider',
                          }}
                        >
                          <Stack direction="row" alignItems="center" spacing={1} mb={1}>
                            <RecordVoiceOver sx={{ fontSize: 18, color: 'primary.main' }} />
                            <Typography variant="subtitle2" fontWeight={600}>
                              Response {i + 1}
                            </Typography>
                          </Stack>
                          {item.transcription && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                              "{item.transcription.slice(0, 80)}{item.transcription.length > 80 ? '...' : ''}"
                            </Typography>
                          )}
                          {item.alerts && item.alerts.length > 0 && (
                            <Stack spacing={0.5}>
                              {item.alerts.slice(0, 3).map((alert, j) => (
                                <Stack key={j} direction="row" alignItems="center" spacing={1}>
                                  {getAlertIcon(alert.type)}
                                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                    {alert.type}
                                  </Typography>
                                </Stack>
                              ))}
                            </Stack>
                          )}
                        </Paper>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              )}
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
}

export default ReportPage;
