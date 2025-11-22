import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui/Select';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { inventoryAPI } from '../services/api';
import './InventoryFormView.css';

export function InventoryFormView({ type }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const isNew = id === 'new';

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [loadingData, setLoadingData] = useState(true); // Loading state for data fetching
  const [formData, setFormData] = useState({
    reference: '',
    partner: '',
    scheduled_date: new Date().toISOString().split('T')[0],
    source_location: '',
    destination_location: '',
    operation_type: '',
    notes: ''
  });
  const [stockMoves, setStockMoves] = useState([]);
  const [products, setProducts] = useState([]);
  const [locations, setLocations] = useState([]);
  const [operationTypes, setOperationTypes] = useState([]);
  const [currentStatus, setCurrentStatus] = useState('draft');

  // Centralized error handling function
  const handleAPIError = (error) => {
    console.error('API Error:', error);
    
    const errorData = error.response?.data;
    
    // Handle network errors (no response from server)
    if (!errorData) {
      alert('❌ Network error. Please check your connection.');
      return;
    }
    
    // Handle validation errors from backend (errorData.details)
    if (errorData.details) {
      const errorMessages = [];
      Object.entries(errorData.details).forEach(([field, messages]) => {
        // Format field names: convert snake_case to Title Case
        const fieldName = field
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ')
          .toUpperCase();
        
        // Handle both array and string message formats
        const messageList = Array.isArray(messages) ? messages : [messages];
        errorMessages.push(`${fieldName}: ${messageList.join(', ')}`);
      });
      
      alert(`❌ Validation Error:\n\n${errorMessages.join('\n')}`);
      return;
    }
    
    // Handle insufficient stock errors with detailed information
    if (errorData.error && errorData.product) {
      alert(
        `❌ Insufficient Stock\n\n` +
        `Product: ${errorData.product}\n` +
        `Required: ${errorData.required}\n` +
        `Available: ${errorData.available}\n` +
        `Location: ${errorData.location}\n\n` +
        `Please adjust the quantity or check stock levels.`
      );
      return;
    }
    
    // Generic error fallback
    alert(`❌ Error: ${errorData.error || 'Something went wrong. Please try again.'}`);
  };

  useEffect(() => {
    fetchData();
    if (!isNew) {
      fetchPicking();
    }
  }, [id]);

  const fetchData = async () => {
    try {
      setLoadingData(true); // Set loading state during data fetching
      const [productsData, locationsData, operationTypesData] = await Promise.all([
        inventoryAPI.getProducts(),
        inventoryAPI.getLocations(),
        inventoryAPI.getOperationTypes()
      ]);

      console.log('Fetched products:', productsData);
      console.log('Fetched locations:', locationsData);
      console.log('Fetched operation types:', operationTypesData);

      setProducts(productsData);
      setLocations(locationsData);
      setOperationTypes(operationTypesData);

      // Set default operation type based on type
      if (isNew && operationTypesData.length > 0) {
        const defaultOp = operationTypesData.find(op => 
          type === 'receipts' 
            ? op.name.toLowerCase().includes('receipt')
            : op.name.toLowerCase().includes('delivery')
        );
        if (defaultOp) {
          setFormData(prev => ({
            ...prev,
            operation_type: defaultOp.id,
            source_location: defaultOp.default_source_location || '',
            destination_location: defaultOp.default_destination_location || ''
          }));
        }
      }
    } catch (error) {
      handleAPIError(error);
    } finally {
      setLoadingData(false); // Clear loading state after data is fetched
    }
  };

  const fetchPicking = async () => {
    try {
      const data = await inventoryAPI.getPicking(id);
      setFormData({
        reference: data.reference,
        partner: data.partner || '',
        scheduled_date: data.scheduled_date.split('T')[0],
        source_location: data.source_location,
        destination_location: data.destination_location,
        operation_type: data.operation_type,
        notes: data.notes || ''
      });
      setStockMoves(data.stock_moves || []);
      setCurrentStatus(data.status);
    } catch (error) {
      handleAPIError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const addStockMoveLine = () => {
    setStockMoves(prev => [...prev, {
      id: `temp-${Date.now()}`,
      product: '',
      quantity: 1, // Initialize as number 1
      isNew: true
    }]);
  };

  const updateStockMove = (index, field, value) => {
    setStockMoves(prev => {
      const updated = [...prev];
      if (field === 'quantity') {
        // Parse as float and validate it's a positive number
        const numValue = parseFloat(value);
        updated[index] = { 
          ...updated[index], 
          [field]: isNaN(numValue) || numValue <= 0 ? '' : numValue 
        };
      } else {
        updated[index] = { ...updated[index], [field]: value };
      }
      return updated;
    });
  };

  const removeStockMove = (index) => {
    // Remove stock move from state array
    // Deletion is handled through nested write (excluded moves are deleted)
    setStockMoves(prev => prev.filter((_, i) => i !== index));
  };

  const validateForm = () => {
    const errors = [];
    
    // Validate source location is selected
    if (!formData.source_location) {
      errors.push('SOURCE LOCATION: This field is required');
    }
    
    // Validate destination location is selected
    if (!formData.destination_location) {
      errors.push('DESTINATION LOCATION: This field is required');
    }
    
    // Validate at least one stock move exists
    if (stockMoves.length === 0) {
      errors.push('PRODUCT LINES: At least one product line is required');
    }
    
    // Validate each stock move has product selected and valid quantity
    stockMoves.forEach((move, index) => {
      const lineNumber = index + 1;
      
      if (!move.product) {
        errors.push(`PRODUCT LINE ${lineNumber}: Product selection is required`);
      }
      
      if (!move.quantity || move.quantity <= 0) {
        errors.push(`PRODUCT LINE ${lineNumber}: Valid quantity (greater than 0) is required`);
      }
    });
    
    return errors;
  };

  const handleSave = async () => {
    // Call validateForm before API calls
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      // Display validation errors in alert with clear field names
      alert(`❌ Validation Error:\n\n${validationErrors.join('\n')}`);
      return;
    }

    try {
      setSaving(true);
      
      // Build picking data with nested stock_moves
      const pickingData = {
        reference: formData.reference || undefined,
        partner: formData.partner,
        scheduled_date: formData.scheduled_date,
        source_location: parseInt(formData.source_location),
        destination_location: parseInt(formData.destination_location),
        operation_type: parseInt(formData.operation_type),
        notes: formData.notes,
        stock_moves: stockMoves.map(move => {
          const moveData = {
            product: parseInt(move.product),
            quantity: parseFloat(move.quantity),
            notes: move.notes || ''
          };
          
          // Include id for existing moves (not new ones)
          if (!move.isNew && move.id && typeof move.id === 'number') {
            moveData.id = move.id;
          }
          
          return moveData;
        })
      };
      
      if (isNew) {
        // Create new picking with nested write format
        pickingData.status = 'draft';
        await inventoryAPI.createPicking(pickingData);
        
        // Add success message with checkmark emoji
        alert('✅ Success!\n\nPicking created successfully!');
        navigate(`/inventory/${type}`);
      } else {
        // Update existing picking with nested write format
        await inventoryAPI.updatePicking(id, pickingData);
        
        // Add success message with checkmark emoji
        alert('✅ Success!\n\nPicking updated successfully!');
        await fetchPicking();
      }
    } catch (error) {
      handleAPIError(error);
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    // Add confirmation dialog before validation
    if (!window.confirm('Validate this picking? This will update stock levels and cannot be undone.')) {
      return;
    }
    
    try {
      // Call inventoryAPI.validatePicking(id)
      await inventoryAPI.validatePicking(id);
      
      // Handle success response with success message with checkmark emoji
      alert('✅ Success!\n\nPicking validated successfully! Stock has been updated.');
      
      // Refresh picking data after successful validation
      await fetchPicking();
    } catch (error) {
      // Use handleAPIError for error handling
      // Display insufficient stock errors with detailed information
      handleAPIError(error);
    }
  };

  const handleCancel = async () => {
    // Add confirmation dialog before cancellation
    if (!window.confirm('Cancel this picking? This action cannot be undone.')) {
      return;
    }
    
    try {
      // Update handleCancel to call inventoryAPI.cancelPicking(id)
      await inventoryAPI.cancelPicking(id);
      
      // Handle success response with success message with checkmark emoji
      alert('✅ Success!\n\nPicking cancelled.');
      
      // Refresh picking data after successful cancellation
      await fetchPicking();
    } catch (error) {
      // Use handleAPIError for error handling
      handleAPIError(error);
    }
  };

  const getStepStatus = (step) => {
    const steps = ['draft', 'confirmed', 'done'];
    const currentIndex = steps.indexOf(currentStatus);
    const stepIndex = steps.indexOf(step);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'upcoming';
  };

  if (loading) {
    return <div className="loading-container">Loading...</div>;
  }

  // Display loading indicator while data is being fetched
  if (loadingData) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading data...</p>
      </div>
    );
  }

  return (
    <div className="inventory-form-view">
      {/* Header with Back Button */}
      <div className="form-header">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => navigate(`/inventory/${type}`)}
          className="back-button"
        >
          <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Button>
        <div>
          <h1 className="form-title">{type === 'receipts' ? 'Receipt' : 'Delivery Order'}</h1>
          <p className="form-subtitle">{isNew ? 'Create new' : 'Edit'} {type === 'receipts' ? 'receipt' : 'delivery order'}</p>
        </div>
      </div>

      <div className="form-content">
        {/* Action Buttons and Status Pipeline */}
        <div className="form-actions">
          <div className="action-buttons">
            {!isNew && currentStatus !== 'done' && (
              <Button className="validate-button" onClick={handleValidate}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Validate
              </Button>
            )}
            <Button variant="outline" onClick={handleSave} disabled={saving || loadingData}>
              <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              {saving ? 'Saving...' : 'Save'}
            </Button>
            {!isNew && currentStatus !== 'done' && currentStatus !== 'cancelled' && (
              <Button variant="outline" className="cancel-button" onClick={handleCancel}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Cancel
              </Button>
            )}
          </div>

          {/* Status Pipeline */}
          {!isNew && (
            <div className="status-pipeline">
              {['draft', 'confirmed', 'done'].map((step, index) => {
                const status = getStepStatus(step);
                return (
                  <div key={step} className="pipeline-step-wrapper">
                    <div className="pipeline-step">
                      <div className={`step-circle ${status}`}>
                        {status === 'completed' ? (
                          <svg className="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <span className="step-number">{index + 1}</span>
                        )}
                      </div>
                      <span className={`step-label ${status}`}>
                        {step.charAt(0).toUpperCase() + step.slice(1)}
                      </span>
                    </div>
                    {index < 2 && <div className={`step-connector ${status}`} />}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Form Card */}
        <div className="form-card">
          {/* Header Information */}
          <div className="form-grid">
            <div className="form-field">
              <Label htmlFor="reference">Reference ID</Label>
              <Input 
                id="reference" 
                name="reference"
                value={formData.reference}
                onChange={handleInputChange}
                placeholder="Auto-generated"
                readOnly={!isNew}
              />
            </div>

            <div className="form-field">
              <Label htmlFor="partner">Contact</Label>
              <Input
                id="partner"
                name="partner"
                value={formData.partner}
                onChange={handleInputChange}
                placeholder="Enter contact name"
              />
            </div>

            <div className="form-field">
              <Label htmlFor="scheduled_date">Schedule Date</Label>
              <Input 
                id="scheduled_date" 
                name="scheduled_date"
                type="date" 
                value={formData.scheduled_date}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-field">
              <Label htmlFor="source_location">Source Location</Label>
              <Select 
                value={formData.source_location}
                onValueChange={(value) => handleSelectChange('source_location', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select location">
                    {locations.find(l => l.id === formData.source_location)?.name}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {locations.map(loc => (
                    <SelectItem key={loc.id} value={loc.id}>
                      {loc.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="form-field">
              <Label htmlFor="destination_location">Destination Location</Label>
              <Select 
                value={formData.destination_location}
                onValueChange={(value) => handleSelectChange('destination_location', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select location">
                    {locations.find(l => l.id === formData.destination_location)?.name}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {locations.map(loc => (
                    <SelectItem key={loc.id} value={loc.id}>
                      {loc.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Product Lines Section */}
          <div className="product-lines-section">
            <h3 className="section-title">Product Lines</h3>
            {loadingData && <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Loading products...</p>}
            {!loadingData && products.length === 0 && <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>⚠️ No products found. Please add products first.</p>}
            {!loadingData && products.length > 0 && <p style={{ color: '#10b981', fontSize: '0.875rem' }}>✓ {products.length} products available</p>}
            
            <Table>
              <TableHeader>
                <TableRow className="product-header-row">
                  <TableHead>Product</TableHead>
                  <TableHead className="quantity-column">Quantity</TableHead>
                  <TableHead className="action-column"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stockMoves.map((move, index) => (
                  <TableRow key={move.id || index}>
                    <TableCell>
                      <Select 
                        value={move.product}
                        onValueChange={(value) => updateStockMove(index, 'product', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select product">
                            {(() => {
                              const selectedProduct = products.find(p => p.id === move.product);
                              return selectedProduct 
                                ? `${selectedProduct.sku} - ${selectedProduct.name} (${selectedProduct.uom || 'Units'})`
                                : null;
                            })()}
                          </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                          {products.length === 0 ? (
                            <div style={{ padding: '0.5rem', textAlign: 'center', color: '#94a3b8' }}>
                              No products available
                            </div>
                          ) : (
                            products.map(prod => (
                              <SelectItem key={prod.id} value={prod.id}>
                                {prod.sku} - {prod.name} ({prod.uom || 'Units'})
                              </SelectItem>
                            ))
                          )}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Input 
                        type="number" 
                        value={move.quantity}
                        onChange={(e) => updateStockMove(index, 'quantity', e.target.value)}
                        min="0.01"
                        step="0.01"
                        className="quantity-input"
                      />
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        className="delete-button"
                        onClick={() => removeStockMove(index)}
                      >
                        <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Button 
              variant="outline" 
              className="add-line-button"
              onClick={addStockMoveLine}
            >
              <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add a Line
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
