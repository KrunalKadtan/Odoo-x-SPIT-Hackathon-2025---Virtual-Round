import { useState, useEffect } from 'react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { inventoryAPI } from '../services/api';
import './AddProductModal.css'; // Reuse the same styles

export function AddLocationModal({ isOpen, onClose, onSuccess }) {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    parent: '',
    barcode: '',
    usage_type: 'internal',
    is_active: true,
  });

  const usageTypes = [
    { value: 'internal', label: 'Internal Location' },
    { value: 'customer', label: 'Customer Location' },
    { value: 'supplier', label: 'Supplier Location' },
    { value: 'inventory', label: 'Inventory Loss' },
    { value: 'production', label: 'Production' },
    { value: 'transit', label: 'Transit Location' },
  ];

  useEffect(() => {
    if (isOpen) {
      fetchLocations();
    }
  }, [isOpen]);

  const fetchLocations = async () => {
    try {
      const data = await inventoryAPI.getLocations();
      setLocations(data);
    } catch (err) {
      console.error('Error fetching locations:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);

      // Validate required fields
      if (!formData.name) {
        setError('Please enter a location name');
        return;
      }

      // Prepare data for API
      const locationData = {
        name: formData.name.trim(),
        parent: formData.parent || null,
        barcode: formData.barcode.trim() || null,
        usage_type: formData.usage_type,
        is_active: formData.is_active,
      };

      await inventoryAPI.createLocation(locationData);
      
      // Reset form
      setFormData({
        name: '',
        parent: '',
        barcode: '',
        usage_type: 'internal',
        is_active: true,
      });

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error creating location:', err);
      setError(err.response?.data?.message || err.response?.data?.name?.[0] || 'Failed to create location. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      parent: '',
      barcode: '',
      usage_type: 'internal',
      is_active: true,
    });
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Add New Location</h2>
          <button className="modal-close" onClick={handleClose}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="modal-error">
            <svg className="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              Location Name <span className="required">*</span>
            </label>
            <Input
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Warehouse A / Zone 1 / Shelf A1"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="parent" className="form-label">
              Parent Location
            </label>
            <select
              id="parent"
              name="parent"
              value={formData.parent}
              onChange={handleInputChange}
              className="form-select"
            >
              <option value="">-- No Parent (Top Level) --</option>
              {locations.map(loc => (
                <option key={loc.id} value={loc.id}>
                  {loc.full_path || loc.name}
                </option>
              ))}
            </select>
            <span className="form-hint">Select a parent location to create a hierarchical structure</span>
          </div>

          <div className="form-group">
            <label htmlFor="usage_type" className="form-label">
              Usage Type <span className="required">*</span>
            </label>
            <select
              id="usage_type"
              name="usage_type"
              value={formData.usage_type}
              onChange={handleInputChange}
              className="form-select"
              required
            >
              {usageTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="barcode" className="form-label">
              Barcode
            </label>
            <Input
              id="barcode"
              name="barcode"
              value={formData.barcode}
              onChange={handleInputChange}
              placeholder="Location barcode (optional)"
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                className="checkbox-input"
              />
              <span>Active Location</span>
            </label>
          </div>

          <div className="modal-actions">
            <Button type="button" variant="outline" onClick={handleClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Location'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
