import { useState, useRef, useEffect } from 'react';
import './Select.css';

export function Select({ 
  children, 
  value, 
  onValueChange, 
  defaultValue,
  disabled = false,
  ...props 
}) {
  const [internalValue, setInternalValue] = useState(defaultValue || '');
  const currentValue = value !== undefined ? value : internalValue;

  const handleChange = (newValue) => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  return (
    <div className="select-wrapper" {...props}>
      {children && children({ value: currentValue, onChange: handleChange, disabled })}
    </div>
  );
}

export function SelectTrigger({ children, value, onChange, disabled, className = '' }) {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        triggerRef.current && 
        !triggerRef.current.contains(event.target) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelect = (newValue) => {
    onChange(newValue);
    setIsOpen(false);
  };

  return (
    <div className="select-container">
      <button
        ref={triggerRef}
        type="button"
        className={`select-trigger ${className}`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <span className="select-value">
          {children}
        </span>
        <svg 
          className="select-icon" 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
      
      {isOpen && (
        <div ref={dropdownRef} className="select-content">
          {children && children.props && children.props.children && 
            children.props.children.map((child) => {
              if (child && child.props) {
                return (
                  <div
                    key={child.props.value}
                    className={`select-item ${value === child.props.value ? 'selected' : ''}`}
                    onClick={() => handleSelect(child.props.value)}
                  >
                    {child.props.children}
                    {value === child.props.value && (
                      <svg 
                        className="select-check" 
                        width="16" 
                        height="16" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="2"
                      >
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                    )}
                  </div>
                );
              }
              return null;
            })
          }
        </div>
      )}
    </div>
  );
}

export function SelectValue({ placeholder, children }) {
  return children || <span className="select-placeholder">{placeholder}</span>;
}

export function SelectContent({ children }) {
  return <>{children}</>;
}

export function SelectItem({ value, children }) {
  return <>{children}</>;
}
