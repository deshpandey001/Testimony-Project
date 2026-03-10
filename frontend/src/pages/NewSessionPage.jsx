import { useState, useRef, useEffect } from 'react';
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
  Stack,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  FiberManualRecord,
  Stop,
  Send,
  Home,
  Psychology,
  Videocam,
  RadioButtonChecked,
} from '@mui/icons-material';
import { uploadRecording, generateReport } from '../services/api';


const QUESTIONS = [
  "Please introduce yourself and share something about your interests or studies.",
  "Describe a recent situation that made you feel stressed or challenged.",
  "How do you usually cope with pressure or difficult situations?"
];


function NewSessionPage() {
  const navigate = useNavigate();

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [sessionComplete, setSessionComplete] = useState(false);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const videoRef = useRef(null);


  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);


  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch {
      setError('Camera/Microphone permission denied. Please allow access to continue.');
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
  };


  const startRecording = () => {
    chunksRef.current = [];
    const recorder = new MediaRecorder(streamRef.current, {
      mimeType: 'video/webm;codecs=vp8,opus',
    });
    recorder.ondataavailable = e => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      await processRecording(blob);
    };
    recorder.start();
    mediaRecorderRef.current = recorder;
    setIsRecording(true);
    setRecordingTime(0);
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    clearInterval(timerRef.current);
  };

  const processRecording = async (blob) => {
    setIsProcessing(true);
    try {
      const result = await uploadRecording(currentQuestion + 1, blob);
      setResults(prev => [...prev, result]);
      if (currentQuestion < QUESTIONS.length - 1) {
        setCurrentQuestion(prev => prev + 1);
      } else {
        setSessionComplete(true);
      }
    } catch {
      setError('Upload failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGenerateReport = async () => {
    setIsProcessing(true);
    try {
      const data = await generateReport(results);
      navigate(`/report/${data.report_id}`, {
        state: {
          report_text: data.report,
          raw_data: data.raw_data || results,
          session_id: data.report_id,
          analytics: data.analytics || null,  // Include analytics data
        }
      });
    } catch (err) {
      setError('Failed to generate report.');
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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
                Wellness Session
              </Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Button color="inherit" startIcon={<Home />} onClick={() => navigate('/')} sx={{ fontWeight: 500 }}>
              Home
            </Button>
          </Toolbar>
        </Container>
      </AppBar>

      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider', bgcolor: 'white' }}>
          <Stepper activeStep={results.length} alternativeLabel>
            {QUESTIONS.map((_, index) => (
              <Step key={index} completed={index < results.length}>
                <StepLabel>
                  <Typography variant="caption" fontWeight={500}>Prompt {index + 1}</Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Card elevation={0} sx={{ borderRadius: 4, border: '1px solid', borderColor: 'divider', overflow: 'hidden' }}>
          <Box sx={{ background: 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)', p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Stack direction="row" alignItems="center" spacing={1} mb={1.5}>
              <Chip label={`Question ${currentQuestion + 1} of ${QUESTIONS.length}`} size="small" sx={{ bgcolor: 'primary.main', color: 'white', fontWeight: 600 }} />
              {isRecording && (
                <Chip
                  icon={<RadioButtonChecked sx={{ fontSize: 14, color: '#ef4444 !important' }} />}
                  label={formatTime(recordingTime)}
                  size="small"
                  sx={{ bgcolor: '#fef2f2', color: '#ef4444', fontWeight: 600 }}
                />
              )}
            </Stack>
            <Typography variant="h5" sx={{ fontWeight: 600, color: 'text.primary' }}>
              {QUESTIONS[currentQuestion]}
            </Typography>
          </Box>

          <CardContent sx={{ p: 3 }}>
            <Box sx={{ position: 'relative', borderRadius: 3, overflow: 'hidden', bgcolor: '#1e293b', mb: 3 }}>
              <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', display: 'block', aspectRatio: '16/9', objectFit: 'cover' }} />
              {isRecording && (
                <Box sx={{ position: 'absolute', top: 16, left: 16, display: 'flex', alignItems: 'center', gap: 1, bgcolor: 'rgba(239, 68, 68, 0.9)', color: 'white', px: 2, py: 0.75, borderRadius: 2 }}>
                  <FiberManualRecord sx={{ fontSize: 12, animation: 'pulse 1s infinite' }} />
                  <Typography variant="body2" fontWeight={600}>Recording</Typography>
                </Box>
              )}
              <Box sx={{ position: 'absolute', bottom: 16, right: 16, bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 2, p: 1 }}>
                <Videocam sx={{ color: 'white', fontSize: 20 }} />
              </Box>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              {isProcessing ? (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <CircularProgress size={40} sx={{ mb: 2 }} />
                  <Typography color="text.secondary" fontWeight={500}>Analyzing wellness signals...</Typography>
                </Box>
              ) : sessionComplete ? (
                <Button variant="contained" size="large" startIcon={<Send />} onClick={handleGenerateReport} sx={{ py: 1.5, px: 4 }}>
                  Generate Wellness Insights
                </Button>
              ) : !isRecording ? (
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<FiberManualRecord />}
                  onClick={startRecording}
                  sx={{ py: 1.5, px: 4, background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', '&:hover': { background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)', boxShadow: '0 4px 12px rgba(239, 68, 68, 0.4)' } }}
                >
                  Start Recording
                </Button>
              ) : (
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<Stop />}
                  onClick={stopRecording}
                  sx={{ py: 1.5, px: 4, background: 'linear-gradient(135deg, #64748b 0%, #475569 100%)', '&:hover': { background: 'linear-gradient(135deg, #475569 0%, #334155 100%)' } }}
                >
                  Stop Recording
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>

        <Paper elevation={0} sx={{ mt: 3, p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider', bgcolor: '#f0fdf4' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#166534', mb: 1 }}>
            💡 Tips for best results
          </Typography>
          <Typography variant="body2" sx={{ color: '#15803d' }}>
            Speak naturally and clearly. Ensure good lighting on your face. Take your time to think before responding.
          </Typography>
        </Paper>
      </Container>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </Box>
  );
}

export default NewSessionPage;
