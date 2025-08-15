import React from 'react';

const LoadingSpinner = ({ size = 'medium', className = '' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className={`fixed inset-0 bg-black/50 flex items-center justify-center z-50 ${className}`}>
      <div className="bg-white/10 rounded-lg p-6 flex items-center space-x-3">
        <div className={`animate-spin rounded-full border-b-2 border-brand-green ${sizeClasses[size]}`}></div>
        <span className="text-text-high">Loading...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;