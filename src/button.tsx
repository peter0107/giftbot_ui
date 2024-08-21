import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  className = '', 
  variant = 'default', 
  ...props 
}) => {
  const baseStyles = 'px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200'
  const variantStyles = {
    default: 'bg-purple-500 text-white hover:bg-purple-600 focus:ring-purple-500',
    outline: 'border border-purple-500 text-purple-500 hover:bg-purple-50 focus:ring-purple-500',
    ghost: 'text-purple-500 hover:bg-purple-50 focus:ring-purple-500'
  }

  return (
    <button 
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}