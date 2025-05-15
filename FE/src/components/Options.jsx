import React, { useState } from 'react';

function Options({ type, items, onSelect, onComplete }) {
  const [selectedItems, setSelectedItems] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);

  const handleItemToggle = (item) => {
    setSelectedItems(prev => 
      prev.some(i => i.id === item.id) 
        ? prev.filter(i => i.id !== item.id)
        : [...prev, item]
    );
  };

  const handleRestaurantSelect = (restaurant) => {
    setSelectedRestaurant(restaurant);
    onSelect(restaurant);
  };

  if (type === 'restaurants') {
    return (
      <div className="options-container">
        <h3>Select a Restaurant:</h3>
        {items.map(restaurant => (
          <div key={restaurant.id} className="option-item">
            <input
              type="radio"
              id={`rest-${restaurant.id}`}
              name="restaurant"
              onChange={() => handleRestaurantSelect(restaurant)}
            />
            <label htmlFor={`rest-${restaurant.id}`}>
              {restaurant.name} - {restaurant.address}
            </label>
          </div>
        ))}
      </div>
    );
  }

  if (type === 'menu') {
    return (
      <div className="options-container">
        <h3>Select Items from {selectedRestaurant?.name}:</h3>
        {items.map(item => (
          <div key={item.id} className="option-item">
            <input
              type="checkbox"
              id={`item-${item.id}`}
              onChange={() => handleItemToggle(item)}
            />
            <label htmlFor={`item-${item.id}`}>
              {item.name} - ${item.price} {item.description && `- ${item.description}`}
            </label>
          </div>
        ))}
        <button 
          onClick={() => onComplete(selectedItems)}
          className="complete-btn"
        >
          Complete Order
        </button>
      </div>
    );
  }

  return null;
}

export default Options;