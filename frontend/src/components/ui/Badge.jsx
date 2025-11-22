import './Badge.css';

export function Badge({ 
  children, 
  variant = 'default', 
  className = '',
  ...props 
}) {
  const variantClass = `badge-${variant}`;
  
  return (
    <span 
      className={`badge ${variantClass} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
