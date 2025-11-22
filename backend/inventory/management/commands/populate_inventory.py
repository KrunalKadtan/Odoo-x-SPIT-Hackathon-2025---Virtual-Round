"""
Management command to populate inventory with sample data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from inventory.models import (
    Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate inventory with sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample inventory data...')
        
        # Create Categories
        self.stdout.write('Creating categories...')
        electronics = Category.objects.create(name='Electronics', description='Electronic items')
        computers = Category.objects.create(name='Computers', parent=electronics, description='Computer equipment')
        accessories = Category.objects.create(name='Accessories', parent=electronics, description='Electronic accessories')
        
        furniture = Category.objects.create(name='Furniture', description='Office furniture')
        office_chairs = Category.objects.create(name='Office Chairs', parent=furniture)
        
        self.stdout.write(self.style.SUCCESS(f'Created {Category.objects.count()} categories'))
        
        # Create Locations
        self.stdout.write('Creating locations...')
        warehouse = Location.objects.create(name='Main Warehouse', usage_type='internal')
        stock_zone = Location.objects.create(name='Stock Zone', parent=warehouse, usage_type='internal')
        shelf_a = Location.objects.create(name='Shelf A', parent=stock_zone, usage_type='internal', barcode='WH-A-001')
        shelf_b = Location.objects.create(name='Shelf B', parent=stock_zone, usage_type='internal', barcode='WH-B-001')
        
        customer_loc = Location.objects.create(name='Customer Locations', usage_type='customer')
        supplier_loc = Location.objects.create(name='Supplier Locations', usage_type='supplier')
        
        self.stdout.write(self.style.SUCCESS(f'Created {Location.objects.count()} locations'))
        
        # Create Operation Types
        self.stdout.write('Creating operation types...')
        receipt_op = OperationType.objects.create(
            name='Receipts',
            code='incoming',
            sequence_prefix='IN',
            description='Incoming shipments from suppliers',
            default_source_location=supplier_loc,
            default_destination_location=stock_zone
        )
        
        delivery_op = OperationType.objects.create(
            name='Delivery Orders',
            code='outgoing',
            sequence_prefix='OUT',
            description='Outgoing shipments to customers',
            default_source_location=stock_zone,
            default_destination_location=customer_loc
        )
        
        internal_op = OperationType.objects.create(
            name='Internal Transfers',
            code='internal',
            sequence_prefix='INT',
            description='Internal warehouse transfers',
            default_source_location=shelf_a,
            default_destination_location=shelf_b
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {OperationType.objects.count()} operation types'))
        
        # Create Products
        self.stdout.write('Creating products...')
        laptop = Product.objects.create(
            sku='LAP-001',
            name='Dell Laptop XPS 15',
            description='High-performance laptop',
            category=computers,
            cost=Decimal('800.00'),
            price=Decimal('1200.00'),
            barcode='LAP001'
        )
        
        mouse = Product.objects.create(
            sku='MOU-001',
            name='Wireless Mouse',
            description='Ergonomic wireless mouse',
            category=accessories,
            cost=Decimal('15.00'),
            price=Decimal('25.00'),
            barcode='MOU001'
        )
        
        keyboard = Product.objects.create(
            sku='KEY-001',
            name='Mechanical Keyboard',
            description='RGB mechanical keyboard',
            category=accessories,
            cost=Decimal('50.00'),
            price=Decimal('80.00'),
            barcode='KEY001'
        )
        
        chair = Product.objects.create(
            sku='CHR-001',
            name='Ergonomic Office Chair',
            description='Adjustable office chair',
            category=office_chairs,
            cost=Decimal('150.00'),
            price=Decimal('250.00'),
            barcode='CHR001'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Product.objects.count()} products'))
        
        # Create Stock Quantities
        self.stdout.write('Creating stock quantities...')
        StockQuant.objects.create(product=laptop, location=shelf_a, quantity=Decimal('10.00'))
        StockQuant.objects.create(product=mouse, location=shelf_a, quantity=Decimal('50.00'))
        StockQuant.objects.create(product=keyboard, location=shelf_b, quantity=Decimal('30.00'))
        StockQuant.objects.create(product=chair, location=shelf_b, quantity=Decimal('15.00'))
        
        self.stdout.write(self.style.SUCCESS(f'Created {StockQuant.objects.count()} stock quantities'))
        
        # Get or create a user for pickings
        user, created = User.objects.get_or_create(
            login_id='admin01',
            defaults={
                'email': 'admin@stockmaster.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('Admin@123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create Pickings with Stock Moves
        self.stdout.write('Creating pickings and stock moves...')
        
        # Receipt
        receipt = Picking.objects.create(
            reference='IN/00001',
            partner='Tech Supplier Inc.',
            operation_type=receipt_op,
            source_location=supplier_loc,
            destination_location=shelf_a,
            status='confirmed',
            scheduled_date=timezone.now() + timedelta(days=1),
            created_by=user
        )
        
        StockMove.objects.create(
            picking=receipt,
            product=laptop,
            quantity=Decimal('5.00'),
            source_location=supplier_loc,
            destination_location=shelf_a,
            status='confirmed'
        )
        
        StockMove.objects.create(
            picking=receipt,
            product=mouse,
            quantity=Decimal('20.00'),
            source_location=supplier_loc,
            destination_location=shelf_a,
            status='confirmed'
        )
        
        # Delivery
        delivery = Picking.objects.create(
            reference='OUT/00001',
            partner='ABC Corporation',
            operation_type=delivery_op,
            source_location=shelf_a,
            destination_location=customer_loc,
            status='assigned',
            scheduled_date=timezone.now() + timedelta(days=2),
            created_by=user
        )
        
        StockMove.objects.create(
            picking=delivery,
            product=laptop,
            quantity=Decimal('2.00'),
            source_location=shelf_a,
            destination_location=customer_loc,
            status='assigned'
        )
        
        StockMove.objects.create(
            picking=delivery,
            product=keyboard,
            quantity=Decimal('5.00'),
            source_location=shelf_b,
            destination_location=customer_loc,
            status='assigned'
        )
        
        # Internal Transfer
        transfer = Picking.objects.create(
            reference='INT/00001',
            partner='',
            operation_type=internal_op,
            source_location=shelf_a,
            destination_location=shelf_b,
            status='draft',
            scheduled_date=timezone.now() + timedelta(days=3),
            created_by=user
        )
        
        StockMove.objects.create(
            picking=transfer,
            product=mouse,
            quantity=Decimal('10.00'),
            source_location=shelf_a,
            destination_location=shelf_b,
            status='draft'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Picking.objects.count()} pickings'))
        self.stdout.write(self.style.SUCCESS(f'Created {StockMove.objects.count()} stock moves'))
        
        # Create Tasks
        self.stdout.write('Creating tasks...')
        Task.objects.create(
            title='Process incoming receipt',
            description='Verify and process incoming shipment IN/00001',
            assigned_to=user,
            related_picking=receipt,
            status='pending',
            priority='high',
            due_date=timezone.now() + timedelta(days=1)
        )
        
        Task.objects.create(
            title='Prepare delivery order',
            description='Pick and pack items for delivery OUT/00001',
            assigned_to=user,
            related_picking=delivery,
            status='in_progress',
            priority='urgent',
            due_date=timezone.now() + timedelta(days=2)
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Task.objects.count()} tasks'))
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Admin user: login_id=admin01, password=Admin@123'))
