
import React, { useState, useEffect } from 'react';
import Message from './Message';
import Inputbox from './Inputbox';
import Options from './Options';
import OrderCard from './OrderCard';

function OrderSummary({ order }) {
  const [expanded, setExpanded] = useState(false);

  if (!order) return null;

  return (
    <div className="order-summary p-3 rounded-lg border border-gray-300 shadow-sm bg-white mb-3">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <strong>Order #{order.id}</strong> — Status: {order.status || "N/A"}
        </div>
        <button className="text-blue-500 hover:underline">
          {expanded ? "Hide" : "Show Details"}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 text-sm">
          <p><strong>Customer:</strong> {order.customer || "N/A"}</p>
          <p><strong>Order Date:</strong> {order.order_date || "N/A"}</p>
          <p><strong>Payment:</strong> {order.payment || "N/A"}</p>
          <p><strong>Delivery:</strong> {order.delivery || "N/A"}</p>
          <p><strong>Address:</strong> {order.address || "N/A"}</p>
          <p><strong>Items:</strong></p>
          <ul className="list-disc list-inside">
            {order.items && order.items.length > 0 ? (
              order.items.map((item, i) => (
                <li key={i}>
                  {item.quantity}x {item.name} - ${item.price || "0.00"}
                </li>
              ))
            ) : (
              <li>No items</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default OrderSummary;
