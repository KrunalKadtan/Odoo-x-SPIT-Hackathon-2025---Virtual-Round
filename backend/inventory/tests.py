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
