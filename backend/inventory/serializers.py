"""
Serializers for inventory API endpoints.
"""

from rest_framework import serializers
from .models import Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant


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


class PickingSerializer(serializers.ModelSerializer):
    """Serializer for Picking model."""
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)
    source_location_name = serializers.CharField(source='source_location.name', read_only=True)
    destination_location_name = serializers.CharField(source='destination_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stock_moves = StockMoveSerializer(many=True)
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
    
    def validate(self, data):
        """Validate nested stock_moves data."""
        stock_moves_data = data.get('stock_moves', [])
        
        # Validate that stock_moves list is not empty
        if not stock_moves_data:
            raise serializers.ValidationError({
                'stock_moves': 'At least one stock move is required.'
            })
        
        # Validate each stock move has required fields
        for idx, move_data in enumerate(stock_moves_data):
            required_fields = ['product', 'quantity', 'source_location', 'destination_location']
            missing_fields = [field for field in required_fields if field not in move_data]
            
            if missing_fields:
                raise serializers.ValidationError({
                    'stock_moves': {
                        idx: {field: 'This field is required.' for field in missing_fields}
                    }
                })
        
        return data
    
    def create(self, validated_data):
        """Create picking with nested stock moves in a transaction."""
        from django.db import transaction
        
        # Extract stock_moves from validated_data
        stock_moves_data = validated_data.pop('stock_moves', [])
        
        # Create picking and stock moves in a transaction
        with transaction.atomic():
            # Create the parent Picking first
            picking = Picking.objects.create(**validated_data)
            
            # Create each StockMove linked to the parent Picking
            for move_data in stock_moves_data:
                StockMove.objects.create(picking=picking, **move_data)
        
        return picking
    
    def update(self, instance, validated_data):
        """Update picking and handle nested stock moves modifications."""
        from django.db import transaction
        
        # Extract stock_moves from validated_data
        stock_moves_data = validated_data.pop('stock_moves', None)
        
        with transaction.atomic():
            # Update picking fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Handle stock moves if provided
            if stock_moves_data is not None:
                # Get existing move IDs from the data
                existing_move_ids = []
                
                for move_data in stock_moves_data:
                    move_id = move_data.get('id')
                    
                    if move_id:
                        # Update existing move
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
                        # Create new move
                        new_move = StockMove.objects.create(picking=instance, **move_data)
                        existing_move_ids.append(new_move.id)
                
                # Remove moves that are not in the updated list
                instance.stock_moves.exclude(id__in=existing_move_ids).delete()
        
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
