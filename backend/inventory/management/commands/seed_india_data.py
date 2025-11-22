"""
Management command to seed database with India-based inventory data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventory.models import Category, Product, Location, OperationType, Picking, StockMove, StockQuant
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with India-based inventory data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed India-based data...')

        # Get or create a user for created_by fields
        user, _ = User.objects.get_or_create(
            login_id='admin',
            defaults={
                'email': 'admin@stockmaster.in'
            }
        )
        if not user.is_active:
            user.is_active = True
            user.save()

        # Create Categories
        self.stdout.write('Creating categories...')
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic items and gadgets'},
            {'name': 'Groceries', 'description': 'Food and grocery items'},
            {'name': 'Textiles', 'description': 'Fabrics and clothing materials'},
            {'name': 'Spices', 'description': 'Indian spices and condiments'},
            {'name': 'Stationery', 'description': 'Office and school supplies'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')

        # Create Products
        self.stdout.write('Creating products...')
        products_data = [
            # Electronics
            {'sku': 'ELEC001', 'name': 'LED Bulb 9W', 'category': 'Electronics', 'cost': 85.00, 'price': 120.00, 'uom': 'Pieces'},
            {'sku': 'ELEC002', 'name': 'Power Bank 10000mAh', 'category': 'Electronics', 'cost': 650.00, 'price': 999.00, 'uom': 'Pieces'},
            {'sku': 'ELEC003', 'name': 'USB Cable Type-C', 'category': 'Electronics', 'cost': 120.00, 'price': 199.00, 'uom': 'Pieces'},
            
            # Groceries
            {'sku': 'GROC001', 'name': 'Basmati Rice Premium', 'category': 'Groceries', 'cost': 85.00, 'price': 120.00, 'uom': 'Kg'},
            {'sku': 'GROC002', 'name': 'Toor Dal', 'category': 'Groceries', 'cost': 95.00, 'price': 135.00, 'uom': 'Kg'},
            {'sku': 'GROC003', 'name': 'Wheat Flour (Atta)', 'category': 'Groceries', 'cost': 35.00, 'price': 50.00, 'uom': 'Kg'},
            
            # Textiles
            {'sku': 'TEXT001', 'name': 'Cotton Fabric White', 'category': 'Textiles', 'cost': 180.00, 'price': 250.00, 'uom': 'Meters'},
            {'sku': 'TEXT002', 'name': 'Silk Saree Material', 'category': 'Textiles', 'cost': 850.00, 'price': 1200.00, 'uom': 'Meters'},
            
            # Spices
            {'sku': 'SPIC001', 'name': 'Turmeric Powder', 'category': 'Spices', 'cost': 180.00, 'price': 250.00, 'uom': 'Kg'},
            {'sku': 'SPIC002', 'name': 'Red Chilli Powder', 'category': 'Spices', 'cost': 220.00, 'price': 300.00, 'uom': 'Kg'},
            {'sku': 'SPIC003', 'name': 'Garam Masala', 'category': 'Spices', 'cost': 320.00, 'price': 450.00, 'uom': 'Kg'},
            
            # Stationery
            {'sku': 'STAT001', 'name': 'A4 Paper Ream', 'category': 'Stationery', 'cost': 220.00, 'price': 299.00, 'uom': 'Ream'},
            {'sku': 'STAT002', 'name': 'Ball Pen Blue', 'category': 'Stationery', 'cost': 5.00, 'price': 10.00, 'uom': 'Pieces'},
        ]

        products = {}
        for prod_data in products_data:
            prod, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': categories[prod_data['category']],
                    'cost': Decimal(str(prod_data['cost'])),
                    'price': Decimal(str(prod_data['price'])),
                    'uom': prod_data['uom'],
                    'is_active': True
                }
            )
            products[prod_data['sku']] = prod
            if created:
                self.stdout.write(f'  Created product: {prod.sku} - {prod.name}')

        # Create Locations
        self.stdout.write('Creating locations...')
        locations_data = [
            {'name': 'Mumbai Warehouse', 'usage_type': 'internal', 'parent': None},
            {'name': 'Delhi Distribution Center', 'usage_type': 'internal', 'parent': None},
            {'name': 'Bangalore Storage', 'usage_type': 'internal', 'parent': None},
            {'name': 'Vendor - Reliance Industries', 'usage_type': 'supplier', 'parent': None},
            {'name': 'Vendor - Tata Enterprises', 'usage_type': 'supplier', 'parent': None},
            {'name': 'Customer - BigBazaar Mumbai', 'usage_type': 'customer', 'parent': None},
            {'name': 'Customer - DMart Pune', 'usage_type': 'customer', 'parent': None},
            {'name': 'Transit Location', 'usage_type': 'transit', 'parent': None},
        ]

        locations = {}
        for loc_data in locations_data:
            loc, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={
                    'usage_type': loc_data['usage_type'],
                    'parent': loc_data['parent'],
                    'is_active': True
                }
            )
            locations[loc_data['name']] = loc
            if created:
                self.stdout.write(f'  Created location: {loc.name}')

        # Create Operation Types
        self.stdout.write('Creating operation types...')
        op_types_data = [
            {
                'name': 'Receipts',
                'code': 'incoming',
                'sequence_prefix': 'REC',
                'description': 'Incoming goods from suppliers',
                'default_source_location': locations['Vendor - Reliance Industries'],
                'default_destination_location': locations['Mumbai Warehouse']
            },
            {
                'name': 'Delivery Orders',
                'code': 'outgoing',
                'sequence_prefix': 'DEL',
                'description': 'Outgoing goods to customers',
                'default_source_location': locations['Mumbai Warehouse'],
                'default_destination_location': locations['Customer - BigBazaar Mumbai']
            },
            {
                'name': 'Internal Transfers',
                'code': 'internal',
                'sequence_prefix': 'INT',
                'description': 'Internal warehouse transfers',
                'default_source_location': locations['Mumbai Warehouse'],
                'default_destination_location': locations['Delhi Distribution Center']
            },
        ]

        op_types = {}
        for op_data in op_types_data:
            # Try to get existing operation type by name first
            op = OperationType.objects.filter(name=op_data['name']).first()
            if not op:
                # If not found, create new one
                op = OperationType.objects.create(
                    name=op_data['name'],
                    code=op_data['code'],
                    sequence_prefix=op_data['sequence_prefix'],
                    description=op_data['description'],
                    default_source_location=op_data['default_source_location'],
                    default_destination_location=op_data['default_destination_location']
                )
                self.stdout.write(f'  Created operation type: {op.name}')
            else:
                self.stdout.write(f'  Using existing operation type: {op.name}')
            op_types[op_data['name']] = op

        # Create Pickings with Stock Moves
        self.stdout.write('Creating pickings and stock moves...')
        
        # Receipt 1
        picking1, created = Picking.objects.get_or_create(
            reference='REC00001',
            defaults={
                'partner': 'Reliance Industries Ltd',
                'operation_type': op_types['Receipts'],
                'source_location': locations['Vendor - Reliance Industries'],
                'destination_location': locations['Mumbai Warehouse'],
                'status': 'done',
                'scheduled_date': timezone.now() - timedelta(days=10),
                'completion_date': timezone.now() - timedelta(days=10),
                'notes': 'Monthly stock replenishment',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  Created picking: {picking1.reference}')
            StockMove.objects.create(
                picking=picking1,
                product=products['ELEC001'],
                quantity=Decimal('500'),
                source_location=locations['Vendor - Reliance Industries'],
                destination_location=locations['Mumbai Warehouse'],
                status='done'
            )
            StockMove.objects.create(
                picking=picking1,
                product=products['GROC001'],
                quantity=Decimal('200'),
                source_location=locations['Vendor - Reliance Industries'],
                destination_location=locations['Mumbai Warehouse'],
                status='done'
            )

        # Receipt 2
        picking2, created = Picking.objects.get_or_create(
            reference='REC00002',
            defaults={
                'partner': 'Tata Enterprises',
                'operation_type': op_types['Receipts'],
                'source_location': locations['Vendor - Tata Enterprises'],
                'destination_location': locations['Delhi Distribution Center'],
                'status': 'done',
                'scheduled_date': timezone.now() - timedelta(days=8),
                'completion_date': timezone.now() - timedelta(days=8),
                'notes': 'Spices and textiles order',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  Created picking: {picking2.reference}')
            StockMove.objects.create(
                picking=picking2,
                product=products['SPIC001'],
                quantity=Decimal('100'),
                source_location=locations['Vendor - Tata Enterprises'],
                destination_location=locations['Delhi Distribution Center'],
                status='done'
            )
            StockMove.objects.create(
                picking=picking2,
                product=products['TEXT001'],
                quantity=Decimal('300'),
                source_location=locations['Vendor - Tata Enterprises'],
                destination_location=locations['Delhi Distribution Center'],
                status='done'
            )

        # Delivery 1
        picking3, created = Picking.objects.get_or_create(
            reference='DEL00001',
            defaults={
                'partner': 'BigBazaar Mumbai',
                'operation_type': op_types['Delivery Orders'],
                'source_location': locations['Mumbai Warehouse'],
                'destination_location': locations['Customer - BigBazaar Mumbai'],
                'status': 'done',
                'scheduled_date': timezone.now() - timedelta(days=5),
                'completion_date': timezone.now() - timedelta(days=5),
                'notes': 'Weekly delivery to BigBazaar',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  Created picking: {picking3.reference}')
            StockMove.objects.create(
                picking=picking3,
                product=products['ELEC001'],
                quantity=Decimal('100'),
                source_location=locations['Mumbai Warehouse'],
                destination_location=locations['Customer - BigBazaar Mumbai'],
                status='done'
            )
            StockMove.objects.create(
                picking=picking3,
                product=products['GROC001'],
                quantity=Decimal('50'),
                source_location=locations['Mumbai Warehouse'],
                destination_location=locations['Customer - BigBazaar Mumbai'],
                status='done'
            )

        # Delivery 2
        picking4, created = Picking.objects.get_or_create(
            reference='DEL00002',
            defaults={
                'partner': 'DMart Pune',
                'operation_type': op_types['Delivery Orders'],
                'source_location': locations['Mumbai Warehouse'],
                'destination_location': locations['Customer - DMart Pune'],
                'status': 'confirmed',
                'scheduled_date': timezone.now() + timedelta(days=2),
                'notes': 'Scheduled delivery for next week',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  Created picking: {picking4.reference}')
            StockMove.objects.create(
                picking=picking4,
                product=products['GROC002'],
                quantity=Decimal('75'),
                source_location=locations['Mumbai Warehouse'],
                destination_location=locations['Customer - DMart Pune'],
                status='confirmed'
            )
            StockMove.objects.create(
                picking=picking4,
                product=products['STAT001'],
                quantity=Decimal('20'),
                source_location=locations['Mumbai Warehouse'],
                destination_location=locations['Customer - DMart Pune'],
                status='confirmed'
            )

        # Internal Transfer
        picking5, created = Picking.objects.get_or_create(
            reference='INT00001',
            defaults={
                'partner': 'Internal Transfer',
                'operation_type': op_types['Internal Transfers'],
                'source_location': locations['Mumbai Warehouse'],
                'destination_location': locations['Delhi Distribution Center'],
                'status': 'draft',
                'scheduled_date': timezone.now() + timedelta(days=5),
                'notes': 'Stock rebalancing between warehouses',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(f'  Created picking: {picking5.reference}')
            StockMove.objects.create(
                picking=picking5,
                product=products['ELEC002'],
                quantity=Decimal('50'),
                source_location=locations['Mumbai Warehouse'],
                destination_location=locations['Delhi Distribution Center'],
                status='draft'
            )

        # Create Stock Quantities
        self.stdout.write('Creating stock quantities...')
        stock_data = [
            {'product': 'ELEC001', 'location': 'Mumbai Warehouse', 'quantity': 400},
            {'product': 'ELEC002', 'location': 'Mumbai Warehouse', 'quantity': 150},
            {'product': 'ELEC003', 'location': 'Mumbai Warehouse', 'quantity': 200},
            {'product': 'GROC001', 'location': 'Mumbai Warehouse', 'quantity': 150},
            {'product': 'GROC002', 'location': 'Mumbai Warehouse', 'quantity': 180},
            {'product': 'GROC003', 'location': 'Mumbai Warehouse', 'quantity': 250},
            {'product': 'SPIC001', 'location': 'Delhi Distribution Center', 'quantity': 100},
            {'product': 'SPIC002', 'location': 'Delhi Distribution Center', 'quantity': 80},
            {'product': 'TEXT001', 'location': 'Delhi Distribution Center', 'quantity': 300},
            {'product': 'TEXT002', 'location': 'Bangalore Storage', 'quantity': 50},
            {'product': 'STAT001', 'location': 'Mumbai Warehouse', 'quantity': 120},
            {'product': 'STAT002', 'location': 'Mumbai Warehouse', 'quantity': 500},
        ]

        for stock in stock_data:
            quant, created = StockQuant.objects.get_or_create(
                product=products[stock['product']],
                location=locations[stock['location']],
                defaults={'quantity': Decimal(str(stock['quantity']))}
            )
            if created:
                self.stdout.write(f'  Created stock: {stock["product"]} at {stock["location"]} - {stock["quantity"]} units')

        self.stdout.write(self.style.SUCCESS('\nSuccessfully seeded India-based data!'))
        self.stdout.write(f'  Categories: {len(categories_data)}')
        self.stdout.write(f'  Products: {len(products_data)}')
        self.stdout.write(f'  Locations: {len(locations_data)}')
        self.stdout.write(f'  Operation Types: {len(op_types_data)}')
        self.stdout.write(f'  Pickings: 5')
        self.stdout.write(f'  Stock Quantities: {len(stock_data)}')
