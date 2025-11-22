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
        data = {
            'reference': 'TEST-001',
            'partner': 'Test Partner',
            'operation_type': self.operation_type.id,
            'source_location': self.source_location.id,
            'destination_location': self.dest_location.id,
            'status': 'draft',
            'scheduled_date': timezone.now().isoformat()
        }
        response = self.client.post('/api/inventory/pickings/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Picking.objects.count(), 1)
