// =========================================================
// CONSISTENCY PANEL COMPONENT
// Displays behavioral inconsistencies detected
// =========================================================

import React from 'react';
import { Box, Typography, Paper, Chip, Stack, Divider, Alert } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

const ConsistencyPanel = ({ inconsistencies }) => {
  const {
    inconsistency_count = 0,
    consistency_score = 1,
    details = [],
    is_consistent = true
  } = inconsistencies || {};

  // Color based on consistency score
  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4CAF50';
    if (score >= 0.5) return '#FF9800';
    return '#F44336';
  };

  const scoreColor = getScoreColor(consistency_score);

  // Severity colors
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#F44336';
      case 'moderate': return '#FF9800';
      default: return '#FFC107';
    }
  };

  // Rule type descriptions
  const getRuleDescription = (rule) => {
    const descriptions = {
      'high_blink_positive_sentiment':
        'High blink rate detected despite positive verbal sentiment',
      'low_gaze_stable_voice':
        'Unstable gaze with otherwise calm vocal patterns',
      'many_fillers_confident_sentiment':
        'Frequent filler words despite confident language',
      'high_pitch_variance_calm_face':
        'Vocal stress indicators with calm facial expression',
      'long_pause_simple_question':
        'Extended pause for straightforward question',
      'sentiment_blink_mismatch':
        'Emotional state mismatch between blink patterns and sentiment'
    };
    return descriptions[rule] || rule;
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
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Behavioral Consistency
        </Typography>
        
        <Chip
          icon={
            is_consistent ? (
              <CheckCircleOutlineIcon sx={{ fontSize: 16 }} />
            ) : (
              <WarningAmberIcon sx={{ fontSize: 16 }} />
            )
          }
          label={is_consistent ? 'Consistent' : `${inconsistency_count} Flags`}
          size="small"
          sx={{
            bgcolor: is_consistent ? '#E8F5E9' : '#FFF3E0',
            color: is_consistent ? '#4CAF50' : '#FF9800',
            fontWeight: 600
          }}
        />
      </Box>

      {/* Consistency Score */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'baseline',
          gap: 1,
          mb: 3
        }}
      >
        <Typography
          variant="h3"
          sx={{ fontWeight: 700, color: scoreColor }}
        >
          {Math.round(consistency_score * 100)}%
        </Typography>
        <Typography variant="body2" color="text.secondary">
          consistency score
        </Typography>
      </Box>

      {/* Progress bar */}
      <Box sx={{ mb: 3 }}>
        <Box
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: '#f0f0f0',
            overflow: 'hidden'
          }}
        >
          <Box
            sx={{
              height: '100%',
              width: `${consistency_score * 100}%`,
              bgcolor: scoreColor,
              borderRadius: 4,
              transition: 'width 0.5s ease'
            }}
          />
        </Box>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Inconsistency Details */}
      {details.length > 0 ? (
        <Stack spacing={2}>
          <Typography variant="subtitle2" color="text.secondary">
            Detected Inconsistencies
          </Typography>
          
          {details.map((item, idx) => (
            <Alert
              key={idx}
              severity="warning"
              sx={{
                borderRadius: 2,
                bgcolor: `${getSeverityColor(item.severity)}10`,
                border: `1px solid ${getSeverityColor(item.severity)}40`,
                '& .MuiAlert-icon': {
                  color: getSeverityColor(item.severity)
                }
              }}
            >
              <Box>
                <Typography variant="body2" fontWeight={600}>
                  Question {item.question_num}: {item.rule.replace(/_/g, ' ')}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {getRuleDescription(item.rule)}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={item.severity}
                    size="small"
                    sx={{
                      bgcolor: `${getSeverityColor(item.severity)}20`,
                      color: getSeverityColor(item.severity),
                      textTransform: 'capitalize',
                      fontSize: '0.7rem'
                    }}
                  />
                </Box>
              </Box>
            </Alert>
          ))}
        </Stack>
      ) : (
        <Box
          sx={{
            p: 3,
            textAlign: 'center',
            bgcolor: '#E8F5E9',
            borderRadius: 2
          }}
        >
          <CheckCircleOutlineIcon sx={{ fontSize: 40, color: '#4CAF50', mb: 1 }} />
          <Typography variant="body2" color="success.main" fontWeight={500}>
            No behavioral inconsistencies detected
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Cross-modal signals are aligned across all responses
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ConsistencyPanel;
