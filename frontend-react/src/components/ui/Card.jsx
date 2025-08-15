import React from 'react';
import clsx from 'clsx';

const Card = ({ children, className = '', hoverable = true, ...props }) => {
  const classes = clsx(
    'glass-card rounded-card p-6',
    {
      'hover:transform hover:-translate-y-1 hover:shadow-lg': hoverable,
    },
    className
  );

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export default Card;