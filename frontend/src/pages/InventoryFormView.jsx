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

  useEffect(() => {
    fetchData();
    if (!isNew) {
      fetchPicking();
    }
  }, [id]);

  const fetchData = async () => {
    try {
      const [productsData, locationsData, operationTypesData] = await Promise.all([
        inventoryAPI.getProducts(),
        inventoryAPI.getLocations(),
        inventoryAPI.getOperationTypes()
      ]);

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
      console.error('Error fetching data:', error);
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
      console.error('Error fetching picking:', error);
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
      quantity: 1,
      isNew: true
    }]);
  };

  const updateStockMove = (index, field, value) => {
    setStockMoves(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const removeStockMove = async (index) => {
    const move = stockMoves[index];
    if (!move.isNew && move.id) {
      try {
        await inventoryAPI.deleteStockMove(move.id);
      } catch (error) {
        console.error('Error deleting stock move:', error);
      }
    }
    setStockMoves(prev => prev.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Validate that we have at least one stock move
      if (stockMoves.length === 0) {
        alert('Please add at least one product line before saving.');
        return;
      }

      // Validate that all stock moves have required fields
      const invalidMoves = stockMoves.filter(m => !m.product || !m.quantity || m.quantity <= 0);
      if (invalidMoves.length > 0) {
        alert('Please ensure all product lines have a product selected and a valid quantity.');
        return;
      }
      
      if (isNew) {
        // Create new picking
        const pickingData = {
          ...formData,
          status: 'draft'
        };
        const newPicking = await inventoryAPI.createPicking(pickingData);
        
        // Create stock moves
        for (const move of stockMoves) {
          if (move.product && move.quantity) {
            await inventoryAPI.createStockMove({
              picking: newPicking.id,
              product: move.product,
              quantity: move.quantity,
              source_location: formData.source_location,
              destination_location: formData.destination_location,
              status: 'draft'
            });
          }
        }
        
        alert('Picking created successfully!');
        navigate(`/inventory/${type}/${newPicking.id}`);
      } else {
        // Update existing picking
        await inventoryAPI.updatePicking(id, formData);
        
        // Update stock moves
        for (const move of stockMoves) {
          if (move.isNew && move.product && move.quantity) {
            await inventoryAPI.createStockMove({
              picking: id,
              product: move.product,
              quantity: move.quantity,
              source_location: formData.source_location,
              destination_location: formData.destination_location,
              status: currentStatus
            });
          } else if (!move.isNew && move.id) {
            await inventoryAPI.updateStockMove(move.id, {
              product: move.product,
              quantity: move.quantity
            });
          }
        }
        
        alert('Picking updated successfully!');
        await fetchPicking();
      }
    } catch (error) {
      console.error('Error saving:', error);
      const errorData = error.response?.data;
      
      if (errorData?.details) {
        // Handle validation errors
        const errorMessages = Object.entries(errorData.details)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join('\n');
        alert(`Validation Error:\n\n${errorMessages}`);
      } else {
        alert(errorData?.error || 'Error saving picking. Please try again.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    try {
      await inventoryAPI.validatePicking(id);
      alert('Picking validated successfully! Stock has been updated.');
      await fetchPicking();
    } catch (error) {
      console.error('Error validating:', error);
      const errorData = error.response?.data;
      
      // Check for insufficient stock error
      if (errorData?.error && errorData?.product) {
        alert(
          `❌ Insufficient Stock\n\n` +
          `Product: ${errorData.product}\n` +
          `Required: ${errorData.required}\n` +
          `Available: ${errorData.available}\n` +
          `Location: ${errorData.location}\n\n` +
          `Please adjust the quantity or check stock levels.`
        );
      } else {
        alert(errorData?.error || 'Error validating picking. Please try again.');
      }
    }
  };

  const handleCancel = async () => {
    if (window.confirm('Are you sure you want to cancel this picking?')) {
      try {
        await inventoryAPI.cancelPicking(id);
        await fetchPicking();
      } catch (error) {
        console.error('Error cancelling:', error);
        alert('Error cancelling picking');
      }
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
            <Button variant="outline" onClick={handleSave} disabled={saving}>
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
                {({ value, onChange }) => (
                  <SelectTrigger value={value} onChange={onChange}>
                    <SelectValue placeholder="Select location">
                      <SelectContent>
                        {locations.map(loc => (
                          <SelectItem key={loc.id} value={loc.id}>
                            {loc.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                      {locations.find(l => l.id === value)?.name || 'Select location'}
                    </SelectValue>
                  </SelectTrigger>
                )}
              </Select>
            </div>

            <div className="form-field">
              <Label htmlFor="destination_location">Destination Location</Label>
              <Select 
                value={formData.destination_location}
                onValueChange={(value) => handleSelectChange('destination_location', value)}
              >
                {({ value, onChange }) => (
                  <SelectTrigger value={value} onChange={onChange}>
                    <SelectValue placeholder="Select location">
                      <SelectContent>
                        {locations.map(loc => (
                          <SelectItem key={loc.id} value={loc.id}>
                            {loc.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                      {locations.find(l => l.id === value)?.name || 'Select location'}
                    </SelectValue>
                  </SelectTrigger>
                )}
              </Select>
            </div>
          </div>

          {/* Product Lines Section */}
          <div className="product-lines-section">
            <h3 className="section-title">Product Lines</h3>
            
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
                        {({ value, onChange }) => (
                          <SelectTrigger value={value} onChange={onChange}>
                            <SelectValue placeholder="Select product">
                              <SelectContent>
                                {products.map(prod => (
                                  <SelectItem key={prod.id} value={prod.id}>
                                    {prod.sku} - {prod.name} ({prod.uom || 'Units'})
                                  </SelectItem>
                                ))}
                              </SelectContent>
                              {(() => {
                                const selectedProduct = products.find(p => p.id === value);
                                return selectedProduct 
                                  ? `${selectedProduct.sku} - ${selectedProduct.name} (${selectedProduct.uom || 'Units'})`
                                  : 'Select product';
                              })()}
                            </SelectValue>
                          </SelectTrigger>
                        )}
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Input 
                        type="number" 
                        value={move.quantity}
                        onChange={(e) => updateStockMove(index, 'quantity', parseFloat(e.target.value))}
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
