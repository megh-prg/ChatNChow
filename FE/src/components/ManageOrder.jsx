import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Paper,
  Typography,
  Box,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent
} from '@mui/material';

function ManageOrder({ orderId }) {
  const [orderDetails, setOrderDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        console.log('Fetching order details for ID:', orderId);
        const response = await axios.get(`http://localhost:8000/orders/${orderId}/details`);
        console.log('Order details response:', response.data);
        setOrderDetails(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching order details:', err);
        setError('Failed to fetch order details');
        setLoading(false);
      }
    };

    if (orderId) {
      fetchOrderDetails();
    }
  }, [orderId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!orderDetails) {
    return <Alert severity="info">No order details found</Alert>;
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Order #{orderDetails.order_id}
        </Typography>
        <Chip 
          label={orderDetails.status.toUpperCase()} 
          color={orderDetails.status === 'delivered' ? 'success' : 'primary'}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Customer Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Customer Information</Typography>
              <Typography><strong>Name:</strong> {orderDetails.customer_name}</Typography>
              <Typography><strong>Order Time:</strong> {new Date(orderDetails.order_time).toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Delivery Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Delivery Information</Typography>
              <Typography><strong>Address:</strong> {orderDetails.delivery_address}</Typography>
              {orderDetails.delivery && (
                <>
                  <Typography><strong>Delivery Person:</strong> {orderDetails.delivery.delivery_person}</Typography>
                  <Typography><strong>Estimated Time:</strong> {new Date(orderDetails.delivery.estimated_time).toLocaleString()}</Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Order Items */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Order Items</Typography>
              <List>
                {orderDetails.items.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={`${item.quantity}x ${item.name}`}
                        secondary={`Price: $${item.price.toFixed(2)} | Total: $${item.total.toFixed(2)}`}
                      />
                    </ListItem>
                    {index < orderDetails.items.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Order Summary</Typography>
              <Box sx={{ pl: 2 }}>
                <Typography><strong>Subtotal:</strong> ${orderDetails.total_amount.toFixed(2)}</Typography>
                <Typography><strong>Delivery Charge:</strong> ${orderDetails.delivery_charge.toFixed(2)}</Typography>
                <Typography><strong>Tax:</strong> ${orderDetails.tax.toFixed(2)}</Typography>
                <Typography variant="h6" sx={{ mt: 2 }}>
                  <strong>Total Amount:</strong> ${orderDetails.final_amount.toFixed(2)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Payment Information */}
        {orderDetails.payment && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Payment Information</Typography>
                <Typography><strong>Status:</strong> {orderDetails.payment.status}</Typography>
                <Typography><strong>Method:</strong> {orderDetails.payment.method}</Typography>
                <Typography><strong>Amount:</strong> ${orderDetails.payment.amount.toFixed(2)}</Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Special Instructions */}
        {orderDetails.special_instructions && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Special Instructions</Typography>
                <Typography>{orderDetails.special_instructions}</Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
}

export default ManageOrder; 