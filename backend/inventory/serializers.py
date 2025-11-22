"""
Serializers for inventory API endpoints.
"""

from rest_framework import serializers
from .models import Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant, MoveHistory, WarehouseSettings


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    full_path = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'full_path', 'description', 'children_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_path(self, obj):
        return obj.get_full_path()
    
    def get_children_count(self, obj):
        return obj.children.count()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'category', 'category_name',
            'cost', 'price', 'barcode', 'uom', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""
    full_path = serializers.SerializerMethodField()
    usage_type_display = serializers.CharField(source='get_usage_type_display', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'parent', 'full_path', 'barcode', 'usage_type',
            'usage_type_display', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_path(self, obj):
        return obj.get_full_path()


class OperationTypeSerializer(serializers.ModelSerializer):
    """Serializer for OperationType model."""
    code_display = serializers.CharField(source='get_code_display', read_only=True)
    
    class Meta:
        model = OperationType
        fields = [
            'id', 'name', 'code', 'code_display', 'sequence_prefix', 'description',
            'default_source_location', 'default_destination_location',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StockMoveSerializer(serializers.ModelSerializer):
    """Serializer for StockMove model."""
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    source_location_name = serializers.CharField(source='source_location.name', read_only=True)
    destination_location_name = serializers.CharField(source='destination_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockMove
        fields = [
            'id', 'picking', 'product', 'product_sku', 'product_name',
            'quantity', 'source_location', 'source_location_name',
            'destination_location', 'destination_location_name',
            'status', 'status_display', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'picking': {'required': False}
        }


class StockMoveNestedSerializer(serializers.Serializer):
    """Simplified serializer for nested stock move data in picking creation/updates."""
    id = serializers.IntegerField(required=False, allow_null=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_product(self, value):
        """Validate that product exists."""
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Product with id {value.id} does not exist.")
        return value
    
    def validate_quantity(self, value):
        """Validate that quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value


class PickingSerializer(serializers.ModelSerializer):
    """Serializer for Picking model."""
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)
    source_location_name = serializers.CharField(source='source_location.name', read_only=True)
    destination_location_name = serializers.CharField(source='destination_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stock_moves = StockMoveNestedSerializer(many=True, required=False)
    stock_moves_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Picking
        fields = [
            'id', 'reference', 'partner', 'operation_type', 'operation_type_name',
            'source_location', 'source_location_name',
            'destination_location', 'destination_location_name',
            'status', 'status_display', 'scheduled_date', 'completion_date',
            'notes', 'stock_moves', 'stock_moves_count',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_stock_moves_count(self, obj):
        return obj.stock_moves.count()
    
    def validate_stock_moves(self, value):
        """Validate that at least one stock move is provided when stock_moves is present."""
        if value is not None and len(value) == 0:
            raise serializers.ValidationError("At least one stock move is required.")
        return value
    
    def create(self, validated_data):
        """Create picking with nested stock moves in a transaction."""
        from django.db import transaction
        
        # Extract stock_moves from validated_data
        stock_moves_data = validated_data.pop('stock_moves', [])
        
        # Create picking and stock moves in a transaction
        with transaction.atomic():
            # Create the parent Picking first
            picking = Picking.objects.create(**validated_data)
            
            # Loop through stock_moves and create StockMove instances
            for move_data in stock_moves_data:
                # Set source_location and destination_location from picking
                move_data['source_location'] = picking.source_location
                move_data['destination_location'] = picking.destination_location
                # Set status to match picking status
                move_data['status'] = picking.status
                # Create StockMove instance
                StockMove.objects.create(picking=picking, **move_data)
        
        return picking
    
    def update(self, instance, validated_data):
        """Update picking and handle nested stock moves modifications."""
        from django.db import transaction
        
        # Extract stock_moves from validated_data if present
        stock_moves_data = validated_data.pop('stock_moves', None)
        
        # Use transaction.atomic() to wrap updates
        with transaction.atomic():
            # Update picking fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Handle stock_moves updates: identify moves to add, update, or remove
            if stock_moves_data is not None:
                # Get existing move IDs from the data
                existing_move_ids = []
                
                for move_data in stock_moves_data:
                    move_id = move_data.get('id')
                    
                    if move_id:
                        # For existing moves (with id), update StockMove instances
                        try:
                            move = StockMove.objects.get(id=move_id, picking=instance)
                            for attr, value in move_data.items():
                                if attr != 'id':
                                    setattr(move, attr, value)
                            move.save()
                            existing_move_ids.append(move_id)
                        except StockMove.DoesNotExist:
                            raise serializers.ValidationError({
                                'stock_moves': f'Stock move with id {move_id} does not exist for this picking.'
                            })
                    else:
                        # For new moves (no id), create StockMove instances
                        move_data['source_location'] = instance.source_location
                        move_data['destination_location'] = instance.destination_location
                        move_data['status'] = instance.status
                        new_move = StockMove.objects.create(picking=instance, **move_data)
                        existing_move_ids.append(new_move.id)
                
                # For removed moves, delete StockMove instances
                instance.stock_moves.exclude(id__in=existing_move_ids).delete()
        
        # Return updated picking with nested moves
        return instance


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    related_picking_reference = serializers.CharField(source='related_picking.reference', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_username',
            'related_picking', 'related_picking_reference',
            'status', 'status_display', 'priority', 'priority_display',
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StockQuantSerializer(serializers.ModelSerializer):
    """Serializer for StockQuant model."""
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    available_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = StockQuant
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'location', 'location_name', 'quantity', 'reserved_quantity',
            'available_quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'available_quantity']



class UserNestedSerializer(serializers.Serializer):
    """Nested serializer for User model in read-only contexts."""
    id = serializers.IntegerField(read_only=True)
    login_id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)


class MoveHistorySerializer(serializers.ModelSerializer):
    """Serializer for MoveHistory model."""
    user = UserNestedSerializer(read_only=True)
    picking = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    source_location = serializers.SerializerMethodField()
    destination_location = serializers.SerializerMethodField()
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = MoveHistory
        fields = [
            'id', 'timestamp', 'user', 'action_type', 'action_type_display',
            'action_display', 'picking', 'product', 'quantity',
            'source_location', 'destination_location',
            'old_status', 'new_status', 'notes'
        ]
        read_only_fields = [
            'id', 'timestamp', 'user', 'action_type', 'action_type_display',
            'action_display', 'picking', 'product', 'quantity',
            'source_location', 'destination_location',
            'old_status', 'new_status', 'notes'
        ]
    
    def get_picking(self, obj):
        """Return nested picking data."""
        if obj.picking:
            return {
                'id': obj.picking.id,
                'reference': obj.picking.reference
            }
        return None
    
    def get_product(self, obj):
        """Return nested product data."""
        if obj.product:
            return {
                'id': obj.product.id,
                'sku': obj.product.sku,
                'name': obj.product.name
            }
        return None
    
    def get_source_location(self, obj):
        """Return nested source location data."""
        if obj.source_location:
            return {
                'id': obj.source_location.id,
                'name': obj.source_location.name
            }
        return None
    
    def get_destination_location(self, obj):
        """Return nested destination location data."""
        if obj.destination_location:
            return {
                'id': obj.destination_location.id,
                'name': obj.destination_location.name
            }
        return None


class WarehouseSettingsSerializer(serializers.ModelSerializer):
    """Serializer for WarehouseSettings model."""
    default_receipt_location = serializers.SerializerMethodField()
    default_delivery_location = serializers.SerializerMethodField()
    default_adjustment_location = serializers.SerializerMethodField()
    updated_by = UserNestedSerializer(read_only=True)
    
    # Write fields for location IDs
    default_receipt_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='default_receipt_location',
        required=False,
        allow_null=True,
        write_only=True
    )
    default_delivery_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='default_delivery_location',
        required=False,
        allow_null=True,
        write_only=True
    )
    default_adjustment_location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='default_adjustment_location',
        required=False,
        allow_null=True,
        write_only=True
    )
    
    class Meta:
        model = WarehouseSettings
        fields = [
            'id', 'low_stock_threshold',
            'default_receipt_location', 'default_receipt_location_id',
            'default_delivery_location', 'default_delivery_location_id',
            'default_adjustment_location', 'default_adjustment_location_id',
            'updated_at', 'updated_by'
        ]
        read_only_fields = ['id', 'updated_at', 'updated_by']
    
    def get_default_receipt_location(self, obj):
        """Return nested receipt location data."""
        if obj.default_receipt_location:
            return {
                'id': obj.default_receipt_location.id,
                'name': obj.default_receipt_location.name
            }
        return None
    
    def get_default_delivery_location(self, obj):
        """Return nested delivery location data."""
        if obj.default_delivery_location:
            return {
                'id': obj.default_delivery_location.id,
                'name': obj.default_delivery_location.name
            }
        return None
    
    def get_default_adjustment_location(self, obj):
        """Return nested adjustment location data."""
        if obj.default_adjustment_location:
            return {
                'id': obj.default_adjustment_location.id,
                'name': obj.default_adjustment_location.name
            }
        return None
    
    def validate_low_stock_threshold(self, value):
        """Validate that low stock threshold is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold must be non-negative.")
        return value
    
    def validate_default_receipt_location_id(self, value):
        """Validate that receipt location exists."""
        if value and not Location.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Location with id {value.id} does not exist.")
        return value
    
    def validate_default_delivery_location_id(self, value):
        """Validate that delivery location exists."""
        if value and not Location.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Location with id {value.id} does not exist.")
        return value
    
    def validate_default_adjustment_location_id(self, value):
        """Validate that adjustment location exists."""
        if value and not Location.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Location with id {value.id} does not exist.")
        return value
