"""
Tests for inventory models and API endpoints.
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test Category model."""
    
    def setUp(self):
        self.parent = Category.objects.create(name='Electronics')
        self.child = Category.objects.create(name='Computers', parent=self.parent)
    
    def test_category_creation(self):
        """Test category is created correctly."""
        self.assertEqual(self.parent.name, 'Electronics')
        self.assertIsNone(self.parent.parent)
    
    def test_category_hierarchy(self):
        """Test category hierarchy."""
        self.assertEqual(self.child.parent, self.parent)
        self.assertEqual(self.child.get_full_path(), 'Electronics / Computers')
    
    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.child), 'Electronics / Computers')


class ProductModelTest(TestCase):
    """Test Product model."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
    
    def test_product_creation(self):
        """Test product is created correctly."""
        self.assertEqual(self.product.sku, 'TEST-001')
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.cost, Decimal('10.00'))
        self.assertEqual(self.product.price, Decimal('20.00'))
    
    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'TEST-001 - Test Product')


class LocationModelTest(TestCase):
    """Test Location model."""
    
    def setUp(self):
        self.warehouse = Location.objects.create(name='Warehouse', usage_type='internal')
        self.shelf = Location.objects.create(name='Shelf A', parent=self.warehouse, usage_type='internal')
    
    def test_location_creation(self):
        """Test location is created correctly."""
        self.assertEqual(self.warehouse.name, 'Warehouse')
        self.assertEqual(self.warehouse.usage_type, 'internal')
    
    def test_location_hierarchy(self):
        """Test location hierarchy."""
        self.assertEqual(self.shelf.parent, self.warehouse)
        self.assertEqual(self.shelf.get_full_path(), 'Warehouse / Shelf A')


class StockQuantModelTest(TestCase):
    """Test StockQuant model."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.location = Location.objects.create(name='Test Location', usage_type='internal')
        self.stock_quant = StockQuant.objects.create(
            product=self.product,
            location=self.location,
            quantity=Decimal('100.00'),
            reserved_quantity=Decimal('20.00')
        )
    
    def test_stock_quant_creation(self):
        """Test stock quant is created correctly."""
        self.assertEqual(self.stock_quant.quantity, Decimal('100.00'))
        self.assertEqual(self.stock_quant.reserved_quantity, Decimal('20.00'))
    
    def test_available_quantity(self):
        """Test available quantity calculation."""
        self.assertEqual(self.stock_quant.available_quantity, Decimal('80.00'))


