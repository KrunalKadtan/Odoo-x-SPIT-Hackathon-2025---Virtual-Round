import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { AddProductModal } from '../components/AddProductModal';
import { AddLocationModal } from '../components/AddLocationModal';
import { inventoryAPI } from '../services/api';
import './StocksPage.css';

export function StocksPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [locations, setLocations] = useState([]);
  const [stockQuants, setStockQuants] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (activeTab === 'products') {
        const data = await inventoryAPI.getProducts();
        setProducts(data);
      } else if (activeTab === 'levels') {
        const data = await inventoryAPI.getStockQuants();
        setStockQuants(data);
      } else if (activeTab === 'locations') {
        const data = await inventoryAPI.getLocations();
        setLocations(data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProductSuccess = () => {
    fetchData();
  };

  const handleLocationSuccess = () => {
    fetchData();
  };

  const filteredProducts = products.filter(p =>
    p.sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredStockQuants = stockQuants.filter(sq =>
    sq.product_sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sq.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    sq.location_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredLocations = locations.filter(loc =>
    loc.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    loc.full_path?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    loc.barcode?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const tabs = [
    { id: 'products', label: 'Products', icon: '📦' },
    { id: 'levels', label: 'Stock Levels', icon: '📊' },
    { id: 'locations', label: 'Locations', icon: '📍' },
  ];

  return (
    <div className="stocks-page">
      <div className="stocks-header">
        <div>
          <h1 className="stocks-title">Stocks</h1>
          <p className="stocks-subtitle">Manage products, stock levels, and locations</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="stocks-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="stocks-content">
        {/* Products Tab */}
        {activeTab === 'products' && (
          <div className="tab-content">
            <div className="content-header">
              <div className="search-wrapper">
                <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <Input
                  placeholder="Search products by SKU or name..."
                  className="search-input"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button onClick={() => setIsProductModalOpen(true)}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Product
              </Button>
            </div>

            {loading ? (
              <div className="loading-state">Loading products...</div>
            ) : filteredProducts.length === 0 ? (
              <div className="empty-state">No products found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="header-row">
                    <TableHead>SKU</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>UOM</TableHead>
                    <TableHead>Cost</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredProducts.map((product) => (
                    <TableRow key={product.id} className="data-row">
                      <TableCell className="sku-cell">{product.sku}</TableCell>
                      <TableCell>{product.name}</TableCell>
                      <TableCell>{product.category_name || '-'}</TableCell>
                      <TableCell className="uom-cell">{product.uom || 'Units'}</TableCell>
                      <TableCell>${parseFloat(product.cost).toFixed(2)}</TableCell>
                      <TableCell>${parseFloat(product.price).toFixed(2)}</TableCell>
                      <TableCell>
                        {product.is_active ? (
                          <Badge className="badge-ready">Active</Badge>
                        ) : (
                          <Badge className="badge-draft">Inactive</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        )}

        {/* Stock Levels Tab */}
        {activeTab === 'levels' && (
          <div className="tab-content">
            <div className="content-header">
              <div className="search-wrapper">
                <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <Input
                  placeholder="Search by product or location..."
                  className="search-input"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {loading ? (
              <div className="loading-state">Loading stock levels...</div>
            ) : filteredStockQuants.length === 0 ? (
              <div className="empty-state">No stock quantities found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="header-row">
                    <TableHead>Product SKU</TableHead>
                    <TableHead>Product Name</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Reserved</TableHead>
                    <TableHead>Available</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredStockQuants.map((sq) => (
                    <TableRow key={sq.id} className="data-row">
                      <TableCell className="sku-cell">{sq.product_sku}</TableCell>
                      <TableCell>{sq.product_name}</TableCell>
                      <TableCell>{sq.location_name}</TableCell>
                      <TableCell className="quantity-cell">{parseFloat(sq.quantity).toFixed(2)}</TableCell>
                      <TableCell className="reserved-cell">{parseFloat(sq.reserved_quantity).toFixed(2)}</TableCell>
                      <TableCell className="available-cell">
                        <strong>{parseFloat(sq.available_quantity).toFixed(2)}</strong>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        )}

        {/* Locations Tab */}
        {activeTab === 'locations' && (
          <div className="tab-content">
            <div className="content-header">
              <div className="search-wrapper">
                <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <Input
                  placeholder="Search locations by name or barcode..."
                  className="search-input"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button onClick={() => setIsLocationModalOpen(true)}>
                <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Location
              </Button>
            </div>

            {loading ? (
              <div className="loading-state">Loading locations...</div>
            ) : filteredLocations.length === 0 ? (
              <div className="empty-state">No locations found</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="header-row">
                    <TableHead>Name</TableHead>
                    <TableHead>Full Path</TableHead>
                    <TableHead>Usage Type</TableHead>
                    <TableHead>Barcode</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLocations.map((location) => (
                    <TableRow key={location.id} className="data-row">
                      <TableCell className="name-cell">{location.name}</TableCell>
                      <TableCell>{location.full_path || location.name}</TableCell>
                      <TableCell>
                        <Badge className="badge-info">
                          {location.usage_type_display || location.usage_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{location.barcode || '-'}</TableCell>
                      <TableCell>
                        {location.is_active ? (
                          <Badge className="badge-ready">Active</Badge>
                        ) : (
                          <Badge className="badge-draft">Inactive</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      <AddProductModal
        isOpen={isProductModalOpen}
        onClose={() => setIsProductModalOpen(false)}
        onSuccess={handleProductSuccess}
      />

      <AddLocationModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
        onSuccess={handleLocationSuccess}
      />
    </div>
  );
}
