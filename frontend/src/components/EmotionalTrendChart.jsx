// =========================================================
// EMOTIONAL TREND CHART COMPONENT
// Line chart showing emotional state over time
// =========================================================

import React from 'react';
import { Box, Typography, Paper, Stack } from '@mui/material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const EmotionalTrendChart = ({ timeline }) => {
  // Process timeline data
  const data = timeline?.map((point, idx) => ({
    segment: idx + 1,
    stress: (point.stress_index ?? 0) * 100,
    energy: (point.energy_level ?? 0) * 100,
    dominant: point.dominant_state || 'neutral'
  })) || [];

  // Get state color
  const getStateColor = (state) => {
    switch (state) {
      case 'excited': return '#FF9800';
      case 'stressed': return '#F44336';
      case 'calm': return '#4CAF50';
      case 'low_energy': return '#9E9E9E';
      default: return '#2196F3';
    }
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
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
            Segment {d.segment}
          </Typography>
          <Typography variant="body2" color="error.main">
            Stress: {Math.round(d.stress)}%
          </Typography>
          <Typography variant="body2" color="primary.main">
            Energy: {Math.round(d.energy)}%
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: getStateColor(d.dominant),
              textTransform: 'capitalize',
              fontWeight: 500
            }}
          >
            State: {d.dominant.replace('_', ' ')}
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  // Legend items
  const legendItems = [
    { color: '#F44336', label: 'Stress' },
    { color: '#2196F3', label: 'Energy' }
  ];

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
          Emotional State Timeline
        </Typography>
        
        <Stack direction="row" spacing={2}>
          {legendItems.map((item) => (
            <Box key={item.label} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  bgcolor: item.color
                }}
              />
              <Typography variant="caption" color="text.secondary">
                {item.label}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Box>

      {data.length > 0 ? (
        <Box sx={{ height: 250, width: '100%' }}>
          <ResponsiveContainer>
            <AreaChart
              data={data}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <defs>
                <linearGradient id="stressGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#F44336" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#F44336" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2196F3" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2196F3" stopOpacity={0} />
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="segment"
                tick={{ fontSize: 12, fill: '#666' }}
                axisLine={{ stroke: '#e0e0e0' }}
                label={{
                  value: 'Questions',
                  position: 'insideBottom',
                  offset: -5,
                  fontSize: 11,
                  fill: '#999'
                }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 12, fill: '#666' }}
                axisLine={{ stroke: '#e0e0e0' }}
                tickFormatter={(val) => `${val}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Threshold line */}
              <ReferenceLine
                y={50}
                stroke="#FF9800"
                strokeDasharray="5 5"
              />
              
              <Area
                type="monotone"
                dataKey="stress"
                stroke="#F44336"
                strokeWidth={2}
                fill="url(#stressGradient)"
              />
              <Area
                type="monotone"
                dataKey="energy"
                stroke="#2196F3"
                strokeWidth={2}
                fill="url(#energyGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      ) : (
        <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography color="text.secondary">No timeline data available</Typography>
        </Box>
      )}

      {/* State legend */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          Dominant States:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {['calm', 'neutral', 'excited', 'stressed', 'low_energy'].map((state) => (
            <Box
              key={state}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                px: 1,
                py: 0.5,
                borderRadius: 1,
                bgcolor: `${getStateColor(state)}15`
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: getStateColor(state)
                }}
              />
              <Typography
                variant="caption"
                sx={{ color: getStateColor(state), textTransform: 'capitalize' }}
              >
                {state.replace('_', ' ')}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Box>
    </Paper>
  );
};

export default EmotionalTrendChart;
