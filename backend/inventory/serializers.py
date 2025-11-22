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
            'cost', 'price', 'barcode', 'is_active', 'created_at', 'updated_at'
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


class PickingSerializer(serializers.ModelSerializer):
    """Serializer for Picking model."""
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)
    source_location_name = serializers.CharField(source='source_location.name', read_only=True)
    destination_location_name = serializers.CharField(source='destination_location.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stock_moves = StockMoveSerializer(many=True, read_only=True)
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
