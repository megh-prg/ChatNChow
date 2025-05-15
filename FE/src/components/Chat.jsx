import React, { useState, useEffect } from 'react';
import Message from './Message';
import Inputbox from './Inputbox';
import Options from './Options';
import OrderCard from './OrderCard';
import './Chat.css'; // Make sure you have this for the new styles

function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Welcome to Mangia Eats! How can I help you?' }
  ]);
  const [orderId, setOrderId] = useState(null);
  const [orderDetails, setOrderDetails] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [isOrdering, setIsOrdering] = useState(false);
  const [priority, setPriority] = useState('normal');

  // Enhanced handleSend with AI features
  const handleSend = async (message) => {
    // Add user message with timestamp
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      // Send to AI-enhanced endpoint
      const response = await fetch('http://localhost:8000/ai-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          order_id: orderId,
          context: {
            is_ordering: isOrdering,
            previous_messages: messages.slice(-3) // Send last 3 messages for context
          }
        })
      });

      const data = await response.json();

      // Handle priority from sentiment analysis
      setPriority(data.priority);
      
      // Process response
      const botMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: data.intent,
        priority: data.priority
      };

      if (data.order_details) {
        setOrderDetails(data.order_details);
        setOrderId(data.order_details.order_id);
        botMessage.isOrderDetails = true;
      } 
      else if (data.menu_items) {
        setMenuItems(data.menu_items);
        setIsOrdering(true);
        botMessage.isMenu = true;
      }

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    }
  };

  return (
    <div className={`chat-container ${priority === 'high' ? 'priority-high' : ''}`}>
      <div className="messages">
        {messages.map((msg, i) => (
          <Message 
            key={i} 
            message={msg}
            intent={msg.intent}
            priority={msg.priority}
          >
            {msg.isOrderDetails && <OrderCard details={orderDetails} />}
            {msg.isMenu && <Options items={menuItems} onSelect={handleSend} />}
          </Message>
        ))}
      </div>
      <Inputbox onSend={handleSend} disabled={priority === 'high'} />
      
      {/* Priority warning banner */}
      {priority === 'high' && (
        <div className="priority-banner">
          ⚠️ Your concern has been prioritized
        </div>
      )}
    </div>
  );
}

export default Chat;