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
  LinearProgress,
} from '@mui/material';
import { FiberManualRecord, Stop, Send, Home } from '@mui/icons-material';
import { uploadRecording, generateReport } from '../services/api';


/* =========================================
   Wellness / Communication prompts
   ========================================= */

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


  /* ================= CAMERA ================= */

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
    } catch {
      setError('Camera/Microphone permission denied.');
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
  };


  /* ================= RECORDING ================= */

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


  /* ================= PROCESS ================= */

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
      setError('Upload failed.');
    } finally {
      setIsProcessing(false);
    }
  };


  const handleGenerateReport = async () => {
    setIsProcessing(true);
    const data = await generateReport(results);
    navigate(`/report/${data.report_id}`);
  };


  /* ================= UI ================= */

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography sx={{ flexGrow: 1 }}>
            Wellness Reflection Session
          </Typography>
          <Button color="inherit" startIcon={<Home />} onClick={() => navigate('/')}>
            Home
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md">
        <Box sx={{ mt: 4 }}>

          {error && <Alert severity="error">{error}</Alert>}

          <Paper sx={{ p: 3 }}>

            <Typography variant="h6">
              Prompt {currentQuestion + 1} / {QUESTIONS.length}
            </Typography>

            <LinearProgress
              variant="determinate"
              value={(results.length / QUESTIONS.length) * 100}
              sx={{ my: 2 }}
            />

            <Typography variant="h5" sx={{ mb: 3 }}>
              {QUESTIONS[currentQuestion]}
            </Typography>


            <video
              ref={videoRef}
              autoPlay
              muted
              style={{ width: '100%', borderRadius: 8 }}
            />


            {isProcessing ? (
              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <CircularProgress />
                <Typography>Analyzing wellness signals...</Typography>
              </Box>
            ) : sessionComplete ? (
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={handleGenerateReport}
              >
                Generate Wellness Insights
              </Button>
            ) : !isRecording ? (
              <Button
                variant="contained"
                color="error"
                startIcon={<FiberManualRecord />}
                onClick={startRecording}
              >
                Start Recording
              </Button>
            ) : (
              <Button
                variant="contained"
                startIcon={<Stop />}
                onClick={stopRecording}
              >
                Stop
              </Button>
            )}

          </Paper>
        </Box>
      </Container>
    </>
  );
}

export default NewSessionPage;
