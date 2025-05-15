import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  Alert,
  InputAdornment,
  IconButton,
  Fade
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import ManageOrder from './ManageOrder';

function ManageOrderTab() {
  const [orderId, setOrderId] = useState('');
  const [error, setError] = useState(null);
  const [showOrderDetails, setShowOrderDetails] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!orderId.trim()) {
      setError('Please enter an order ID');
      return;
    }
    setError(null);
    setShowOrderDetails(true);
  };

  const handleClear = () => {
    setOrderId('');
    setError(null);
    setShowOrderDetails(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mb: 3, 
          borderRadius: 2,
          background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <ReceiptIcon color="primary" sx={{ fontSize: 32, mr: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Track Your Order
          </Typography>
        </Box>

        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Enter Order ID"
              value={orderId}
              onChange={(e) => {
                setOrderId(e.target.value);
                setError(null);
              }}
              error={!!error}
              helperText={error}
              placeholder="e.g., 12345"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: orderId && (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={handleClear}
                      edge="end"
                      size="small"
                    >
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  '&:hover fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
          </Box>
          <Button 
            variant="contained" 
            color="primary" 
            type="submit"
            fullWidth
            size="large"
            startIcon={<SearchIcon />}
            sx={{
              borderRadius: 2,
              py: 1.5,
              textTransform: 'none',
              fontSize: '1.1rem',
              boxShadow: 2,
              '&:hover': {
                boxShadow: 4,
              },
            }}
          >
            Look Up Order
          </Button>
        </form>
      </Paper>

      <Fade in={showOrderDetails}>
        <Box>
          {showOrderDetails && (
            <ManageOrder orderId={orderId} />
          )}
        </Box>
      </Fade>
    </Box>
  );
}

export default ManageOrderTab; 