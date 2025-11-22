"""
Management command to initialize inventory adjustment location and operation type.
"""

from django.core.management.base import BaseCommand
from inventory.models import Location, OperationType


class Command(BaseCommand):
    help = 'Initialize virtual location and operation type for inventory adjustments'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing inventory adjustment setup...')
        
        # Create or get Virtual Locations parent
        virtual_locations, created = Location.objects.get_or_create(
            name='Virtual Locations',
            defaults={
                'usage_type': 'inventory',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Virtual Locations parent'))
        else:
            self.stdout.write('Virtual Locations parent already exists')
        
        # Create or get Inventory Adjustment location
        adjustment_loc, created = Location.objects.get_or_create(
            name='Inventory Adjustment',
            defaults={
                'parent': virtual_locations,
                'usage_type': 'inventory',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Inventory Adjustment location'))
        else:
            self.stdout.write('Inventory Adjustment location already exists')
        
        # Get the main warehouse stock zone for default destination
        try:
            stock_zone = Location.objects.get(name='Stock Zone')
        except Location.DoesNotExist:
            # Fallback to any internal location
            stock_zone = Location.objects.filter(usage_type='internal').first()
            if not stock_zone:
                self.stdout.write(self.style.WARNING(
                    'No internal location found. Creating default warehouse location.'
                ))
                warehouse = Location.objects.create(
                    name='Main Warehouse',
                    usage_type='internal'
                )
                stock_zone = Location.objects.create(
                    name='Stock Zone',
                    parent=warehouse,
                    usage_type='internal'
                )
        
        # Create or get Inventory Adjustment operation type
        adjustment_op, created = OperationType.objects.get_or_create(
            name='Inventory Adjustment',
            defaults={
                'code': 'internal',
                'sequence_prefix': 'ADJ',
                'description': 'Inventory adjustments and corrections',
                'default_source_location': adjustment_loc,
                'default_destination_location': stock_zone
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Inventory Adjustment operation type'))
        else:
            self.stdout.write('Inventory Adjustment operation type already exists')
        
        self.stdout.write(self.style.SUCCESS('\nInventory adjustment setup complete!'))
        self.stdout.write(f'Virtual Location: {adjustment_loc.get_full_path()}')
        self.stdout.write(f'Operation Type: {adjustment_op.name} ({adjustment_op.sequence_prefix})')
