import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import HomePage from './pages/HomePage';
import NewSessionPage from './pages/NewSessionPage';
import ResultsPage from './pages/ResultsPage';
import ReportPage from './pages/ReportPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/session" element={<NewSessionPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/report/:report_id" element={<ReportPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
