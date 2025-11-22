import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { inventoryAPI } from '../services/api';
import './InventoryListView.css';

export function InventoryListView({ type }) {
  const navigate = useNavigate();
  const [pickings, setPickings] = useState([]);
  const [filteredPickings, setFilteredPickings] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  const title = type === 'receipts' ? 'Receipts' : 'Delivery Orders';

  useEffect(() => {
    fetchPickings();
  }, [type]);

  useEffect(() => {
    filterPickings();
  }, [searchTerm, pickings]);

  const fetchPickings = async () => {
    try {
      setLoading(true);
      const data = await inventoryAPI.getPickings();
      
      // Filter by operation type
      const filtered = data.filter(p => {
        if (type === 'receipts') {
          return p.operation_type_name?.toLowerCase().includes('receipt');
        } else {
          return p.operation_type_name?.toLowerCase().includes('delivery');
        }
      });
      
      setPickings(filtered);
      setFilteredPickings(filtered);
    } catch (error) {
      console.error('Error fetching pickings:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterPickings = () => {
    if (!searchTerm) {
      setFilteredPickings(pickings);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = pickings.filter(p => 
      p.reference?.toLowerCase().includes(term) ||
      p.partner?.toLowerCase().includes(term)
    );
    setFilteredPickings(filtered);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      draft: { className: 'badge-draft', label: 'Draft' },
      waiting: { className: 'badge-waiting', label: 'Waiting' },
      confirmed: { className: 'badge-ready', label: 'Ready' },
      done: { className: 'badge-done', label: 'Done' },
      cancelled: { className: 'badge-cancelled', label: 'Cancelled' },
    };

    const config = statusMap[status] || statusMap.draft;
    return (
      <Badge className={`${config.className} badge-outline`} variant="outline">
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
  };

  return (
    <div className="inventory-list-view">
      {/* Header */}
      <div className="list-header">
        <div>
          <h1 className="list-title">{title}</h1>
          <p className="list-subtitle">Manage your {type}</p>
        </div>
        <Button 
          className="new-button"
          onClick={() => navigate(`/inventory/${type}/new`)}
        >
          <svg className="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New
        </Button>
      </div>

      {/* Controls */}
      <div className="list-controls">
        <div className="search-wrapper">
          <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <Input 
            placeholder="Search by reference or contact..." 
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="view-toggles">
          <Button variant="outline" size="icon" className="view-button">
            <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </Button>
          <Button variant="outline" size="icon" className="view-button">
            <svg className="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        {loading ? (
          <div className="loading-state">Loading...</div>
        ) : filteredPickings.length === 0 ? (
          <div className="empty-state">
            <p>No {type} found</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="header-row">
                <TableHead>Reference</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPickings.map((item, index) => (
                <TableRow 
                  key={item.id} 
                  className={`data-row ${index % 2 === 1 ? 'alternate' : ''}`}
                  onClick={() => navigate(`/inventory/${type}/${item.id}`)}
                >
                  <TableCell className="reference-cell">{item.reference}</TableCell>
                  <TableCell className="contact-cell">{item.partner || '-'}</TableCell>
                  <TableCell className="date-cell">{formatDate(item.scheduled_date)}</TableCell>
                  <TableCell>{getStatusBadge(item.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
