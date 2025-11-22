import './Button.css';

export function Button({ 
  children, 
  variant = 'default', 
  size = 'default', 
  className = '', 
  type = 'button',
  disabled = false,
  onClick,
  ...props 
}) {
  const variantClass = `button-${variant}`;
  const sizeClass = `button-${size}`;
  
  return (
    <button
      type={type}
      className={`button ${variantClass} ${sizeClass} ${className}`}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
}
