import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
} from '@mui/material';
import { Home, Article, GetApp } from '@mui/icons-material';
import { getAnalysisById } from '../services/api';

function ReportPage() {
  const params = useParams();
  const itemId = params.report_id || params.itemId || params.id;

  const navigate = useNavigate();

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    if (itemId) fetchReport(itemId);
  }, [itemId]);


  const fetchReport = async (id) => {
    try {
      setLoading(true);
      const data = await getAnalysisById(id);
      setReport(data || null);
    } catch (err) {
      console.error(err);
      setError('Failed to load insights.');
    } finally {
      setLoading(false);
    }
  };


  /* ================= Download JSON ================= */

  const downloadJSON = () => {
    if (!report) return;

    const blob = new Blob(
      [JSON.stringify(report, null, 2)],
      { type: 'application/json' }
    );

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    a.href = url;
    a.download = `wellness-report-${itemId}.json`;
    a.click();

    URL.revokeObjectURL(url);
  };


  const renderKeyValue = (label, value) => (
    <Box sx={{ mb: 1 }}>
      <Typography variant="subtitle2">{label}</Typography>
      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
        {value ?? '—'}
      </Typography>
    </Box>
  );


  /* ================= UI ================= */

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography sx={{ flexGrow: 1 }}>
            Wellness Insight Report
          </Typography>

          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => navigate('/')}
          >
            Home
          </Button>
        </Toolbar>
      </AppBar>


      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : !report ? (
            <Alert severity="info">No insights found for this session.</Alert>
          ) : (
            <Paper elevation={3} sx={{ p: 3 }}>

              {/* ================= Header ================= */}

              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 2
                }}
              >
                <Box>
                  <Typography variant="h5">
                    Communication & Wellness Summary
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Assessment ID: {itemId}
                  </Typography>
                </Box>

                <Box>
                  <Button
                    variant="outlined"
                    startIcon={<GetApp />}
                    onClick={downloadJSON}
                    sx={{ mr: 1 }}
                  >
                    Download Data
                  </Button>

                  <Button
                    variant="contained"
                    startIcon={<Article />}
                    onClick={() => window.print()}
                  >
                    Print
                  </Button>
                </Box>
              </Box>


              <Divider sx={{ my: 2 }} />


              {/* ================= Metadata ================= */}

              {renderKeyValue('Assessment ID', report.session_id)}
              {renderKeyValue(
                'Generated At',
                report.created_at || report.generated_at
              )}


              <Divider sx={{ my: 2 }} />


              {/* ================= Main Report ================= */}

              <Typography variant="h6" sx={{ mb: 1 }}>
                AI-Generated Wellness Insights
              </Typography>

              <Typography sx={{ whiteSpace: 'pre-wrap', mb: 3 }}>
                {report.report_text || 'No insights available.'}
              </Typography>


              {/* ================= Raw Signals ================= */}

              <Typography variant="h6" sx={{ mb: 1 }}>
                Observed Communication Signals
              </Typography>

              {report.raw_data ? (
                (Array.isArray(report.raw_data)
                  ? report.raw_data
                  : [report.raw_data]
                ).map((item, i) => (
                  <Paper key={i} variant="outlined" sx={{ p: 2, mb: 2 }}>
                    <Typography variant="subtitle1">
                      Segment {i + 1}
                    </Typography>

                    <pre style={{ whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(item, null, 2)}
                    </pre>
                  </Paper>
                ))
              ) : (
                <Typography variant="body2">
                  No signal data available.
                </Typography>
              )}


              <Divider sx={{ my: 2 }} />


              {/* ================= Disclaimer ================= */}

              <Typography variant="caption" color="text.secondary">
                This report provides supportive behavioral insights for
                communication improvement and psychological wellness research.
                It is not intended for diagnostic or forensic decision-making.
              </Typography>

            </Paper>
          )}
        </Box>
      </Container>
    </>
  );
}

export default ReportPage;
