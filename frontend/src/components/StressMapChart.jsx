// =========================================================
// STRESS MAP CHART COMPONENT
// Bar chart showing stress levels per question
// =========================================================

import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from 'recharts';

const StressMapChart = ({ stressMap, peakStressQuestion, stressTrend }) => {
  // Default empty data
  const data = stressMap?.map((item, idx) => ({
    question: `Q${item.question_num || idx + 1}`,
    stress: (item.stress_score ?? 0) * 100,  // Convert 0-1 to 0-100
    rawScore: item.stress_score ?? 0
  })) || [];

  // Color based on stress level
  const getBarColor = (stress) => {
    if (stress >= 70) return '#F44336';  // High stress
    if (stress >= 40) return '#FF9800';  // Moderate
    return '#4CAF50';                     // Low stress
  };

  // Trend indicator
  const getTrendInfo = (trend) => {
    switch (trend) {
      case 'increasing':
        return { label: 'Increasing', color: '#F44336', icon: '↑' };
      case 'decreasing':
        return { label: 'Decreasing', color: '#4CAF50', icon: '↓' };
      default:
        return { label: 'Stable', color: '#2196F3', icon: '→' };
    }
  };

  const trendInfo = getTrendInfo(stressTrend);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper
          sx={{
            p: 1.5,
            borderRadius: 2,
            boxShadow: 3,
            bgcolor: 'background.paper'
          }}
        >
          <Typography variant="subtitle2" fontWeight={600}>
            {data.question}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Stress Level: {Math.round(data.stress)}%
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 4,
        border: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper'
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Stress Mapping by Question
        </Typography>
        
        <Chip
          label={`${trendInfo.icon} ${trendInfo.label}`}
          size="small"
          sx={{
            bgcolor: `${trendInfo.color}15`,
            color: trendInfo.color,
            fontWeight: 600
          }}
        />
      </Box>

      {data.length > 0 ? (
        <Box sx={{ height: 250, width: '100%' }}>
          <ResponsiveContainer>
            <BarChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="question"
                tick={{ fontSize: 12, fill: '#666' }}
                axisLine={{ stroke: '#e0e0e0' }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 12, fill: '#666' }}
                axisLine={{ stroke: '#e0e0e0' }}
                tickFormatter={(val) => `${val}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Threshold line at 60% */}
              <ReferenceLine
                y={60}
                stroke="#FF9800"
                strokeDasharray="5 5"
                label={{
                  value: 'High',
                  position: 'right',
                  fill: '#FF9800',
                  fontSize: 10
                }}
              />
              
              <Bar dataKey="stress" radius={[6, 6, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.stress)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      ) : (
        <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography color="text.secondary">No stress data available</Typography>
        </Box>
      )}

      {/* Peak stress indicator */}
      {peakStressQuestion && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            bgcolor: '#FFF3E0',
            border: '1px solid #FFE0B2'
          }}
        >
          <Typography variant="body2" color="warning.dark">
            <strong>Peak Stress:</strong> Question {peakStressQuestion.question_num} 
            ({Math.round((peakStressQuestion.stress_score || 0) * 100)}%)
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default StressMapChart;
