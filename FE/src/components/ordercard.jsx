import React from 'react';

function OrderCard({ orderData }) {
  return (
    <div className="order-details-card">
      <h3>Order #{orderData.id}</h3>
      <div className="order-meta">
        <p><strong>Status:</strong> {orderData.status}</p>
        <p><strong>Date:</strong> {new Date(orderData.created_at).toLocaleString()}</p>
      </div>
      
      <div className="order-items">
        <h4>Items:</h4>
        <ul>
          {orderData.items.map((item, index) => (
            <li key={index}>
              {item.quantity}x {item.name} @ ${item.price.toFixed(2)} = ${item.total.toFixed(2)}
            </li>
          ))}
        </ul>
      </div>
      
      <div className="order-totals">
        <p><strong>Subtotal:</strong> ${orderData.subtotal.toFixed(2)}</p>
        <p><strong>Delivery Fee:</strong> ${orderData.delivery_fee.toFixed(2)}</p>
        <p><strong>Total:</strong> ${orderData.total.toFixed(2)}</p>
      </div>
      
      <div className="order-status">
        <p><strong>Payment:</strong> {orderData.payment_status}</p>
        <p><strong>Delivery Address:</strong> {orderData.delivery_address}</p>
        {orderData.estimated_delivery && (
          <p><strong>Estimated Delivery:</strong> {new Date(orderData.estimated_delivery).toLocaleString()}</p>
        )}
      </div>
    </div>
  );
}

export default OrderCard;