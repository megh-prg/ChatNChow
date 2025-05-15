import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function ChatSupport() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! Welcome to Support.\nHow can I help you with your food delivery today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentOrderId, setCurrentOrderId] = useState(null);
  const [orderDetails, setOrderDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messageEndRef = useRef(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage;
    if (!textToSend.trim()) return;

    setError(null);
    const userMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          order_id: currentOrderId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Network error');
      }

      const data = await response.json();

      if (data.order_data) setOrderDetails(data.order_data);
      if (data.detected_order_id) setCurrentOrderId(data.detected_order_id);

      // Append bot response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (error) {
      setError(error.message);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error.message}. Please try again later.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    if (action === 'Order Food') {
      sendMessage('I want to place a new order'); // Triggers menu items list
    } else if (action === 'Track Order') {
      sendMessage('Track my order'); // Triggers order tracking logic
    }
  };

  const formatMessageContent = (content) => {
    if (typeof content !== 'string') return content;
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line.split(/(\d+\.)/g).map((part, j) => (
          /\d+\./.test(part) ? <strong key={j}>{part}</strong> : part
        ))}
        <br />
      </React.Fragment>
    ));
  };

  const OrderDetails = ({ orderData }) => {
    if (!orderData) return null;

    return (
      <div className="order-details">
        <h2>Mangia Eats Support</h2>
        <h3>Order #{orderData.order_id}</h3>
        <div className="customer-info">
          <p><strong>Customer:</strong> {orderData.customer_name}</p>
          <p><strong>Order Date:</strong> {new Date(orderData.order_date).toLocaleString()}</p>
        </div>
        <div className="order-status">
          <p><strong>Status:</strong> {orderData.status}</p>
          <p><strong>Payment:</strong> {orderData.payment_status}</p>
          <p><strong>Delivery:</strong> {orderData.delivery_status}</p>
        </div>
        <div className="delivery-info">
          <p><strong>Address:</strong> {orderData.delivery_address}</p>
          {orderData.estimated_delivery && (
            <p><strong>Estimated Delivery:</strong> {new Date(orderData.estimated_delivery).toLocaleTimeString()}</p>
          )}
        </div>
        <div className="order-items">
          <h4>Items:</h4>
          <ul>
            {orderData.items?.map((item) => (
              <li key={item.item_id}>
                {item.quantity}x {item.name} - ${item.price} ({item.restaurant})
              </li>
            ))}
          </ul>
        </div>
        <div className="order-totals">
          <p><strong>Subtotal:</strong> ${orderData.subtotal?.toFixed(2)}</p>
          <p><strong>Delivery Fee:</strong> ${orderData.delivery_fee?.toFixed(2)}</p>
          <p><strong>Tax:</strong> ${orderData.tax?.toFixed(2)}</p>
          <p><strong>Total:</strong> ${orderData.total_amount?.toFixed(2)}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="food-delivery-chat">
      <div className="chat-container">
        <div className="chat-header">
          <div className="logo">
            <img src="/logo.png" alt="Logo" className="logo-image" />
            <h2>Support</h2>
          </div>
          <div className="order-badge">
            {currentOrderId && `Order #${currentOrderId}`}
          </div>
        </div>

        <div className="quick-actions">
          <button onClick={() => handleQuickAction('Order Food')} className="food-btn primary">New Order</button>
          <button onClick={() => handleQuickAction('Track Order')} className="food-btn secondary">Track Order</button>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}>
              <div className="message-content">{formatMessageContent(message.content)}</div>
              <div className="message-timestamp">{message.timestamp}</div>
            </div>
          ))}
          {error && <div className="error-message">{error}</div>}
          <div ref={messageEndRef} />
        </div>

        {orderDetails && <OrderDetails orderData={orderDetails} />}

        <form className="chat-input" onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message here..."
            className="food-input"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading} className="send-btn">
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatSupport;
