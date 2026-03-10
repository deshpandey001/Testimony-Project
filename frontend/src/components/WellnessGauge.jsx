// =========================================================
// WELLNESS GAUGE COMPONENT
// Radial gauge displaying 0-100 wellness score
// =========================================================

import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const WellnessGauge = ({ score, interpretation }) => {
  // Default to 50 if no score
  const value = score ?? 50;
  
  // Color gradient based on score
  const getColor = (score) => {
    if (score >= 80) return '#4CAF50';  // Green - Excellent
    if (score >= 60) return '#8BC34A';  // Light green - Good
    if (score >= 40) return '#FFC107';  // Yellow - Moderate
    if (score >= 20) return '#FF9800';  // Orange - Low
    return '#F44336';                    // Red - Poor
  };

  const color = getColor(value);
  
  // Data for semi-circular gauge
  const data = [
    { name: 'Score', value: value },
    { name: 'Remaining', value: 100 - value }
  ];

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 4,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        textAlign: 'center'
      }}
    >
      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
        Wellness Index
      </Typography>

      <Box sx={{ position: 'relative', height: 180 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="80%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={0}
              dataKey="value"
            >
              <Cell fill={color} />
              <Cell fill="#e0e0e0" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Score display in center */}
        <Box
          sx={{
            position: 'absolute',
            top: '65%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center'
          }}
        >
          <Typography
            variant="h2"
            sx={{
              fontWeight: 700,
              color: color,
              lineHeight: 1
            }}
          >
            {Math.round(value)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            / 100
          </Typography>
        </Box>
      </Box>

      {/* Interpretation */}
      {interpretation && (
        <Box sx={{ mt: 2 }}>
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: color,
              textTransform: 'capitalize'
            }}
          >
            {interpretation.level || 'Unknown'}
          </Typography>
          {interpretation.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {interpretation.description}
            </Typography>
          )}
        </Box>
      )}

      {/* Breakdown indicators */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mt: 2 }}>
        <Box sx={{ textAlign: 'center' }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: '#4CAF50',
              mx: 'auto',
              mb: 0.5
            }}
          />
          <Typography variant="caption" color="text.secondary">
            80-100
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: '#FFC107',
              mx: 'auto',
              mb: 0.5
            }}
          />
          <Typography variant="caption" color="text.secondary">
            40-79
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: '#F44336',
              mx: 'auto',
              mb: 0.5
            }}
          />
          <Typography variant="caption" color="text.secondary">
            0-39
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default WellnessGauge;
