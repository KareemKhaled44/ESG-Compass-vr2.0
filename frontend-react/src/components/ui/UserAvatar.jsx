import React from 'react';

const UserAvatar = ({ 
  fullName, 
  email, 
  size = 'md',
  className = '' 
}) => {
  // Function to get initials from full name or email
  const getInitials = (name, fallbackEmail) => {
    if (name && typeof name === 'string') {
      const nameParts = name.trim().split(' ').filter(part => part.length > 0);
      if (nameParts.length >= 2) {
        // First letter of first name + first letter of last name
        return (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase();
      } else if (nameParts.length === 1) {
        // Just first letter of single name
        return nameParts[0][0].toUpperCase();
      }
    }
    
    // Fallback to email if name is not available
    if (fallbackEmail && typeof fallbackEmail === 'string') {
      return fallbackEmail[0].toUpperCase();
    }
    
    return 'U'; // Ultimate fallback
  };

  // Size configurations
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg'
  };

  // Generate a consistent background color based on the initials
  const getBackgroundColor = (initials) => {
    const colors = [
      'bg-brand-green',
      'bg-brand-blue', 
      'bg-brand-teal',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-yellow-500',
      'bg-red-500'
    ];
    
    // Use character codes to get consistent color
    const charSum = initials.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0);
    return colors[charSum % colors.length];
  };

  const initials = getInitials(fullName, email);
  const bgColor = getBackgroundColor(initials);

  return (
    <div 
      className={`
        ${sizeClasses[size]} 
        ${bgColor} 
        rounded-full 
        flex 
        items-center 
        justify-center 
        text-white 
        font-semibold 
        select-none
        ${className}
      `}
      title={fullName || email || 'User'}
    >
      {initials}
    </div>
  );
};

export default UserAvatar;