import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  Paper,
} from '@mui/material';
import { Psychology, Assessment } from '@mui/icons-material';

function HomePage() {
  const navigate = useNavigate();

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Psychology sx={{ mr: 2 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Student Psychological Wellness Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md">
        <Box sx={{ mt: 8, mb: 4 }}>
          <Typography variant="h3" align="center" gutterBottom>
            Communication & Wellness Insights
          </Typography>

          <Typography variant="h6" align="center" color="text.secondary">
            AI-assisted analysis of speech, facial cues, and engagement patterns
          </Typography>
        </Box>

        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
          <Typography paragraph>
            This platform supports psychological wellness research for students
            and professionals by analyzing communication behavior during guided
            conversations.
          </Typography>

          <Typography paragraph>
            Using multimodal AI, the system evaluates:
          </Typography>

          <ul>
            <li>Facial engagement & eye contact</li>
            <li>Speech fluency & pause patterns</li>
            <li>Vocal energy & emotional tone</li>
            <li>Confidence and stress indicators</li>
          </ul>

          <Typography>
            The goal is to provide supportive, non-judgmental insights that help
            improve communication skills, emotional well-being, and self-awareness.
          </Typography>
        </Paper>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<Psychology />}
            onClick={() => navigate('/session')}
          >
            Start Wellness Session
          </Button>

          <Button
            variant="outlined"
            size="large"
            startIcon={<Assessment />}
            onClick={() => navigate('/results')}
          >
            View Past Reports
          </Button>
        </Box>
      </Container>
    </>
  );
}

export default HomePage;
