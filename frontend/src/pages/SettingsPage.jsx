import { useState, useEffect } from 'react';
import { inventoryAPI } from '../services/api';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import './SettingsPage.css';

export function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    low_stock_threshold: 10,
    default_receipt_location_id: '',
    default_delivery_location_id: '',
    default_adjustment_location_id: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch settings and locations in parallel
      const [settingsData, locationsData] = await Promise.all([
        inventoryAPI.getWarehouseSettings(),
        inventoryAPI.getLocations(),
      ]);

      setSettings(settingsData);
      setLocations(locationsData);

      // Populate form with current settings
      setFormData({
        low_stock_threshold: settingsData.low_stock_threshold || 10,
        default_receipt_location_id: settingsData.default_receipt_location?.id || '',
        default_delivery_location_id: settingsData.default_delivery_location?.id || '',
        default_adjustment_location_id: settingsData.default_adjustment_location?.id || '',
      });
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'low_stock_threshold' ? parseInt(value) || 0 : value
    }));
    setSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      // Prepare data for API
      const updateData = {
        low_stock_threshold: formData.low_stock_threshold,
        default_receipt_location_id: formData.default_receipt_location_id || null,
        default_delivery_location_id: formData.default_delivery_location_id || null,
        default_adjustment_location_id: formData.default_adjustment_location_id || null,
      };

      await inventoryAPI.updateWarehouseSettings(updateData);
      
      setSuccess(true);
      
      // Refresh settings
      await fetchData();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError(err.response?.data?.message || 'Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-header">
          <h1 className="settings-title">Warehouse Settings</h1>
          <p className="settings-subtitle">Configure your warehouse parameters and default locations</p>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="settings-title">Warehouse Settings</h1>
        <p className="settings-subtitle">Configure your warehouse parameters and default locations</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <svg className="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <svg className="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Settings saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <Card className="settings-card">
          <div className="card-header">
            <h2 className="card-title">Stock Thresholds</h2>
            <p className="card-description">Configure alert thresholds for inventory levels</p>
          </div>

          <div className="form-group">
            <label htmlFor="low_stock_threshold" className="form-label">
              Low Stock Threshold
              <span className="label-hint">Items below this quantity will be flagged as low stock</span>
            </label>
            <input
              type="number"
              id="low_stock_threshold"
              name="low_stock_threshold"
              value={formData.low_stock_threshold}
              onChange={handleInputChange}
              min="0"
              className="form-input"
              required
            />
          </div>
        </Card>

        <Card className="settings-card">
          <div className="card-header">
            <h2 className="card-title">Default Locations</h2>
            <p className="card-description">Set default locations for different operation types</p>
          </div>

          <div className="form-group">
            <label htmlFor="default_receipt_location_id" className="form-label">
              Default Receipt Location
              <span className="label-hint">Default location for incoming goods</span>
            </label>
            <select
              id="default_receipt_location_id"
              name="default_receipt_location_id"
              value={formData.default_receipt_location_id}
              onChange={handleInputChange}
              className="form-select"
            >
              <option value="">-- Select Location --</option>
              {locations.map(location => (
                <option key={location.id} value={location.id}>
                  {location.full_path || location.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="default_delivery_location_id" className="form-label">
              Default Delivery Location
              <span className="label-hint">Default location for outgoing goods</span>
            </label>
            <select
              id="default_delivery_location_id"
              name="default_delivery_location_id"
              value={formData.default_delivery_location_id}
              onChange={handleInputChange}
              className="form-select"
            >
              <option value="">-- Select Location --</option>
              {locations.map(location => (
                <option key={location.id} value={location.id}>
                  {location.full_path || location.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="default_adjustment_location_id" className="form-label">
              Default Adjustment Location
              <span className="label-hint">Default location for inventory adjustments</span>
            </label>
            <select
              id="default_adjustment_location_id"
              name="default_adjustment_location_id"
              value={formData.default_adjustment_location_id}
              onChange={handleInputChange}
              className="form-select"
            >
              <option value="">-- Select Location --</option>
              {locations.map(location => (
                <option key={location.id} value={location.id}>
                  {location.full_path || location.name}
                </option>
              ))}
            </select>
          </div>
        </Card>

        <div className="settings-actions">
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
          <Button type="button" variant="outline" onClick={fetchData} disabled={saving}>
            Reset
          </Button>
        </div>
      </form>

      {settings && (
        <Card className="settings-card info-card">
          <div className="card-header">
            <h2 className="card-title">Settings Information</h2>
          </div>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Last Updated:</span>
              <span className="info-value">
                {settings.updated_at ? new Date(settings.updated_at).toLocaleString() : 'Never'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Updated By:</span>
              <span className="info-value">
                {settings.updated_by?.username || 'System'}
              </span>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
