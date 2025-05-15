import React from 'react';

const Message = ({ message }) => {
  return (
    <div className={`message ${message.role}`}>
      {message.content}
    </div>
  );
};

export default Message;