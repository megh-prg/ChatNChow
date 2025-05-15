const API_URL = 'http://localhost:8000';

// Enhanced with retry logic and timeout
const fetchWithRetry = async (url, options, retries = 2, timeout = 5000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (retries > 0) {
      console.log(`Retrying... ${retries} attempts left`);
      await new Promise(resolve => setTimeout(resolve, 1000));
      return fetchWithRetry(url, options, retries - 1, timeout);
    }
    throw error;
  }
};

// Main function to send chat messages
export const sendMessage = async (messages) => {
  try {
    console.groupCollapsed('[FRONTEND] Sending chat message');
    console.log('Request payload:', { messages });
    
    const response = await fetchWithRetry(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
      },
      body: JSON.stringify({ messages }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.detail || 
                      errorData.message || 
                      `HTTP error! status: ${response.status}`;
      throw new Error(errorMsg);
    }

    const data = await response.json();
    console.log('Response data:', data);
    console.groupEnd();
    return data;
  } catch (error) {
    console.groupEnd();
    console.error('[FRONTEND] API call failed:', error);
    throw new Error(error.message || 'Failed to communicate with the server');
  }
};

// Specific function for managing orders
export const manageOrder = async (orderId) => {
  try {
    console.groupCollapsed('[FRONTEND] Managing order');
    console.log('Order ID:', orderId);
    
    const response = await fetchWithRetry(`${API_URL}/manage-order`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ order_id: orderId }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.detail || 
                      `Order lookup failed with status: ${response.status}`;
      throw new Error(errorMsg);
    }

    const data = await response.json();
    console.log('Order details:', data);
    console.groupEnd();
    return data;
  } catch (error) {
    console.groupEnd();
    console.error('[FRONTEND] Order management failed:', error);
    throw new Error(error.message || 'Failed to retrieve order details');
  }
};

// Utility function to check API health
export const checkApiHealth = async () => {
  try {
    const response = await fetchWithRetry(`${API_URL}/health`, {
      method: 'GET',
      timeout: 3000
    });
    return response.ok;
  } catch (error) {
    console.error('[FRONTEND] API health check failed:', error);
    return false;
  }
};