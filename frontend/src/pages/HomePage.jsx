import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
} from '@mui/material';
import {
  Psychology,
  Assessment,
  Face,
  RecordVoiceOver,
  GraphicEq,
  TrendingUp,
  ArrowForward,
  Shield,
  AutoAwesome,
} from '@mui/icons-material';

const features = [
  {
    icon: <Face sx={{ fontSize: 40 }} />,
    title: 'Facial Analysis',
    description: 'Track eye contact, engagement levels, and micro-expressions',
    color: '#4f46e5',
  },
  {
    icon: <RecordVoiceOver sx={{ fontSize: 40 }} />,
    title: 'Speech Patterns',
    description: 'Analyze fluency, pauses, and filler words in real-time',
    color: '#06b6d4',
  },
  {
    icon: <GraphicEq sx={{ fontSize: 40 }} />,
    title: 'Vocal Energy',
    description: 'Measure pitch variation, tone, and emotional expression',
    color: '#10b981',
  },
  {
    icon: <TrendingUp sx={{ fontSize: 40 }} />,
    title: 'Confidence Metrics',
    description: 'Comprehensive wellness and stress indicator tracking',
    color: '#f59e0b',
  },
];

function HomePage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: '100vh', width: '100%', bgcolor: 'background.default' }}>
      {/* AppBar */}
      <AppBar position="static" elevation={0}>
        <Container maxWidth="lg">
          <Toolbar sx={{ py: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  borderRadius: 2,
                  p: 0.8,
                  display: 'flex',
                }}
              >
                <Psychology sx={{ fontSize: 28 }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600, letterSpacing: '-0.01em' }}>
                MindSense AI
              </Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Chip
              icon={<Shield sx={{ fontSize: 16 }} />}
              label="Privacy First"
              size="small"
              sx={{
                bgcolor: 'rgba(255,255,255,0.15)',
                color: 'white',
                fontWeight: 500,
                '& .MuiChip-icon': { color: 'white' },
              }}
            />
          </Toolbar>
        </Container>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(180deg, rgba(79, 70, 229, 0.05) 0%, rgba(255,255,255,0) 100%)',
          pt: { xs: 6, md: 10 },
          pb: { xs: 8, md: 12 },
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 800, mx: 'auto' }}>
            <Chip
              icon={<AutoAwesome sx={{ fontSize: 16 }} />}
              label="AI-Powered Analysis"
              sx={{
                mb: 3,
                bgcolor: 'primary.main',
                color: 'white',
                fontWeight: 500,
                px: 1,
                '& .MuiChip-icon': { color: 'white' },
              }}
            />
            
            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '2.2rem', md: '3.2rem' },
                fontWeight: 700,
                color: 'text.primary',
                mb: 2,
                lineHeight: 1.2,
              }}
            >
              Communication &{' '}
              <Box
                component="span"
                sx={{
                  background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Wellness Insights
              </Box>
            </Typography>

            <Typography
              variant="h6"
              sx={{
                color: 'text.secondary',
                fontWeight: 400,
                mb: 5,
                fontSize: { xs: '1rem', md: '1.15rem' },
                lineHeight: 1.7,
              }}
            >
              Unlock deeper understanding of your communication patterns with AI-assisted
              analysis of speech, facial cues, and engagement indicators.
            </Typography>

            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                variant="contained"
                size="large"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/session')}
                sx={{
                  py: 1.5,
                  px: 4,
                  fontSize: '1rem',
                }}
              >
                Start Wellness Session
              </Button>

              <Button
                variant="outlined"
                size="large"
                startIcon={<Assessment />}
                onClick={() => navigate('/results')}
                sx={{
                  py: 1.5,
                  px: 4,
                  fontSize: '1rem',
                }}
              >
                View Past Reports
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1.5 }}>
            Multimodal AI Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Our platform combines multiple AI technologies to provide comprehensive,
            supportive wellness insights.
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 20px 40px -15px rgba(0,0,0,0.15)',
                    borderColor: feature.color,
                  },
                }}
              >
                <CardContent sx={{ p: 3, textAlign: 'center' }}>
                  <Box
                    sx={{
                      width: 72,
                      height: 72,
                      borderRadius: 3,
                      bgcolor: `${feature.color}15`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2.5,
                      color: feature.color,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Info Section */}
      <Box sx={{ bgcolor: 'white', py: { xs: 6, md: 8 } }}>
        <Container maxWidth="md">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3, md: 5 },
              borderRadius: 4,
              border: '1px solid',
              borderColor: 'divider',
              background: 'linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%)',
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
              How It Works
            </Typography>
            
            <Grid container spacing={4}>
              {[
                { step: '1', title: 'Record', desc: 'Answer guided prompts while we capture audio and video' },
                { step: '2', title: 'Analyze', desc: 'AI processes facial, vocal, and speech patterns' },
                { step: '3', title: 'Insights', desc: 'Receive a detailed wellness report with actionable feedback' },
              ].map((item, i) => (
                <Grid item xs={12} md={4} key={i}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: '50%',
                        bgcolor: 'primary.main',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 2,
                        fontWeight: 700,
                        fontSize: '1.2rem',
                      }}
                    >
                      {item.step}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {item.desc}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ py: 4, textAlign: 'center', borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary">
          © 2026 MindSense AI · Student Psychological Wellness Platform
        </Typography>
      </Box>
    </Box>
  );
}

export default HomePage;
