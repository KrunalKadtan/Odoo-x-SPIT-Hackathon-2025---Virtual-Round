import './Input.css';

export function Input({ 
  type = 'text', 
  className = '', 
  placeholder = '',
  value,
  onChange,
  required = false,
  disabled = false,
  id,
  name,
  ...props 
}) {
  return (
    <input
      type={type}
      id={id}
      name={name}
      className={`input ${className}`}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      disabled={disabled}
      {...props}
    />
  );
}
