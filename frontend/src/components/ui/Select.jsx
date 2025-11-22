import { useState, useRef, useEffect, createContext, useContext } from 'react';
import './Select.css';

// Create context for Select state management
const SelectContext = createContext(null);

export function Select({ 
  children, 
  value, 
  onValueChange, 
  defaultValue,
  disabled = false,
  ...props 
}) {
  const [internalValue, setInternalValue] = useState(defaultValue || '');
  const [isOpen, setIsOpen] = useState(false);
  const currentValue = value !== undefined ? value : internalValue;

  const handleChange = (newValue) => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    if (onValueChange) {
      onValueChange(newValue);
    }
    setIsOpen(false); // Close dropdown after selection
  };

  const contextValue = {
    value: currentValue,
    onChange: handleChange,
    disabled,
    isOpen,
    setIsOpen
  };

  return (
    <SelectContext.Provider value={contextValue}>
      <div className="select-wrapper" {...props}>
        {children}
      </div>
    </SelectContext.Provider>
  );
}

export function SelectTrigger({ children, className = '' }) {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error('SelectTrigger must be used within a Select component');
  }

  const { disabled, isOpen, setIsOpen } = context;
  const triggerRef = useRef(null);

  const handleClick = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  return (
    <button
      ref={triggerRef}
      type="button"
      className={`select-trigger ${className}`}
      onClick={handleClick}
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
  );
}

export function SelectValue({ placeholder, children }) {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error('SelectValue must be used within a Select component');
  }

  const { value } = context;
  
  // If children is provided and value exists, render children
  // Otherwise show placeholder
  if (value && children) {
    return <>{children}</>;
  }
  
  return <span className="select-placeholder">{placeholder || 'Select...'}</span>;
}

export function SelectContent({ children }) {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error('SelectContent must be used within a Select component');
  }

  const { isOpen, setIsOpen } = context;
  const contentRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contentRef.current && !contentRef.current.contains(event.target)) {
        // Check if click is on trigger button
        const trigger = contentRef.current.parentElement?.querySelector('.select-trigger');
        if (trigger && !trigger.contains(event.target)) {
          setIsOpen(false);
        }
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, setIsOpen]);

  if (!isOpen) {
    return null;
  }

  return (
    <div ref={contentRef} className="select-content">
      {children}
    </div>
  );
}

export function SelectItem({ value, children }) {
  const context = useContext(SelectContext);
  if (!context) {
    throw new Error('SelectItem must be used within a Select component');
  }

  const { value: selectedValue, onChange } = context;
  const isSelected = selectedValue === value;

  const handleClick = () => {
    onChange(value);
  };

  return (
    <div
      className={`select-item ${isSelected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      {children}
      {isSelected && (
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
