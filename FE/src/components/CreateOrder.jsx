import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  TextField,
  CircularProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Paper
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Restaurant as RestaurantIcon,
  ShoppingCart as CartIcon
} from '@mui/icons-material';

function CreateOrder() {
  const [step, setStep] = useState(0);
  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [specialInstructions, setSpecialInstructions] = useState('');

  // Fetch restaurants
  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/restaurants/');
        setRestaurants(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch restaurants');
        setLoading(false);
      }
    };
    fetchRestaurants();
  }, []);

  // Fetch menu items when restaurant is selected
  useEffect(() => {
    const fetchMenuItems = async () => {
      if (selectedRestaurant) {
        try {
          setLoading(true);
          const response = await axios.get(`http://localhost:8000/restaurants/${selectedRestaurant.id}/menu`);
          setMenuItems(response.data);
          setLoading(false);
        } catch (err) {
          setError('Failed to fetch menu items');
          setLoading(false);
        }
      }
    };
    fetchMenuItems();
  }, [selectedRestaurant]);

  const handleRestaurantSelect = (restaurant) => {
    setSelectedRestaurant(restaurant);
    setStep(1);
  };

  const addToCart = (item) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(cartItem => cartItem.id === item.id);
      if (existingItem) {
        return prevCart.map(cartItem =>
          cartItem.id === item.id
            ? { ...cartItem, quantity: cartItem.quantity + 1 }
            : cartItem
        );
      }
      return [...prevCart, { ...item, quantity: 1 }];
    });
  };

  const removeFromCart = (itemId) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === itemId);
      if (existingItem.quantity === 1) {
        return prevCart.filter(item => item.id !== itemId);
      }
      return prevCart.map(item =>
        item.id === itemId
          ? { ...item, quantity: item.quantity - 1 }
          : item
      );
    });
  };

  const calculateTotal = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const handlePlaceOrder = async () => {
    try {
      setLoading(true);
      const orderData = {
        restaurant_id: selectedRestaurant.id,
        items: cart.map(item => ({
          menu_item_id: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        delivery_address: deliveryAddress,
        special_instructions: specialInstructions
      };

      const response = await axios.post('http://localhost:8000/orders/create', orderData);
      setStep(3); // Show confirmation
      setLoading(false);
    } catch (err) {
      setError('Failed to place order');
      setLoading(false);
    }
  };

  const steps = ['Select Restaurant', 'Choose Items', 'Review & Place Order'];

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

  return (
    <Box sx={{ p: 3 }}>
      <Stepper activeStep={step} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {step === 0 && (
        <Grid container spacing={3}>
          {restaurants.map((restaurant) => (
            <Grid item xs={12} md={6} key={restaurant.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: 3 }
                }}
                onClick={() => handleRestaurantSelect(restaurant)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <RestaurantIcon sx={{ mr: 1 }} />
                    <Typography variant="h6">{restaurant.name}</Typography>
                  </Box>
                  <Typography color="textSecondary">{restaurant.address}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {step === 1 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            {selectedRestaurant.name} - Menu
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <List>
                {menuItems.map((item) => (
                  <ListItem key={item.id} divider>
                    <ListItemText
                      primary={item.name}
                      secondary={`$${item.price.toFixed(2)} - ${item.description}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton onClick={() => addToCart(item)}>
                        <AddIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  <CartIcon sx={{ mr: 1 }} />
                  Your Cart
                </Typography>
                {cart.length === 0 ? (
                  <Typography color="textSecondary">Your cart is empty</Typography>
                ) : (
                  <>
                    <List>
                      {cart.map((item) => (
                        <ListItem key={item.id}>
                          <ListItemText
                            primary={item.name}
                            secondary={`$${item.price.toFixed(2)} x ${item.quantity}`}
                          />
                          <ListItemSecondaryAction>
                            <IconButton onClick={() => removeFromCart(item.id)}>
                              <RemoveIcon />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                    <Typography variant="h6" sx={{ mt: 2 }}>
                      Total: ${calculateTotal().toFixed(2)}
                    </Typography>
                    <Button
                      variant="contained"
                      fullWidth
                      sx={{ mt: 2 }}
                      onClick={() => setStep(2)}
                    >
                      Proceed to Checkout
                    </Button>
                  </>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}

      {step === 2 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Review Your Order
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>Order Summary</Typography>
                <List>
                  {cart.map((item) => (
                    <ListItem key={item.id}>
                      <ListItemText
                        primary={item.name}
                        secondary={`$${item.price.toFixed(2)} x ${item.quantity}`}
                      />
                      <Typography>
                        ${(item.price * item.quantity).toFixed(2)}
                      </Typography>
                    </ListItem>
                  ))}
                </List>
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Total: ${calculateTotal().toFixed(2)}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>Delivery Details</Typography>
                <TextField
                  fullWidth
                  label="Delivery Address"
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  margin="normal"
                  required
                />
                <TextField
                  fullWidth
                  label="Special Instructions"
                  value={specialInstructions}
                  onChange={(e) => setSpecialInstructions(e.target.value)}
                  margin="normal"
                  multiline
                  rows={3}
                />
                <Button
                  variant="contained"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={handlePlaceOrder}
                  disabled={!deliveryAddress}
                >
                  Place Order
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}

      {step === 3 && (
        <Box textAlign="center">
          <Typography variant="h5" gutterBottom>
            Order Placed Successfully!
          </Typography>
          <Typography>
            Thank you for your order. You can track your order status in the "Track Order" section.
          </Typography>
          <Button
            variant="contained"
            sx={{ mt: 3 }}
            onClick={() => {
              setStep(0);
              setCart([]);
              setDeliveryAddress('');
              setSpecialInstructions('');
            }}
          >
            Place Another Order
          </Button>
        </Box>
      )}
    </Box>
  );
}

export default CreateOrder; 