class ProductAPITest(APITestCase):
    """Test Product API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
    
    def test_list_products(self):
        """Test listing products."""
        response = self.client.get('/api/inventory/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_product(self):
        """Test creating a product."""
        data = {
            'sku': 'TEST-002',
            'name': 'New Product',
            'category': self.category.id,
            'cost': '15.00',
            'price': '30.00'
        }
        response = self.client.post('/api/inventory/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
    
    def test_retrieve_product(self):
        """Test retrieving a product."""
        response = self.client.get(f'/api/inventory/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sku'], 'TEST-001')
    
    def test_create_product_with_custom_uom(self):
        """Test creating a product with custom unit of measure."""
        data = {
            'sku': 'TEST-UOM-001',
            'name': 'Product with Custom UOM',
            'category': self.category.id,
            'cost': '10.00',
            'price': '20.00',
            'uom': 'kg'
        }
        response = self.client.post('/api/inventory/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['uom'], 'kg')
        
        # Verify in database
        product = Product.objects.get(sku='TEST-UOM-001')
        self.assertEqual(product.uom, 'kg')
    
    def test_create_product_with_default_uom(self):
        """Test creating a product without specifying UOM uses default 'Units'."""
        data = {
            'sku': 'TEST-UOM-002',
            'name': 'Product with Default UOM',
            'category': self.category.id,
            'cost': '10.00',
            'price': '20.00'
        }
        response = self.client.post('/api/inventory/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['uom'], 'Units')
        
        # Verify in database
        product = Product.objects.get(sku='TEST-UOM-002')
        self.assertEqual(product.uom, 'Units')
    
    def test_uom_in_serialized_response(self):
        """Test that UOM field is included in product API responses."""
        # Create product with specific UOM
        product = Product.objects.create(
            sku='TEST-UOM-003',
            name='Product for Serialization Test',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00'),
            uom='liters'
        )
        
        # Test retrieve endpoint
        response = self.client.get(f'/api/inventory/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('uom', response.data)
        self.assertEqual(response.data['uom'], 'liters')
        
        # Test list endpoint
        response = self.client.get('/api/inventory/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_data = next((p for p in response.data if p['sku'] == 'TEST-UOM-003'), None)
        self.assertIsNotNone(product_data)
        self.assertIn('uom', product_data)
        self.assertEqual(product_data['uom'], 'liters')


class PickingAPITest(APITestCase):
    """Test Picking API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
    
    def test_list_pickings(self):
        """Test listing pickings."""
        response = self.client.get('/api/inventory/pickings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_picking(self):
        """Test creating a picking."""
        from django.utils import timezone
        
        # Create a product for the stock move
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(
            sku='TEST-PROD',
            name='Test Product',
            category=category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        data = {
            'reference': 'TEST-001',
            'partner': 'Test Partner',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': product.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Picking.objects.count(), 1)


class NestedWritePickingAPITest(APITestCase):
    """Test nested writes for Picking with StockMoves."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        self.operation_type = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )
    
    def test_create_picking_with_nested_moves(self):
        """Test creating a picking with nested stock moves in a single request."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-001',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                },
                {
                    'product': self.product2.id,
                    'quantity': '5.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify picking was created
        self.assertEqual(Picking.objects.count(), 1)
        picking = Picking.objects.first()
        self.assertEqual(picking.reference, 'REC-001')
        
        # Verify stock moves were created
        self.assertEqual(picking.stock_moves.count(), 2)
        self.assertEqual(StockMove.objects.count(), 2)
    
    def test_create_picking_without_stock_moves_fails(self):
        """Test that creating a picking without stock moves returns validation error."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-002',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': []
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
    
    def test_create_picking_with_invalid_product_fails(self):
        """Test that creating a picking with invalid product reference fails."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-003',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': 99999,  # Invalid product ID
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_picking_with_missing_required_fields_fails(self):
        """Test that creating a picking with missing required fields in stock moves fails."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-004',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    # Missing quantity field
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
    
    def test_transaction_rollback_on_failure(self):
        """Test that transaction is rolled back when nested write fails."""
        from django.utils import timezone
        
        initial_picking_count = Picking.objects.count()
        initial_move_count = StockMove.objects.count()
        
        data = {
            'reference': 'REC-005',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                },
                {
                    'product': 99999,  # Invalid product - should cause rollback
                    'quantity': '5.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no partial data was created
        self.assertEqual(Picking.objects.count(), initial_picking_count)
        self.assertEqual(StockMove.objects.count(), initial_move_count)


class StockAvailabilityValidationTest(APITestCase):
    """Test stock availability validation for outgoing operations."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        self.source_location = Location.objects.create(name='Warehouse', usage_type='internal')
        self.dest_location = Location.objects.create(name='Customer', usage_type='customer')
        
        self.outgoing_operation = OperationType.objects.create(
            name='Delivery',
            code='outgoing',
            sequence_prefix='DEL'
        )
        
        self.incoming_operation = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )
    
    def test_validate_outgoing_with_sufficient_stock(self):
        """Test validating outgoing picking with sufficient stock succeeds."""
        from django.utils import timezone
        
        # Create stock
        StockQuant.objects.create(
            product=self.product,
            location=self.source_location,
            quantity=Decimal('100.00')
        )
        
        # Create picking with stock move
        picking = Picking.objects.create(
            reference='DEL-001',
            partner='Test Customer',
            operation_type=self.outgoing_operation,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product,
            quantity=Decimal('50.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Validate picking
        response = self.client.post(f'/api/inventory/pickings/{picking.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify stock was updated
        source_quant = StockQuant.objects.get(product=self.product, location=self.source_location)
        self.assertEqual(source_quant.quantity, Decimal('50.00'))
    
    def test_validate_outgoing_with_insufficient_stock(self):
        """Test validating outgoing picking with insufficient stock fails."""
        from django.utils import timezone
        
        # Create insufficient stock
        StockQuant.objects.create(
            product=self.product,
            location=self.source_location,
            quantity=Decimal('30.00')
        )
        
        # Create picking with stock move requiring more than available
        picking = Picking.objects.create(
            reference='DEL-002',
            partner='Test Customer',
            operation_type=self.outgoing_operation,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product,
            quantity=Decimal('50.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Attempt to validate picking
        response = self.client.post(f'/api/inventory/pickings/{picking.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error response format
        self.assertIn('error', response.data)
        self.assertIn('product', response.data)
        self.assertIn('required', response.data)
        self.assertIn('available', response.data)
        self.assertIn('location', response.data)
        
        # Verify stock was not updated
        source_quant = StockQuant.objects.get(product=self.product, location=self.source_location)
        self.assertEqual(source_quant.quantity, Decimal('30.00'))
    
    def test_validate_outgoing_with_no_stock_record(self):
        """Test validating outgoing picking with no stock record treats as zero."""
        from django.utils import timezone
        
        # Do not create any StockQuant record
        
        # Create picking with stock move
        picking = Picking.objects.create(
            reference='DEL-003',
            partner='Test Customer',
            operation_type=self.outgoing_operation,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Attempt to validate picking
        response = self.client.post(f'/api/inventory/pickings/{picking.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error indicates zero available
        self.assertEqual(response.data['available'], '0.00')
    
    def test_error_response_format(self):
        """Test that error response contains all required fields with correct format."""
        from django.utils import timezone
        
        # Create picking with no stock
        picking = Picking.objects.create(
            reference='DEL-004',
            partner='Test Customer',
            operation_type=self.outgoing_operation,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product,
            quantity=Decimal('25.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Attempt to validate
        response = self.client.post(f'/api/inventory/pickings/{picking.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify all required fields are present
        self.assertIn('error', response.data)
        self.assertIn(self.product.name, response.data['error'])
        self.assertEqual(response.data['product'], self.product.sku)
        self.assertEqual(response.data['required'], '25.00')
        self.assertEqual(response.data['available'], '0.00')
        self.assertEqual(response.data['location'], self.source_location.name)
    
    def test_incoming_operations_skip_validation(self):
        """Test that incoming operations do not check stock availability."""
        from django.utils import timezone
        
        # Create incoming picking (no stock needed at source)
        picking = Picking.objects.create(
            reference='REC-001',
            partner='Test Supplier',
            operation_type=self.incoming_operation,
            source_location=self.dest_location,  # Supplier location
            destination_location=self.source_location,  # Warehouse
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product,
            quantity=Decimal('100.00'),
            source_location=self.dest_location,
            destination_location=self.source_location,
            status='draft'
        )
        
        # Validate picking - should succeed without stock check
        response = self.client.post(f'/api/inventory/pickings/{picking.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardStatisticsTest(APITestCase):
    """Test dashboard statistics endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.warehouse = Location.objects.create(name='Warehouse', usage_type='internal')
        self.customer = Location.objects.create(name='Customer', usage_type='customer')
        self.supplier = Location.objects.create(name='Supplier', usage_type='supplier')
        
        self.incoming_op = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )
        
        self.outgoing_op = OperationType.objects.create(
            name='Delivery',
            code='outgoing',
            sequence_prefix='DEL'
        )
    
    def test_dashboard_stats_with_empty_database(self):
        """Test dashboard statistics with no data returns zeros."""
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['total_products'], 0)
        self.assertEqual(response.data['low_stock_items'], 0)
        self.assertEqual(response.data['pending_receipts'], 0)
        self.assertEqual(response.data['pending_deliveries'], 0)
    
    def test_total_products_calculation(self):
        """Test correct calculation of total active products."""
        # Create active products
        Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00'),
            is_active=True
        )
        Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00'),
            is_active=True
        )
        
        # Create inactive product (should not be counted)
        Product.objects.create(
            sku='PROD-003',
            name='Inactive Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00'),
            is_active=False
        )
        
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_products'], 2)
    
    def test_low_stock_items_calculation(self):
        """Test correct calculation of low stock items (quantity < 10 and > 0)."""
        product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        product3 = Product.objects.create(
            sku='PROD-003',
            name='Product 3',
            category=self.category,
            cost=Decimal('20.00'),
            price=Decimal('40.00')
        )
        
        # Low stock (should be counted)
        StockQuant.objects.create(
            product=product1,
            location=self.warehouse,
            quantity=Decimal('5.00')
        )
        
        # Zero stock (should NOT be counted)
        StockQuant.objects.create(
            product=product2,
            location=self.warehouse,
            quantity=Decimal('0.00')
        )
        
        # High stock (should NOT be counted)
        StockQuant.objects.create(
            product=product3,
            location=self.warehouse,
            quantity=Decimal('50.00')
        )
        
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['low_stock_items'], 1)
    
    def test_pending_receipts_calculation(self):
        """Test correct calculation of pending receipts."""
        from django.utils import timezone
        
        # Create pending receipts (draft, confirmed, assigned)
        Picking.objects.create(
            reference='REC-001',
            partner='Supplier 1',
            operation_type=self.incoming_op,
            source_location=self.supplier,
            destination_location=self.warehouse,
            status='draft',
            scheduled_date=timezone.now()
        )
        Picking.objects.create(
            reference='REC-002',
            partner='Supplier 2',
            operation_type=self.incoming_op,
            source_location=self.supplier,
            destination_location=self.warehouse,
            status='confirmed',
            scheduled_date=timezone.now()
        )
        Picking.objects.create(
            reference='REC-003',
            partner='Supplier 3',
            operation_type=self.incoming_op,
            source_location=self.supplier,
            destination_location=self.warehouse,
            status='assigned',
            scheduled_date=timezone.now()
        )
        
        # Create completed receipt (should NOT be counted)
        Picking.objects.create(
            reference='REC-004',
            partner='Supplier 4',
            operation_type=self.incoming_op,
            source_location=self.supplier,
            destination_location=self.warehouse,
            status='done',
            scheduled_date=timezone.now()
        )
        
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pending_receipts'], 3)
    
    def test_pending_deliveries_calculation(self):
        """Test correct calculation of pending deliveries."""
        from django.utils import timezone
        
        # Create pending deliveries (draft, confirmed, assigned)
        Picking.objects.create(
            reference='DEL-001',
            partner='Customer 1',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='draft',
            scheduled_date=timezone.now()
        )
        Picking.objects.create(
            reference='DEL-002',
            partner='Customer 2',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='confirmed',
            scheduled_date=timezone.now()
        )
        
        # Create completed delivery (should NOT be counted)
        Picking.objects.create(
            reference='DEL-003',
            partner='Customer 3',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='done',
            scheduled_date=timezone.now()
        )
        
        # Create cancelled delivery (should NOT be counted)
        Picking.objects.create(
            reference='DEL-004',
            partner='Customer 4',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='cancelled',
            scheduled_date=timezone.now()
        )
        
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pending_deliveries'], 2)
    
    def test_all_kpis_together(self):
        """Test all four KPIs calculated correctly together."""
        from django.utils import timezone
        
        # Create products
        product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00'),
            is_active=True
        )
        product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00'),
            is_active=True
        )
        
        # Create low stock
        StockQuant.objects.create(
            product=product1,
            location=self.warehouse,
            quantity=Decimal('3.00')
        )
        StockQuant.objects.create(
            product=product2,
            location=self.warehouse,
            quantity=Decimal('7.00')
        )
        
        # Create pending receipts
        Picking.objects.create(
            reference='REC-001',
            partner='Supplier',
            operation_type=self.incoming_op,
            source_location=self.supplier,
            destination_location=self.warehouse,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        # Create pending deliveries
        Picking.objects.create(
            reference='DEL-001',
            partner='Customer',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='confirmed',
            scheduled_date=timezone.now()
        )
        Picking.objects.create(
            reference='DEL-002',
            partner='Customer',
            operation_type=self.outgoing_op,
            source_location=self.warehouse,
            destination_location=self.customer,
            status='assigned',
            scheduled_date=timezone.now()
        )
        
        response = self.client.get('/api/inventory/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['total_products'], 2)
        self.assertEqual(response.data['low_stock_items'], 2)
        self.assertEqual(response.data['pending_receipts'], 1)
        self.assertEqual(response.data['pending_deliveries'], 2)


class StockAdjustmentIntegrationTest(APITestCase):
    """Integration tests for stock adjustment operations."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        # Create locations
        self.warehouse = Location.objects.create(name='WH/Stock', usage_type='internal')
        self.virtual_location = Location.objects.create(
            name='Inventory Adjustment',
            usage_type='inventory'
        )
        
        # Create adjustment operation type
        self.adjustment_op = OperationType.objects.create(
            name='Inventory Adjustment',
            code='internal',
            sequence_prefix='ADJ',
            default_source_location=self.virtual_location,
            default_destination_location=self.warehouse
        )
        
        # Create initial stock
        self.initial_stock = StockQuant.objects.create(
            product=self.product,
            location=self.warehouse,
            quantity=Decimal('50.00')
        )
    
    def test_positive_adjustment_end_to_end(self):
        """Test positive stock adjustment increases inventory."""
        from django.utils import timezone
        
        initial_quantity = self.initial_stock.quantity
        adjustment_qty = Decimal('10.00')
        
        # Create adjustment picking (from virtual to warehouse)
        data = {
            'reference': 'ADJ-001',
            'partner': 'Inventory Count',
            'operation_type': self.adjustment_op.id,
            'source_location': self.virtual_location.id,
            'destination_location': self.warehouse.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product.id,
                    'quantity': str(adjustment_qty),
                    'source_location': self.virtual_location.id,
                    'destination_location': self.warehouse.id,
                    'status': 'draft'
                }
            ]
        }
        
        # Create the adjustment
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        picking_id = response.data['id']
        
        # Validate the adjustment
        response = self.client.post(f'/api/inventory/pickings/{picking_id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify stock increased
        self.initial_stock.refresh_from_db()
        expected_quantity = initial_quantity + adjustment_qty
        self.assertEqual(self.initial_stock.quantity, expected_quantity)
        
        # Verify picking is done
        picking = Picking.objects.get(id=picking_id)
        self.assertEqual(picking.status, 'done')
    
    def test_negative_adjustment_end_to_end(self):
        """Test negative stock adjustment decreases inventory."""
        from django.utils import timezone
        
        initial_quantity = self.initial_stock.quantity
        adjustment_qty = Decimal('15.00')
        
        # Create adjustment picking (from warehouse to virtual)
        data = {
            'reference': 'ADJ-002',
            'partner': 'Inventory Count',
            'operation_type': self.adjustment_op.id,
            'source_location': self.warehouse.id,
            'destination_location': self.virtual_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product.id,
                    'quantity': str(adjustment_qty),
                    'source_location': self.warehouse.id,
                    'destination_location': self.virtual_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        # Create the adjustment
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        picking_id = response.data['id']
        
        # Validate the adjustment
        response = self.client.post(f'/api/inventory/pickings/{picking_id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify stock decreased
        self.initial_stock.refresh_from_db()
        expected_quantity = initial_quantity - adjustment_qty
        self.assertEqual(self.initial_stock.quantity, expected_quantity)
        
        # Verify picking is done
        picking = Picking.objects.get(id=picking_id)
        self.assertEqual(picking.status, 'done')
    
    def test_multiple_adjustments_sequential(self):
        """Test multiple adjustments applied sequentially."""
        from django.utils import timezone
        
        initial_quantity = self.initial_stock.quantity
        
        # First adjustment: +20
        data1 = {
            'reference': 'ADJ-003',
            'partner': 'Inventory Count',
            'operation_type': self.adjustment_op.id,
            'source_location': self.virtual_location.id,
            'destination_location': self.warehouse.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product.id,
                    'quantity': '20.00',
                    'source_location': self.virtual_location.id,
                    'destination_location': self.warehouse.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        picking1_id = response.data['id']
        
        response = self.client.post(f'/api/inventory/pickings/{picking1_id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Second adjustment: -10
        data2 = {
            'reference': 'ADJ-004',
            'partner': 'Inventory Count',
            'operation_type': self.adjustment_op.id,
            'source_location': self.warehouse.id,
            'destination_location': self.virtual_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product.id,
                    'quantity': '10.00',
                    'source_location': self.warehouse.id,
                    'destination_location': self.virtual_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        picking2_id = response.data['id']
        
        response = self.client.post(f'/api/inventory/pickings/{picking2_id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify final stock: initial + 20 - 10
        self.initial_stock.refresh_from_db()
        expected_quantity = initial_quantity + Decimal('20.00') - Decimal('10.00')
        self.assertEqual(self.initial_stock.quantity, expected_quantity)


class MoveHistoryModelTest(TestCase):
    """Test MoveHistory model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
        
        from django.utils import timezone
        self.picking = Picking.objects.create(
            reference='TEST-001',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
    
    def test_history_record_creation_with_all_fields(self):
        """Test creating a history record with all fields populated."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            notes='Test move'
        )
        
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.action_type, 'stock_move')
        self.assertEqual(history.picking, self.picking)
        self.assertEqual(history.product, self.product)
        self.assertEqual(history.quantity, Decimal('10.00'))
        self.assertEqual(history.source_location, self.source_location)
        self.assertEqual(history.destination_location, self.dest_location)
        self.assertEqual(history.notes, 'Test move')
        self.assertIsNotNone(history.timestamp)
    
    def test_str_method_stock_move(self):
        """Test __str__() method for stock_move action type."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        str_repr = str(history)
        self.assertIn(self.product.sku, str_repr)
        self.assertIn('10', str_repr)
        self.assertIn('moved', str_repr.lower())
    
    def test_str_method_status_change(self):
        """Test __str__() method for status_change action type."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        str_repr = str(history)
        self.assertIn(self.picking.reference, str_repr)
        self.assertIn('draft', str_repr)
        self.assertIn('confirmed', str_repr)
    
    def test_get_action_display_stock_move(self):
        """Test get_action_display() method for stock_move."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('25.00'),
            source_location=self.source_location,
            destination_location=self.dest_location
        )
        
        display = history.get_action_display()
        self.assertIn('Moved', display)
        self.assertIn('25', display)
        self.assertIn(self.product.sku, display)
        self.assertIn(self.source_location.name, display)
        self.assertIn(self.dest_location.name, display)
    
    def test_get_action_display_status_change(self):
        """Test get_action_display() method for status_change."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='done'
        )
        
        display = history.get_action_display()
        self.assertIn(self.picking.reference, display)
        self.assertIn('draft', display)
        self.assertIn('done', display)
        self.assertIn('changed', display.lower())
    
    def test_get_action_display_adjustment(self):
        """Test get_action_display() method for adjustment."""
        from .models import MoveHistory
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='adjustment',
            product=self.product,
            quantity=Decimal('5.00')
        )
        
        display = history.get_action_display()
        self.assertIn('adjustment', display.lower())
        self.assertIn(self.product.sku, display)
        self.assertIn('5', display)
    
    def test_filtering_by_product(self):
        """Test filtering history records by product."""
        from .models import MoveHistory
        
        product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        
        # Create history for product1
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        # Create history for product2
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=product2,
            quantity=Decimal('20.00')
        )
        
        # Filter by product1
        history_product1 = MoveHistory.objects.filter(product=self.product)
        self.assertEqual(history_product1.count(), 1)
        self.assertEqual(history_product1.first().product, self.product)
    
    def test_filtering_by_picking(self):
        """Test filtering history records by picking."""
        from .models import MoveHistory
        from django.utils import timezone
        
        picking2 = Picking.objects.create(
            reference='TEST-002',
            partner='Test Partner 2',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        # Create history for picking1
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Create history for picking2
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=picking2,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Filter by picking1
        history_picking1 = MoveHistory.objects.filter(picking=self.picking)
        self.assertEqual(history_picking1.count(), 1)
        self.assertEqual(history_picking1.first().picking, self.picking)
    
    def test_filtering_by_action_type(self):
        """Test filtering history records by action_type."""
        from .models import MoveHistory
        
        # Create stock_move history
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        # Create status_change history
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Create adjustment history
        MoveHistory.objects.create(
            user=self.user,
            action_type='adjustment',
            product=self.product,
            quantity=Decimal('5.00')
        )
        
        # Filter by action_type
        stock_moves = MoveHistory.objects.filter(action_type='stock_move')
        status_changes = MoveHistory.objects.filter(action_type='status_change')
        adjustments = MoveHistory.objects.filter(action_type='adjustment')
        
        self.assertEqual(stock_moves.count(), 1)
        self.assertEqual(status_changes.count(), 1)
        self.assertEqual(adjustments.count(), 1)
    
    def test_ordering_by_timestamp(self):
        """Test that history records are ordered by timestamp descending."""
        from .models import MoveHistory
        import time
        
        # Create first history record
        history1 = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        # Create second history record
        history2 = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('20.00')
        )
        
        # Get all history records (should be ordered by timestamp descending)
        all_history = MoveHistory.objects.all()
        
        # Most recent should be first
        self.assertEqual(all_history[0].id, history2.id)
        self.assertEqual(all_history[1].id, history1.id)



class WarehouseSettingsModelTest(TestCase):
    """Test WarehouseSettings model."""
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing settings
        from .models import WarehouseSettings
        WarehouseSettings.objects.all().delete()
        
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.receipt_location = Location.objects.create(name='Receipt Area', usage_type='internal')
        self.delivery_location = Location.objects.create(name='Delivery Area', usage_type='internal')
        self.adjustment_location = Location.objects.create(name='Adjustment Area', usage_type='internal')
    
    def test_singleton_pattern_only_one_record_allowed(self):
        """Test that only one settings record can exist (singleton pattern)."""
        from .models import WarehouseSettings
        
        # Create first settings record
        settings1 = WarehouseSettings.objects.create(
            low_stock_threshold=10,
            default_receipt_location=self.receipt_location
        )
        first_pk = settings1.pk
        
        # Try to create second settings record using save() method
        settings2 = WarehouseSettings(
            low_stock_threshold=20,
            default_delivery_location=self.delivery_location
        )
        settings2.save()
        
        # Should only have one record in database
        self.assertEqual(WarehouseSettings.objects.count(), 1)
        
        # The second save should have updated the first record
        settings = WarehouseSettings.objects.first()
        self.assertEqual(settings.pk, first_pk)
        self.assertEqual(settings.low_stock_threshold, 20)
        self.assertEqual(settings.default_delivery_location, self.delivery_location)
    
    def test_get_settings_creates_record_if_not_exists(self):
        """Test that get_settings() class method creates a record if it doesn't exist."""
        from .models import WarehouseSettings
        
        # Ensure no settings exist
        self.assertEqual(WarehouseSettings.objects.count(), 0)
        
        # Call get_settings()
        settings = WarehouseSettings.get_settings()
        
        # Should have created a record
        self.assertIsNotNone(settings)
        self.assertEqual(WarehouseSettings.objects.count(), 1)
        self.assertEqual(settings.pk, 1)
    
    def test_get_settings_returns_existing_record(self):
        """Test that get_settings() returns existing record without creating a new one."""
        from .models import WarehouseSettings
        
        # Create a settings record with pk=1 (as get_settings expects)
        existing_settings = WarehouseSettings.objects.create(
            pk=1,
            low_stock_threshold=15,
            default_receipt_location=self.receipt_location
        )
        
        # Call get_settings()
        settings = WarehouseSettings.get_settings()
        
        # Should return the existing record
        self.assertEqual(settings.pk, 1)
        self.assertEqual(settings.low_stock_threshold, 15)
        self.assertEqual(settings.default_receipt_location, self.receipt_location)
        
        # Should still only have one record
        self.assertEqual(WarehouseSettings.objects.count(), 1)
    
    def test_default_values_for_all_fields(self):
        """Test that default values are set correctly for all fields."""
        from .models import WarehouseSettings
        
        # Create settings with minimal data
        settings = WarehouseSettings.objects.create()
        
        # Check default values
        self.assertEqual(settings.low_stock_threshold, 10)
        self.assertIsNone(settings.default_receipt_location)
        self.assertIsNone(settings.default_delivery_location)
        self.assertIsNone(settings.default_adjustment_location)
        self.assertIsNone(settings.updated_by)
        self.assertIsNotNone(settings.updated_at)
    
    def test_save_method_enforces_singleton(self):
        """Test that save() method enforces singleton pattern."""
        from .models import WarehouseSettings
        
        # Create first settings
        settings1 = WarehouseSettings.objects.create(
            low_stock_threshold=10
        )
        first_pk = settings1.pk
        
        # Create another settings instance (should update existing)
        settings2 = WarehouseSettings()
        settings2.low_stock_threshold = 25
        settings2.default_receipt_location = self.receipt_location
        settings2.save()
        
        # Should still only have one record
        self.assertEqual(WarehouseSettings.objects.count(), 1)
        
        # The pk should be the same as the first one
        self.assertEqual(settings2.pk, first_pk)
        
        # Verify the values were updated
        updated_settings = WarehouseSettings.objects.first()
        self.assertEqual(updated_settings.low_stock_threshold, 25)
        self.assertEqual(updated_settings.default_receipt_location, self.receipt_location)


class MoveHistorySerializerTest(TestCase):
    """Test MoveHistorySerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
        
        from django.utils import timezone
        self.picking = Picking.objects.create(
            reference='TEST-001',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
    
    def test_serialization_with_all_related_objects(self):
        """Test serialization of history record with all related objects."""
        from .models import MoveHistory
        from .serializers import MoveHistorySerializer
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            notes='Test move'
        )
        
        serializer = MoveHistorySerializer(history)
        data = serializer.data
        
        # Verify all fields are present
        self.assertIn('id', data)
        self.assertIn('timestamp', data)
        self.assertIn('user', data)
        self.assertIn('action_type', data)
        self.assertIn('picking', data)
        self.assertIn('product', data)
        self.assertIn('quantity', data)
        self.assertIn('source_location', data)
        self.assertIn('destination_location', data)
        self.assertIn('notes', data)
        
        # Verify values
        self.assertEqual(data['action_type'], 'stock_move')
        self.assertEqual(data['quantity'], '10.00')
        self.assertEqual(data['notes'], 'Test move')
    
    def test_nested_user_serializer(self):
        """Test nested user serializer."""
        from .models import MoveHistory
        from .serializers import MoveHistorySerializer
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        serializer = MoveHistorySerializer(history)
        data = serializer.data
        
        # Verify nested user data
        self.assertIsNotNone(data['user'])
        self.assertEqual(data['user']['id'], self.user.id)
        self.assertEqual(data['user']['login_id'], 'testuser')
    
    def test_nested_product_serializer(self):
        """Test nested product serializer."""
        from .models import MoveHistory
        from .serializers import MoveHistorySerializer
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00')
        )
        
        serializer = MoveHistorySerializer(history)
        data = serializer.data
        
        # Verify nested product data
        self.assertIsNotNone(data['product'])
        self.assertEqual(data['product']['id'], self.product.id)
        self.assertEqual(data['product']['sku'], 'PROD-001')
        self.assertEqual(data['product']['name'], 'Test Product')
    
    def test_nested_location_serializers(self):
        """Test nested location serializers."""
        from .models import MoveHistory
        from .serializers import MoveHistorySerializer
        
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location
        )
        
        serializer = MoveHistorySerializer(history)
        data = serializer.data
        
        # Verify nested source location data
        self.assertIsNotNone(data['source_location'])
        self.assertEqual(data['source_location']['id'], self.source_location.id)
        self.assertEqual(data['source_location']['name'], 'Source')
        
        # Verify nested destination location data
        self.assertIsNotNone(data['destination_location'])
        self.assertEqual(data['destination_location']['id'], self.dest_location.id)
        self.assertEqual(data['destination_location']['name'], 'Destination')
    
    def test_read_only_enforcement(self):
        """Test that all fields are read-only."""
        from .serializers import MoveHistorySerializer
        
        serializer = MoveHistorySerializer()
        
        # All fields should be read-only
        read_only_fields = [
            'id', 'timestamp', 'user', 'action_type', 'action_type_display',
            'action_display', 'picking', 'product', 'quantity',
            'source_location', 'destination_location',
            'old_status', 'new_status', 'notes'
        ]
        
        for field_name in read_only_fields:
            field = serializer.fields.get(field_name)
            self.assertIsNotNone(field, f"Field {field_name} not found")
            self.assertTrue(field.read_only, f"Field {field_name} is not read-only")



class WarehouseSettingsSerializerTest(TestCase):
    """Test WarehouseSettingsSerializer."""
    
    def setUp(self):
        """Set up test data."""
        from .models import WarehouseSettings
        WarehouseSettings.objects.all().delete()
        
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.receipt_location = Location.objects.create(name='Receipt Area', usage_type='internal')
        self.delivery_location = Location.objects.create(name='Delivery Area', usage_type='internal')
        self.adjustment_location = Location.objects.create(name='Adjustment Area', usage_type='internal')
    
    def test_serialization_with_all_fields(self):
        """Test serialization with all fields populated."""
        from .models import WarehouseSettings
        from .serializers import WarehouseSettingsSerializer
        
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=15,
            default_receipt_location=self.receipt_location,
            default_delivery_location=self.delivery_location,
            default_adjustment_location=self.adjustment_location,
            updated_by=self.user
        )
        
        serializer = WarehouseSettingsSerializer(settings)
        data = serializer.data
        
        # Verify all fields are present
        self.assertIn('id', data)
        self.assertIn('low_stock_threshold', data)
        self.assertIn('default_receipt_location', data)
        self.assertIn('default_delivery_location', data)
        self.assertIn('default_adjustment_location', data)
        self.assertIn('updated_at', data)
        self.assertIn('updated_by', data)
        
        # Verify values
        self.assertEqual(data['low_stock_threshold'], 15)
        self.assertIsNotNone(data['default_receipt_location'])
        self.assertIsNotNone(data['default_delivery_location'])
        self.assertIsNotNone(data['default_adjustment_location'])
        self.assertIsNotNone(data['updated_by'])
    
    def test_nested_location_serializers(self):
        """Test nested location serializers."""
        from .models import WarehouseSettings
        from .serializers import WarehouseSettingsSerializer
        
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=10,
            default_receipt_location=self.receipt_location,
            default_delivery_location=self.delivery_location,
            default_adjustment_location=self.adjustment_location
        )
        
        serializer = WarehouseSettingsSerializer(settings)
        data = serializer.data
        
        # Verify nested receipt location
        self.assertIsNotNone(data['default_receipt_location'])
        self.assertEqual(data['default_receipt_location']['id'], self.receipt_location.id)
        self.assertEqual(data['default_receipt_location']['name'], 'Receipt Area')
        
        # Verify nested delivery location
        self.assertIsNotNone(data['default_delivery_location'])
        self.assertEqual(data['default_delivery_location']['id'], self.delivery_location.id)
        self.assertEqual(data['default_delivery_location']['name'], 'Delivery Area')
        
        # Verify nested adjustment location
        self.assertIsNotNone(data['default_adjustment_location'])
        self.assertEqual(data['default_adjustment_location']['id'], self.adjustment_location.id)
        self.assertEqual(data['default_adjustment_location']['name'], 'Adjustment Area')
    
    def test_validation_of_location_references(self):
        """Test validation of location references."""
        from .serializers import WarehouseSettingsSerializer
        
        # Test with invalid location ID
        data = {
            'low_stock_threshold': 10,
            'default_receipt_location_id': 99999  # Invalid location ID
        }
        
        serializer = WarehouseSettingsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('default_receipt_location_id', serializer.errors)
    
    def test_validation_of_negative_threshold(self):
        """Test validation of negative threshold."""
        from .serializers import WarehouseSettingsSerializer
        
        # Test with negative threshold
        data = {
            'low_stock_threshold': -5
        }
        
        serializer = WarehouseSettingsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('low_stock_threshold', serializer.errors)
    
    def test_update_with_valid_location_references(self):
        """Test updating settings with valid location references."""
        from .models import WarehouseSettings
        from .serializers import WarehouseSettingsSerializer
        
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=10
        )
        
        # Update with valid location references
        data = {
            'low_stock_threshold': 20,
            'default_receipt_location_id': self.receipt_location.id,
            'default_delivery_location_id': self.delivery_location.id
        }
        
        serializer = WarehouseSettingsSerializer(settings, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_settings = serializer.save()
        self.assertEqual(updated_settings.low_stock_threshold, 20)
        self.assertEqual(updated_settings.default_receipt_location, self.receipt_location)
        self.assertEqual(updated_settings.default_delivery_location, self.delivery_location)



class PickingSerializerNestedWriteTest(TestCase):
    """Test nested write functionality in PickingSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )
    
    def test_serialization_with_nested_stock_moves(self):
        """Test serialization with nested stock_moves."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        # Create picking with stock moves
        picking = Picking.objects.create(
            reference='REC-001',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('5.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        serializer = PickingSerializer(picking)
        data = serializer.data
        
        # Verify stock_moves are included
        self.assertIn('stock_moves', data)
        self.assertEqual(len(data['stock_moves']), 2)
        self.assertEqual(data['stock_moves_count'], 2)
    
    def test_validation_of_empty_stock_moves_array(self):
        """Test validation of empty stock_moves array."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        data = {
            'reference': 'REC-002',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': []  # Empty array
        }
        
        serializer = PickingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_moves', serializer.errors)
    
    def test_validation_of_invalid_product_id(self):
        """Test validation of invalid product ID."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        data = {
            'reference': 'REC-003',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': 99999,  # Invalid product ID
                    'quantity': '10.00'
                }
            ]
        }
        
        serializer = PickingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_moves', serializer.errors)
    
    def test_validation_of_negative_quantity(self):
        """Test validation of negative quantity."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        data = {
            'reference': 'REC-004',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '-10.00'  # Negative quantity
                }
            ]
        }
        
        serializer = PickingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('stock_moves', serializer.errors)
    
    def test_create_with_nested_stock_moves(self):
        """Test creating picking with nested stock_moves."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        data = {
            'reference': 'REC-005',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'notes': 'Batch A'
                },
                {
                    'product': self.product2.id,
                    'quantity': '5.00',
                    'notes': 'Batch B'
                }
            ]
        }
        
        serializer = PickingSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        picking = serializer.save(created_by=self.user)
        
        # Verify picking was created
        self.assertEqual(picking.reference, 'REC-005')
        
        # Verify stock moves were created
        self.assertEqual(picking.stock_moves.count(), 2)
        
        # Verify stock move details
        move1 = picking.stock_moves.get(product=self.product1)
        self.assertEqual(move1.quantity, Decimal('10.00'))
        self.assertEqual(move1.notes, 'Batch A')
        self.assertEqual(move1.source_location, self.source_location)
        self.assertEqual(move1.destination_location, self.dest_location)
        self.assertEqual(move1.status, 'draft')
        
        move2 = picking.stock_moves.get(product=self.product2)
        self.assertEqual(move2.quantity, Decimal('5.00'))
        self.assertEqual(move2.notes, 'Batch B')
    
    def test_update_with_nested_stock_moves(self):
        """Test updating picking with nested stock_moves."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        # Create initial picking with one stock move
        picking = Picking.objects.create(
            reference='REC-006',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        existing_move = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with modified and new stock moves
        data = {
            'reference': 'REC-006',
            'partner': 'Test Supplier Updated',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'confirmed',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': existing_move.id,
                    'product': self.product1.id,
                    'quantity': '15.00',  # Updated quantity
                    'notes': 'Updated'
                },
                {
                    # New move without id
                    'product': self.product2.id,
                    'quantity': '20.00',
                    'notes': 'New move'
                }
            ]
        }
        
        serializer = PickingSerializer(picking, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_picking = serializer.save()
        
        # Verify picking was updated
        self.assertEqual(updated_picking.partner, 'Test Supplier Updated')
        self.assertEqual(updated_picking.status, 'confirmed')
        
        # Verify stock moves
        self.assertEqual(updated_picking.stock_moves.count(), 2)
        
        # Verify existing move was updated
        updated_move = StockMove.objects.get(id=existing_move.id)
        self.assertEqual(updated_move.quantity, Decimal('15.00'))
        self.assertEqual(updated_move.notes, 'Updated')
        
        # Verify new move was created
        new_move = updated_picking.stock_moves.get(product=self.product2)
        self.assertEqual(new_move.quantity, Decimal('20.00'))
        self.assertEqual(new_move.notes, 'New move')
    
    def test_update_removes_stock_moves_not_in_list(self):
        """Test that updating removes stock moves not included in the update."""
        from django.utils import timezone
        from .serializers import PickingSerializer
        
        # Create picking with two stock moves
        picking = Picking.objects.create(
            reference='REC-007',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now()
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        move2 = StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('5.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with only move1 (move2 should be removed)
        data = {
            'reference': 'REC-007',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '10.00'
                }
            ]
        }
        
        serializer = PickingSerializer(picking, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_picking = serializer.save()
        
        # Verify only one stock move remains
        self.assertEqual(updated_picking.stock_moves.count(), 1)
        self.assertTrue(updated_picking.stock_moves.filter(id=move1.id).exists())
        self.assertFalse(StockMove.objects.filter(id=move2.id).exists())


class StockMoveSignalTest(TestCase):
    """Test StockMove signal for history tracking."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Test Product',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
        
        from django.utils import timezone
        self.picking = Picking.objects.create(
            reference='TEST-001',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
    
    def test_history_record_created_when_move_status_changes_to_done(self):
        """Test history record created when move status changes to 'done'."""
        from .models import MoveHistory
        
        # Create stock move with draft status
        stock_move = StockMove.objects.create(
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # No history should exist yet
        initial_count = MoveHistory.objects.filter(action_type='stock_move').count()
        
        # Change status to 'done'
        stock_move.status = 'done'
        stock_move.save()
        
        # Verify history record was created
        history_records = MoveHistory.objects.filter(action_type='stock_move')
        self.assertEqual(history_records.count(), initial_count + 1)
        
        # Verify the history record
        history = history_records.latest('timestamp')
        self.assertEqual(history.action_type, 'stock_move')
        self.assertEqual(history.picking, self.picking)
        self.assertEqual(history.product, self.product)
        self.assertEqual(history.quantity, Decimal('10.00'))
        self.assertEqual(history.source_location, self.source_location)
        self.assertEqual(history.destination_location, self.dest_location)
    
    def test_history_record_contains_correct_product_quantity_locations(self):
        """Test history record contains correct product, quantity, and locations."""
        from .models import MoveHistory
        
        # Create and validate stock move
        stock_move = StockMove.objects.create(
            picking=self.picking,
            product=self.product,
            quantity=Decimal('25.50'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='done',
            notes='Test notes'
        )
        
        # Get the history record
        history = MoveHistory.objects.filter(
            action_type='stock_move',
            product=self.product
        ).latest('timestamp')
        
        # Verify all details are correct
        self.assertEqual(history.product, self.product)
        self.assertEqual(history.quantity, Decimal('25.50'))
        self.assertEqual(history.source_location, self.source_location)
        self.assertEqual(history.destination_location, self.dest_location)
        self.assertIn('Test notes', history.notes)
    
    def test_user_attribution_in_history_record(self):
        """Test user attribution in history record."""
        from .models import MoveHistory
        
        # Create stock move with status 'done'
        stock_move = StockMove.objects.create(
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='done'
        )
        
        # Get the history record
        history = MoveHistory.objects.filter(
            action_type='stock_move',
            product=self.product
        ).latest('timestamp')
        
        # Verify user is attributed from picking.created_by
        self.assertEqual(history.user, self.user)
    
    def test_no_history_created_for_other_status_changes(self):
        """Test no history created for status changes other than 'done'."""
        from .models import MoveHistory
        
        # Create stock move with draft status
        stock_move = StockMove.objects.create(
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        initial_count = MoveHistory.objects.filter(action_type='stock_move').count()
        
        # Change to confirmed (not 'done')
        stock_move.status = 'confirmed'
        stock_move.save()
        
        # No new history should be created
        self.assertEqual(
            MoveHistory.objects.filter(action_type='stock_move').count(),
            initial_count
        )
        
        # Change to assigned (not 'done')
        stock_move.status = 'assigned'
        stock_move.save()
        
        # Still no new history
        self.assertEqual(
            MoveHistory.objects.filter(action_type='stock_move').count(),
            initial_count
        )
        
        # Change to cancelled (not 'done')
        stock_move.status = 'cancelled'
        stock_move.save()
        
        # Still no new history
        self.assertEqual(
            MoveHistory.objects.filter(action_type='stock_move').count(),
            initial_count
        )
    
    def test_no_duplicate_history_on_subsequent_saves(self):
        """Test that no duplicate history records are created on subsequent saves."""
        from .models import MoveHistory
        
        # Create stock move with status 'done'
        stock_move = StockMove.objects.create(
            picking=self.picking,
            product=self.product,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='done'
        )
        
        # Count history records
        initial_count = MoveHistory.objects.filter(
            action_type='stock_move',
            product=self.product
        ).count()
        
        # Save again without changing status
        stock_move.notes = 'Updated notes'
        stock_move.save()
        
        # Should not create duplicate history
        final_count = MoveHistory.objects.filter(
            action_type='stock_move',
            product=self.product
        ).count()
        
        self.assertEqual(final_count, initial_count)


class PickingSignalTest(TestCase):
    """Test Picking signal for status change history tracking."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
    
    def test_history_record_created_when_picking_status_changes(self):
        """Test history record created when picking status changes."""
        from django.utils import timezone
        from .models import MoveHistory
        
        # Create picking with draft status
        picking = Picking.objects.create(
            reference='TEST-001',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        initial_count = MoveHistory.objects.filter(action_type='status_change').count()
        
        # Change status
        picking.status = 'confirmed'
        picking.save()
        
        # Verify history record was created
        history_records = MoveHistory.objects.filter(action_type='status_change')
        self.assertEqual(history_records.count(), initial_count + 1)
        
        # Verify the history record
        history = history_records.latest('timestamp')
        self.assertEqual(history.action_type, 'status_change')
        self.assertEqual(history.picking, picking)
        self.assertEqual(history.old_status, 'draft')
        self.assertEqual(history.new_status, 'confirmed')
    
    def test_old_status_and_new_status_captured_correctly(self):
        """Test old_status and new_status captured correctly."""
        from django.utils import timezone
        from .models import MoveHistory
        
        # Create picking
        picking = Picking.objects.create(
            reference='TEST-002',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        # Change from draft to confirmed
        picking.status = 'confirmed'
        picking.save()
        
        history1 = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).latest('timestamp')
        
        self.assertEqual(history1.old_status, 'draft')
        self.assertEqual(history1.new_status, 'confirmed')
        
        # Change from confirmed to assigned
        picking.status = 'assigned'
        picking.save()
        
        history2 = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).latest('timestamp')
        
        self.assertEqual(history2.old_status, 'confirmed')
        self.assertEqual(history2.new_status, 'assigned')
        
        # Change from assigned to done
        picking.status = 'done'
        picking.save()
        
        history3 = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).latest('timestamp')
        
        self.assertEqual(history3.old_status, 'assigned')
        self.assertEqual(history3.new_status, 'done')
    
    def test_user_attribution_in_picking_history_record(self):
        """Test user attribution in history record."""
        from django.utils import timezone
        from .models import MoveHistory
        
        # Create picking
        picking = Picking.objects.create(
            reference='TEST-003',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        # Change status
        picking.status = 'confirmed'
        picking.save()
        
        # Get the history record
        history = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).latest('timestamp')
        
        # Verify user is attributed from picking.created_by
        self.assertEqual(history.user, self.user)
    
    def test_no_history_created_when_status_unchanged(self):
        """Test no history created when status unchanged."""
        from django.utils import timezone
        from .models import MoveHistory
        
        # Create picking
        picking = Picking.objects.create(
            reference='TEST-004',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        initial_count = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).count()
        
        # Save without changing status
        picking.partner = 'Updated Partner'
        picking.save()
        
        # No new history should be created
        final_count = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).count()
        
        self.assertEqual(final_count, initial_count)
    
    def test_no_history_created_on_initial_creation(self):
        """Test no history created when picking is initially created."""
        from django.utils import timezone
        from .models import MoveHistory
        
        initial_count = MoveHistory.objects.filter(action_type='status_change').count()
        
        # Create new picking
        picking = Picking.objects.create(
            reference='TEST-005',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        # No history should be created on initial creation
        final_count = MoveHistory.objects.filter(action_type='status_change').count()
        self.assertEqual(final_count, initial_count)
    
    def test_multiple_status_changes_create_multiple_history_records(self):
        """Test multiple status changes create separate history records."""
        from django.utils import timezone
        from .models import MoveHistory
        
        # Create picking
        picking = Picking.objects.create(
            reference='TEST-006',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        initial_count = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).count()
        
        # Make multiple status changes
        picking.status = 'confirmed'
        picking.save()
        
        picking.status = 'assigned'
        picking.save()
        
        picking.status = 'in_progress'
        picking.save()
        
        picking.status = 'done'
        picking.save()
        
        # Should have 4 new history records
        final_count = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).count()
        
        self.assertEqual(final_count, initial_count + 4)
        
        # Verify the sequence of status changes
        history_records = MoveHistory.objects.filter(
            action_type='status_change',
            picking=picking
        ).order_by('timestamp')
        
        status_changes = [
            (h.old_status, h.new_status) for h in history_records
        ]
        
        expected_changes = [
            ('draft', 'confirmed'),
            ('confirmed', 'assigned'),
            ('assigned', 'in_progress'),
            ('in_progress', 'done')
        ]
        
        self.assertEqual(status_changes, expected_changes)



class NestedPickingCreationIntegrationTest(APITestCase):
    """Integration tests for nested picking creation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        self.product3 = Product.objects.create(
            sku='PROD-003',
            name='Product 3',
            category=self.category,
            cost=Decimal('20.00'),
            price=Decimal('40.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        self.operation_type = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )

    
    def test_successful_creation_of_picking_with_multiple_stock_moves(self):
        """Test successful creation of picking with multiple stock moves."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-INT-001',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'notes': 'First product'
                },
                {
                    'product': self.product2.id,
                    'quantity': '20.00',
                    'notes': 'Second product'
                },
                {
                    'product': self.product3.id,
                    'quantity': '30.00',
                    'notes': 'Third product'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify picking was created
        self.assertEqual(Picking.objects.count(), 1)
        picking = Picking.objects.first()
        self.assertEqual(picking.reference, 'REC-INT-001')
        self.assertEqual(picking.partner, 'Test Supplier')
        
        # Verify all stock moves were created
        self.assertEqual(picking.stock_moves.count(), 3)
        self.assertEqual(StockMove.objects.count(), 3)

    
    def test_all_moves_created_with_correct_data(self):
        """Test all moves are created with correct data."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-INT-002',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '15.50',
                    'notes': 'Batch A123'
                },
                {
                    'product': self.product2.id,
                    'quantity': '25.75',
                    'notes': 'Batch B456'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        picking = Picking.objects.get(reference='REC-INT-002')
        
        # Verify first move
        move1 = picking.stock_moves.get(product=self.product1)
        self.assertEqual(move1.quantity, Decimal('15.50'))
        self.assertEqual(move1.notes, 'Batch A123')
        self.assertEqual(move1.product, self.product1)
        
        # Verify second move
        move2 = picking.stock_moves.get(product=self.product2)
        self.assertEqual(move2.quantity, Decimal('25.75'))
        self.assertEqual(move2.notes, 'Batch B456')
        self.assertEqual(move2.product, self.product2)

    
    def test_source_destination_locations_inherited_from_picking(self):
        """Test source/destination locations inherited from picking."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-INT-003',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00'
                },
                {
                    'product': self.product2.id,
                    'quantity': '20.00'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        picking = Picking.objects.get(reference='REC-INT-003')
        
        # Verify all moves inherit locations from picking
        for move in picking.stock_moves.all():
            self.assertEqual(move.source_location, self.source_location)
            self.assertEqual(move.destination_location, self.dest_location)

    
    def test_transaction_rollback_on_validation_error(self):
        """Test transaction rollback on validation error."""
        from django.utils import timezone
        
        initial_picking_count = Picking.objects.count()
        initial_move_count = StockMove.objects.count()
        
        # Create data with one valid and one invalid product
        data = {
            'reference': 'REC-INT-004',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00'
                },
                {
                    'product': 99999,  # Invalid product ID
                    'quantity': '20.00'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no partial data was created (transaction rolled back)
        self.assertEqual(Picking.objects.count(), initial_picking_count)
        self.assertEqual(StockMove.objects.count(), initial_move_count)

    
    def test_error_response_format_for_failed_validation(self):
        """Test error response format for failed validation."""
        from django.utils import timezone
        
        # Test with invalid product
        data = {
            'reference': 'REC-INT-005',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': 99999,
                    'quantity': '10.00'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
        
        # Test with empty stock_moves
        data['stock_moves'] = []
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
        
        # Test with negative quantity
        data['stock_moves'] = [
            {
                'product': self.product1.id,
                'quantity': '-10.00'
            }
        ]
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)



class NestedPickingUpdateIntegrationTest(APITestCase):
    """Integration tests for nested picking updates."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        self.product3 = Product.objects.create(
            sku='PROD-003',
            name='Product 3',
            category=self.category,
            cost=Decimal('20.00'),
            price=Decimal('40.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        self.operation_type = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )

    
    def test_adding_new_stock_moves_to_existing_picking(self):
        """Test adding new stock moves to existing picking."""
        from django.utils import timezone
        
        # Create initial picking with one stock move
        picking = Picking.objects.create(
            reference='REC-UPD-001',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        existing_move = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with existing move plus new moves
        data = {
            'reference': 'REC-UPD-001',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': existing_move.id,
                    'product': self.product1.id,
                    'quantity': '10.00'
                },
                {
                    'product': self.product2.id,
                    'quantity': '20.00',
                    'notes': 'New move 1'
                },
                {
                    'product': self.product3.id,
                    'quantity': '30.00',
                    'notes': 'New move 2'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify picking now has 3 moves
        picking.refresh_from_db()
        self.assertEqual(picking.stock_moves.count(), 3)
        
        # Verify new moves were created
        self.assertTrue(picking.stock_moves.filter(product=self.product2).exists())
        self.assertTrue(picking.stock_moves.filter(product=self.product3).exists())

    
    def test_updating_existing_stock_moves(self):
        """Test updating existing stock moves."""
        from django.utils import timezone
        
        # Create picking with two stock moves
        picking = Picking.objects.create(
            reference='REC-UPD-002',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            notes='Original note 1'
        )
        
        move2 = StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('20.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            notes='Original note 2'
        )
        
        # Update both moves with new quantities and notes
        data = {
            'reference': 'REC-UPD-002',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '15.00',
                    'notes': 'Updated note 1'
                },
                {
                    'id': move2.id,
                    'product': self.product2.id,
                    'quantity': '25.00',
                    'notes': 'Updated note 2'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify moves were updated
        move1.refresh_from_db()
        self.assertEqual(move1.quantity, Decimal('15.00'))
        self.assertEqual(move1.notes, 'Updated note 1')
        
        move2.refresh_from_db()
        self.assertEqual(move2.quantity, Decimal('25.00'))
        self.assertEqual(move2.notes, 'Updated note 2')

    
    def test_removing_stock_moves_from_picking(self):
        """Test removing stock moves from picking."""
        from django.utils import timezone
        
        # Create picking with three stock moves
        picking = Picking.objects.create(
            reference='REC-UPD-003',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        move2 = StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('20.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        move3 = StockMove.objects.create(
            picking=picking,
            product=self.product3,
            quantity=Decimal('30.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with only move1 and move2 (remove move3)
        data = {
            'reference': 'REC-UPD-003',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '10.00'
                },
                {
                    'id': move2.id,
                    'product': self.product2.id,
                    'quantity': '20.00'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify picking now has only 2 moves
        picking.refresh_from_db()
        self.assertEqual(picking.stock_moves.count(), 2)
        
        # Verify move3 was deleted
        self.assertFalse(StockMove.objects.filter(id=move3.id).exists())
        
        # Verify move1 and move2 still exist
        self.assertTrue(StockMove.objects.filter(id=move1.id).exists())
        self.assertTrue(StockMove.objects.filter(id=move2.id).exists())

    
    def test_transaction_rollback_on_update_failure(self):
        """Test transaction rollback on update failure."""
        from django.utils import timezone
        
        # Create picking with one stock move
        picking = Picking.objects.create(
            reference='REC-UPD-004',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        original_quantity = move1.quantity
        original_partner = picking.partner
        
        # Try to update with invalid product in new move
        data = {
            'reference': 'REC-UPD-004',
            'partner': 'Updated Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '50.00'
                },
                {
                    'product': 99999,  # Invalid product
                    'quantity': '20.00'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no changes were made (transaction rolled back)
        picking.refresh_from_db()
        self.assertEqual(picking.partner, original_partner)
        
        move1.refresh_from_db()
        self.assertEqual(move1.quantity, original_quantity)
        
        # Verify no new moves were created
        self.assertEqual(picking.stock_moves.count(), 1)

    
    def test_complex_update_add_update_remove_simultaneously(self):
        """Test complex update: add, update, and remove moves simultaneously."""
        from django.utils import timezone
        
        # Create picking with two stock moves
        picking = Picking.objects.create(
            reference='REC-UPD-005',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            notes='Keep and update'
        )
        
        move2 = StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('20.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            notes='Remove this'
        )
        
        # Update: keep move1 with changes, remove move2, add move for product3
        data = {
            'reference': 'REC-UPD-005',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '15.00',
                    'notes': 'Updated'
                },
                {
                    'product': self.product3.id,
                    'quantity': '30.00',
                    'notes': 'New move'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify picking has 2 moves
        picking.refresh_from_db()
        self.assertEqual(picking.stock_moves.count(), 2)
        
        # Verify move1 was updated
        move1.refresh_from_db()
        self.assertEqual(move1.quantity, Decimal('15.00'))
        self.assertEqual(move1.notes, 'Updated')
        
        # Verify move2 was deleted
        self.assertFalse(StockMove.objects.filter(id=move2.id).exists())
        
        # Verify new move for product3 was created
        new_move = picking.stock_moves.get(product=self.product3)
        self.assertEqual(new_move.quantity, Decimal('30.00'))
        self.assertEqual(new_move.notes, 'New move')


class MoveHistoryAPITest(APITestCase):
    """Test MoveHistory API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Test Operation',
            code='internal',
            sequence_prefix='TEST'
        )
        
        from django.utils import timezone
        self.picking = Picking.objects.create(
            reference='TEST-001',
            partner='Test Partner',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
    
    def test_get_move_history_returns_paginated_list(self):
        """Test GET /move-history/ returns paginated list."""
        from .models import MoveHistory
        
        # Create multiple history records
        for i in range(15):
            MoveHistory.objects.create(
                user=self.user,
                action_type='stock_move',
                product=self.product1,
                quantity=Decimal(f'{i+1}.00')
            )
        
        response = self.client.get('/api/inventory/move-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response contains data (either paginated or list)
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertIn('count', response.data)
            self.assertEqual(response.data['count'], 15)
        else:
            # Non-paginated list response
            self.assertIsInstance(response.data, list)
            self.assertEqual(len(response.data), 15)
    
    def test_filter_by_product(self):
        """Test filtering by product."""
        from .models import MoveHistory
        
        # Create history for product1
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Create history for product2
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product2,
            quantity=Decimal('20.00')
        )
        
        # Filter by product1
        response = self.client.get(f'/api/inventory/move-history/?product={self.product1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
        else:
            results = response.data
            self.assertEqual(len(results), 1)
        
        self.assertEqual(results[0]['product']['id'], self.product1.id)
    
    def test_filter_by_picking(self):
        """Test filtering by picking."""
        from .models import MoveHistory
        from django.utils import timezone
        
        picking2 = Picking.objects.create(
            reference='TEST-002',
            partner='Test Partner 2',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        # Create history for picking1
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Create history for picking2
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=picking2,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Filter by picking1
        response = self.client.get(f'/api/inventory/move-history/?picking={self.picking.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
        else:
            results = response.data
            self.assertEqual(len(results), 1)
        
        self.assertEqual(results[0]['picking']['id'], self.picking.id)
    
    def test_filter_by_action_type(self):
        """Test filtering by action_type."""
        from .models import MoveHistory
        
        # Create stock_move history
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Create status_change history
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Filter by stock_move
        response = self.client.get('/api/inventory/move-history/?action_type=stock_move')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
        else:
            results = response.data
            self.assertEqual(len(results), 1)
        
        self.assertEqual(results[0]['action_type'], 'stock_move')
        
        # Filter by status_change
        response = self.client.get('/api/inventory/move-history/?action_type=status_change')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
        else:
            results = response.data
            self.assertEqual(len(results), 1)
        
        self.assertEqual(results[0]['action_type'], 'status_change')
    
    def test_filter_by_user(self):
        """Test filtering by user."""
        from .models import MoveHistory
        
        user2 = User.objects.create_user(
            login_id='testuser2',
            email='test2@example.com',
            password='TestPass@123'
        )
        
        # Create history for user1
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Create history for user2
        MoveHistory.objects.create(
            user=user2,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('20.00')
        )
        
        # Filter by user1
        response = self.client.get(f'/api/inventory/move-history/?user={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
        else:
            results = response.data
            self.assertEqual(len(results), 1)
        
        self.assertEqual(results[0]['user']['id'], self.user.id)
    
    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        from .models import MoveHistory
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Create history record
        history = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Filter with date range that includes the record
        # Format dates properly for URL
        date_from = yesterday.strftime('%Y-%m-%dT%H:%M:%S')
        date_to = tomorrow.strftime('%Y-%m-%dT%H:%M:%S')
        response = self.client.get(
            f'/api/inventory/move-history/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(response.data['count'], 1)
        else:
            self.assertEqual(len(response.data), 1)
        
        # Filter with date range that excludes the record
        past_date = yesterday - timedelta(days=2)
        date_from = past_date.strftime('%Y-%m-%dT%H:%M:%S')
        date_to = yesterday.strftime('%Y-%m-%dT%H:%M:%S')
        response = self.client.get(
            f'/api/inventory/move-history/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(response.data['count'], 0)
        else:
            self.assertEqual(len(response.data), 0)
    
    def test_search_by_picking_reference(self):
        """Test search by picking reference."""
        from .models import MoveHistory
        
        # Create history with picking
        MoveHistory.objects.create(
            user=self.user,
            action_type='status_change',
            picking=self.picking,
            old_status='draft',
            new_status='confirmed'
        )
        
        # Search by picking reference
        response = self.client.get('/api/inventory/move-history/?search=TEST-001')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['picking']['reference'], 'TEST-001')
    
    def test_search_by_product_sku(self):
        """Test search by product SKU."""
        from .models import MoveHistory
        
        # Create history with product
        MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Search by product SKU
        response = self.client.get('/api/inventory/move-history/?search=PROD-001')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['product']['sku'], 'PROD-001')
    
    def test_authentication_requirement(self):
        """Test authentication requirement."""
        # Logout
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/inventory/move-history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_ordering_by_timestamp_descending(self):
        """Test ordering by timestamp descending."""
        from .models import MoveHistory
        import time
        
        # Create first history record
        history1 = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('10.00')
        )
        
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        
        # Create second history record
        history2 = MoveHistory.objects.create(
            user=self.user,
            action_type='stock_move',
            product=self.product1,
            quantity=Decimal('20.00')
        )
        
        # Get all history records
        response = self.client.get('/api/inventory/move-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Most recent should be first
        results = response.data['results']
        self.assertEqual(results[0]['id'], history2.id)
        self.assertEqual(results[1]['id'], history1.id)



class WarehouseSettingsAPITest(APITestCase):
    """Test WarehouseSettings API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        from .models import WarehouseSettings
        WarehouseSettings.objects.all().delete()
        
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.receipt_location = Location.objects.create(name='Receipt Area', usage_type='internal')
        self.delivery_location = Location.objects.create(name='Delivery Area', usage_type='internal')
        self.adjustment_location = Location.objects.create(name='Adjustment Area', usage_type='internal')
    
    def test_get_settings_returns_current_settings(self):
        """Test GET /settings/ returns current settings."""
        from .models import WarehouseSettings
        
        # Create settings
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=15,
            default_receipt_location=self.receipt_location,
            default_delivery_location=self.delivery_location,
            updated_by=self.user
        )
        
        response = self.client.get('/api/inventory/settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response is not an array (singleton pattern)
        self.assertNotIn('results', response.data)
        self.assertNotIn('count', response.data)
        
        # Verify settings data
        self.assertEqual(response.data['id'], settings.id)
        self.assertEqual(response.data['low_stock_threshold'], 15)
        self.assertIsNotNone(response.data['default_receipt_location'])
        self.assertEqual(response.data['default_receipt_location']['id'], self.receipt_location.id)
        self.assertIsNotNone(response.data['default_delivery_location'])
        self.assertEqual(response.data['default_delivery_location']['id'], self.delivery_location.id)
    
    def test_get_settings_creates_if_not_exists(self):
        """Test GET /settings/ creates settings if they don't exist."""
        from .models import WarehouseSettings
        
        # Ensure no settings exist
        self.assertEqual(WarehouseSettings.objects.count(), 0)
        
        response = self.client.get('/api/inventory/settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify settings were created
        self.assertEqual(WarehouseSettings.objects.count(), 1)
        self.assertEqual(response.data['low_stock_threshold'], 10)  # Default value
    
    def test_put_settings_updates_all_fields(self):
        """Test PUT /settings/ updates all fields."""
        from .models import WarehouseSettings
        
        # Create initial settings
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=10
        )
        
        # Update all fields
        data = {
            'low_stock_threshold': 25,
            'default_receipt_location_id': self.receipt_location.id,
            'default_delivery_location_id': self.delivery_location.id,
            'default_adjustment_location_id': self.adjustment_location.id
        }
        
        response = self.client.put('/api/inventory/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all fields were updated
        self.assertEqual(response.data['low_stock_threshold'], 25)
        self.assertEqual(response.data['default_receipt_location']['id'], self.receipt_location.id)
        self.assertEqual(response.data['default_delivery_location']['id'], self.delivery_location.id)
        self.assertEqual(response.data['default_adjustment_location']['id'], self.adjustment_location.id)
        
        # Verify in database
        settings.refresh_from_db()
        self.assertEqual(settings.low_stock_threshold, 25)
        self.assertEqual(settings.default_receipt_location, self.receipt_location)
        self.assertEqual(settings.default_delivery_location, self.delivery_location)
        self.assertEqual(settings.default_adjustment_location, self.adjustment_location)
    
    def test_patch_settings_updates_partial_fields(self):
        """Test PATCH /settings/ updates partial fields."""
        from .models import WarehouseSettings
        
        # Create initial settings
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=10,
            default_receipt_location=self.receipt_location
        )
        
        # Update only threshold
        data = {
            'low_stock_threshold': 20
        }
        
        response = self.client.patch('/api/inventory/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify threshold was updated
        self.assertEqual(response.data['low_stock_threshold'], 20)
        
        # Verify receipt location was not changed
        self.assertEqual(response.data['default_receipt_location']['id'], self.receipt_location.id)
        
        # Verify in database
        settings.refresh_from_db()
        self.assertEqual(settings.low_stock_threshold, 20)
        self.assertEqual(settings.default_receipt_location, self.receipt_location)
    
    def test_validation_of_invalid_location_references(self):
        """Test validation of invalid location references."""
        from .models import WarehouseSettings
        
        # Create initial settings
        WarehouseSettings.objects.create(low_stock_threshold=10)
        
        # Try to update with invalid location ID
        data = {
            'low_stock_threshold': 15,
            'default_receipt_location_id': 99999  # Invalid location ID
        }
        
        response = self.client.put('/api/inventory/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('default_receipt_location_id', response.data)
    
    def test_validation_of_negative_threshold(self):
        """Test validation of negative threshold."""
        from .models import WarehouseSettings
        
        # Create initial settings
        WarehouseSettings.objects.create(low_stock_threshold=10)
        
        # Try to update with negative threshold
        data = {
            'low_stock_threshold': -5
        }
        
        response = self.client.patch('/api/inventory/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('low_stock_threshold', response.data)
    
    def test_authentication_requirement(self):
        """Test authentication requirement."""
        # Logout
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/inventory/settings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.put('/api/inventory/settings/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_updated_by_field_set_to_current_user(self):
        """Test updated_by field set to current user."""
        from .models import WarehouseSettings
        
        # Create initial settings
        settings = WarehouseSettings.objects.create(
            low_stock_threshold=10
        )
        
        # Verify updated_by is None initially
        self.assertIsNone(settings.updated_by)
        
        # Update settings
        data = {
            'low_stock_threshold': 20
        }
        
        response = self.client.patch('/api/inventory/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify updated_by is set to current user
        settings.refresh_from_db()
        self.assertEqual(settings.updated_by, self.user)
        self.assertEqual(response.data['updated_by']['id'], self.user.id)
        self.assertEqual(response.data['updated_by']['login_id'], 'testuser')
    
    def test_multiple_updates_preserve_singleton(self):
        """Test multiple updates preserve singleton pattern."""
        from .models import WarehouseSettings
        
        # Create initial settings
        WarehouseSettings.objects.create(low_stock_threshold=10)
        
        # First update
        data1 = {'low_stock_threshold': 15}
        response1 = self.client.patch('/api/inventory/settings/', data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second update
        data2 = {'low_stock_threshold': 20}
        response2 = self.client.patch('/api/inventory/settings/', data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify only one settings record exists
        self.assertEqual(WarehouseSettings.objects.count(), 1)
        
        # Verify final value
        settings = WarehouseSettings.objects.first()
        self.assertEqual(settings.low_stock_threshold, 20)



class EnhancedPickingAPITest(APITestCase):
    """Test enhanced Picking API with nested writes."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            sku='PROD-001',
            name='Product 1',
            category=self.category,
            cost=Decimal('10.00'),
            price=Decimal('20.00')
        )
        self.product2 = Product.objects.create(
            sku='PROD-002',
            name='Product 2',
            category=self.category,
            cost=Decimal('15.00'),
            price=Decimal('30.00')
        )
        
        self.source_location = Location.objects.create(name='Source', usage_type='internal')
        self.dest_location = Location.objects.create(name='Destination', usage_type='internal')
        
        self.operation_type = OperationType.objects.create(
            name='Receipt',
            code='incoming',
            sequence_prefix='REC'
        )
    
    def test_post_pickings_with_nested_stock_moves(self):
        """Test POST /pickings/ with nested stock_moves."""
        from django.utils import timezone
        
        data = {
            'reference': 'REC-001',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft',
                    'notes': 'Batch A'
                },
                {
                    'product': self.product2.id,
                    'quantity': '5.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft',
                    'notes': 'Batch B'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify picking was created
        self.assertEqual(Picking.objects.count(), 1)
        picking = Picking.objects.first()
        self.assertEqual(picking.reference, 'REC-001')
        
        # Verify stock moves were created
        self.assertEqual(picking.stock_moves.count(), 2)
        self.assertEqual(StockMove.objects.count(), 2)
        
        # Verify stock move details
        move1 = picking.stock_moves.get(product=self.product1)
        self.assertEqual(move1.quantity, Decimal('10.00'))
        self.assertEqual(move1.notes, 'Batch A')
        
        move2 = picking.stock_moves.get(product=self.product2)
        self.assertEqual(move2.quantity, Decimal('5.00'))
        self.assertEqual(move2.notes, 'Batch B')
    
    def test_post_pickings_without_nested_stock_moves_backward_compatibility(self):
        """Test POST /pickings/ without nested stock_moves (backward compatibility)."""
        from django.utils import timezone
        
        # Create picking without stock_moves field
        data = {
            'reference': 'REC-002',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat()
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify picking was created
        self.assertEqual(Picking.objects.count(), 1)
        picking = Picking.objects.first()
        self.assertEqual(picking.reference, 'REC-002')
        
        # Verify no stock moves were created
        self.assertEqual(picking.stock_moves.count(), 0)
    
    def test_put_pickings_with_nested_stock_moves(self):
        """Test PUT /pickings/ with nested stock_moves."""
        from django.utils import timezone
        
        # Create initial picking with one stock move
        picking = Picking.objects.create(
            reference='REC-003',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        existing_move = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with modified and new stock moves
        data = {
            'reference': 'REC-003',
            'partner': 'Test Supplier Updated',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'confirmed',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': existing_move.id,
                    'product': self.product1.id,
                    'quantity': '15.00',  # Updated quantity
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'confirmed',
                    'notes': 'Updated'
                },
                {
                    # New move without id
                    'product': self.product2.id,
                    'quantity': '20.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'confirmed',
                    'notes': 'New move'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify picking was updated
        picking.refresh_from_db()
        self.assertEqual(picking.partner, 'Test Supplier Updated')
        self.assertEqual(picking.status, 'confirmed')
        
        # Verify stock moves
        self.assertEqual(picking.stock_moves.count(), 2)
        
        # Verify existing move was updated
        updated_move = StockMove.objects.get(id=existing_move.id)
        self.assertEqual(updated_move.quantity, Decimal('15.00'))
        self.assertEqual(updated_move.notes, 'Updated')
        
        # Verify new move was created
        new_move = picking.stock_moves.get(product=self.product2)
        self.assertEqual(new_move.quantity, Decimal('20.00'))
        self.assertEqual(new_move.notes, 'New move')
    
    def test_error_responses_for_validation_failures(self):
        """Test error responses for validation failures."""
        from django.utils import timezone
        
        # Test with empty stock_moves array
        data = {
            'reference': 'REC-004',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': []  # Empty array
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
        
        # Test with invalid product ID
        data['stock_moves'] = [
            {
                'product': 99999,  # Invalid product ID
                'quantity': '10.00',
                'source_location': self.source_location.id,
                'destination_location': self.dest_location.id,
                'status': 'draft'
            }
        ]
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
        
        # Test with negative quantity
        data['stock_moves'] = [
            {
                'product': self.product1.id,
                'quantity': '-10.00',  # Negative quantity
                'source_location': self.source_location.id,
                'destination_location': self.dest_location.id,
                'status': 'draft'
            }
        ]
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
        
        # Test with missing required field
        data['stock_moves'] = [
            {
                'product': self.product1.id,
                # Missing quantity field
                'source_location': self.source_location.id,
                'destination_location': self.dest_location.id,
                'status': 'draft'
            }
        ]
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock_moves', response.data)
    
    def test_transaction_rollback_behavior(self):
        """Test transaction rollback behavior."""
        from django.utils import timezone
        
        initial_picking_count = Picking.objects.count()
        initial_move_count = StockMove.objects.count()
        
        # Create picking with one valid and one invalid stock move
        data = {
            'reference': 'REC-005',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                },
                {
                    'product': 99999,  # Invalid product - should cause rollback
                    'quantity': '5.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify no partial data was created (transaction was rolled back)
        self.assertEqual(Picking.objects.count(), initial_picking_count)
        self.assertEqual(StockMove.objects.count(), initial_move_count)
    
    def test_nested_write_with_multiple_products(self):
        """Test nested write with multiple products."""
        from django.utils import timezone
        
        # Create additional products
        product3 = Product.objects.create(
            sku='PROD-003',
            name='Product 3',
            category=self.category,
            cost=Decimal('20.00'),
            price=Decimal('40.00')
        )
        
        data = {
            'reference': 'REC-006',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                },
                {
                    'product': self.product2.id,
                    'quantity': '15.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                },
                {
                    'product': product3.id,
                    'quantity': '20.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.post('/api/inventory/pickings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all stock moves were created
        picking = Picking.objects.get(reference='REC-006')
        self.assertEqual(picking.stock_moves.count(), 3)
        
        # Verify each product has a stock move
        self.assertTrue(picking.stock_moves.filter(product=self.product1).exists())
        self.assertTrue(picking.stock_moves.filter(product=self.product2).exists())
        self.assertTrue(picking.stock_moves.filter(product=product3).exists())
    
    def test_update_removes_stock_moves_not_in_list(self):
        """Test that updating removes stock moves not included in the update."""
        from django.utils import timezone
        
        # Create picking with two stock moves
        picking = Picking.objects.create(
            reference='REC-007',
            partner='Test Supplier',
            operation_type=self.operation_type,
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft',
            scheduled_date=timezone.now(),
            created_by=self.user
        )
        
        move1 = StockMove.objects.create(
            picking=picking,
            product=self.product1,
            quantity=Decimal('10.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        move2 = StockMove.objects.create(
            picking=picking,
            product=self.product2,
            quantity=Decimal('5.00'),
            source_location=self.source_location,
            destination_location=self.dest_location,
            status='draft'
        )
        
        # Update with only move1 (move2 should be removed)
        data = {
            'reference': 'REC-007',
            'partner': 'Test Supplier',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat(),
            'stock_moves': [
                {
                    'id': move1.id,
                    'product': self.product1.id,
                    'quantity': '10.00',
                    'source_location': self.source_location.id,
                    'destination_location': self.dest_location.id,
                    'status': 'draft'
                }
            ]
        }
        
        response = self.client.put(f'/api/inventory/pickings/{picking.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only one stock move remains
        picking.refresh_from_db()
        self.assertEqual(picking.stock_moves.count(), 1)
        self.assertTrue(picking.stock_moves.filter(id=move1.id).exists())
        self.assertFalse(StockMove.objects.filter(id=move2.id).exists())
