import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { Home, Article } from '@mui/icons-material';
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

      // backend returns { results: [...] }
      setResults(data.results || []);

    } catch (err) {
      console.error(err);
      setError('Failed to load assessments.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <>
      {/* ================= APP BAR ================= */}

      <AppBar position="static">
        <Toolbar>
          <Typography sx={{ flexGrow: 1 }}>
            Wellness Insight History
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


      {/* ================= CONTENT ================= */}

      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}


          <Paper elevation={3} sx={{ p: 3 }}>

            <Typography variant="h5" gutterBottom>
              Recent Assessments
            </Typography>


            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : results.length === 0 ? (
              <Alert severity="info">
                No assessments found. Start a new wellness session to begin.
              </Alert>
            ) : (
              <List>

                {results.map((result) => {

                  const segments = (result.raw_data || []).length;

                  return (
                    <ListItem key={result.id} disablePadding>

                      <ListItemButton
                        onClick={() => navigate(`/report/${result.id}`)}
                        sx={{ py: 2 }}
                      >

                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Article />

                              <Typography variant="h6">
                                Insight Report {result.id?.slice(0, 8)}
                              </Typography>

                              <Chip
                                label={`${segments} segments`}
                                size="small"
                                color={segments > 2 ? 'primary' : 'default'}
                              />
                            </Box>
                          }

                          secondary={
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mt: 1 }}
                            >
                              {
                                result.report_text
                                  ? result.report_text.substring(0, 150)
                                  : "Wellness insights generated from multimodal signals"
                              }
                              {result.report_text?.length > 150 && '...'}
                            </Typography>
                          }
                        />

                      </ListItemButton>

                    </ListItem>
                  );
                })}

              </List>
            )}

          </Paper>
        </Box>
      </Container>
    </>
  );
}

export default ResultsPage;
