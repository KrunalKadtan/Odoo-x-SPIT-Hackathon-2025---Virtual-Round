"""
API views for inventory management.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from decimal import Decimal
import django_filters
from django.utils.dateparse import parse_datetime
from .models import Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant, MoveHistory, WarehouseSettings
from .serializers import (
    CategorySerializer, ProductSerializer, LocationSerializer,
    OperationTypeSerializer, PickingSerializer, StockMoveSerializer,
    TaskSerializer, StockQuantSerializer, MoveHistorySerializer, WarehouseSettingsSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model.
    
    Provides CRUD operations and hierarchical category management.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get all child categories of a category."""
        category = self.get_object()
        children = category.children.all()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model.
    
    Provides CRUD operations and product search/filtering.
    """
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['sku', 'name', 'barcode']
    ordering_fields = ['sku', 'name', 'cost', 'price', 'created_at']
    ordering = ['sku']
    
    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get current stock levels for a product across all locations."""
        product = self.get_object()
        stock_quants = StockQuant.objects.filter(product=product).select_related('location')
        serializer = StockQuantSerializer(stock_quants, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Location model.
    
    Provides CRUD operations and hierarchical location management.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['usage_type', 'is_active']
    search_fields = ['name', 'barcode']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get current stock levels at a location."""
        location = self.get_object()
        stock_quants = StockQuant.objects.filter(location=location).select_related('product')
        serializer = StockQuantSerializer(stock_quants, many=True)
        return Response(serializer.data)


class OperationTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OperationType model.
    
    Provides CRUD operations for operation types.
    """
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'sequence_prefix']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class PickingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Picking model.
    
    Provides CRUD operations and picking workflow management.
    """
    queryset = Picking.objects.select_related(
        'operation_type', 'source_location', 'destination_location', 'created_by'
    ).prefetch_related('stock_moves').all()
    serializer_class = PickingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'operation_type']
    search_fields = ['reference', 'partner']
    ordering_fields = ['reference', 'scheduled_date', 'created_at']
    ordering = ['-scheduled_date']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a picking (change status from draft to confirmed)."""
        picking = self.get_object()
        if picking.status != 'draft':
            return Response(
                {'error': 'Only draft pickings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        picking.status = 'confirmed'
        picking.save()
        serializer = self.get_serializer(picking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate a picking (mark as done and update stock)."""
        picking = self.get_object()
        if picking.status == 'done':
            return Response(
                {'error': 'Picking is already done'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock availability for outgoing operations
        if picking.operation_type.code == 'outgoing':
            for move in picking.stock_moves.all():
                # Query current stock at source location
                quant = StockQuant.objects.filter(
                    product=move.product,
                    location=move.source_location
                ).first()
                
                # Treat as zero if no StockQuant record exists
                available = quant.quantity if quant else Decimal('0.00')
                
                # Check if sufficient stock is available
                if available < move.quantity:
                    return Response({
                        'error': f'Insufficient stock for {move.product.name}',
                        'product': move.product.sku,
                        'required': str(move.quantity),
                        'available': str(available),
                        'location': move.source_location.name
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update stock quantities for each stock move
        for move in picking.stock_moves.all():
            # Decrease quantity at source location
            source_quant, _ = StockQuant.objects.get_or_create(
                product=move.product,
                location=move.source_location
            )
            source_quant.quantity -= move.quantity
            source_quant.save()
            
            # Increase quantity at destination location
            dest_quant, _ = StockQuant.objects.get_or_create(
                product=move.product,
                location=move.destination_location
            )
            dest_quant.quantity += move.quantity
            dest_quant.save()
            
            # Update move status
            move.status = 'done'
            move.save()
        
        # Update picking status
        picking.status = 'done'
        from django.utils import timezone
        picking.completion_date = timezone.now()
        picking.save()
        
        serializer = self.get_serializer(picking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a picking."""
        picking = self.get_object()
        if picking.status == 'done':
            return Response(
                {'error': 'Cannot cancel a completed picking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        picking.status = 'cancelled'
        picking.save()
        
        # Cancel all stock moves
        picking.stock_moves.update(status='cancelled')
        
        serializer = self.get_serializer(picking)
        return Response(serializer.data)


class StockMoveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StockMove model.
    
    Provides CRUD operations for stock moves.
    """
    queryset = StockMove.objects.select_related(
        'picking', 'product', 'source_location', 'destination_location'
    ).all()
    serializer_class = StockMoveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'picking', 'product']
    search_fields = ['product__sku', 'product__name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model.
    
    Provides CRUD operations and task management.
    """
    queryset = Task.objects.select_related('assigned_to', 'related_picking').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'due_date', 'created_at']
    ordering = ['-priority', 'due_date']
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user."""
        tasks = self.queryset.filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed."""
        task = self.get_object()
        task.status = 'completed'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class StockQuantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for StockQuant model (read-only).
    
    Provides stock level queries and reporting.
    """
    queryset = StockQuant.objects.select_related('product', 'location').all()
    serializer_class = StockQuantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'location']
    search_fields = ['product__sku', 'product__name', 'location__name']
    ordering_fields = ['quantity', 'created_at']
    ordering = ['product__sku']
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock levels (quantity < 10)."""
        low_stock = self.queryset.filter(quantity__lt=10, quantity__gt=0)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get products that are out of stock."""
        out_of_stock = self.queryset.filter(quantity=0)
        serializer = self.get_serializer(out_of_stock, many=True)
        return Response(serializer.data)


class MoveHistoryFilter(django_filters.FilterSet):
    """Custom filter for MoveHistory with date range support."""
    date_from = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = MoveHistory
        fields = ['product', 'picking', 'action_type', 'user']


class MoveHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for MoveHistory model (read-only).
    
    Provides history tracking and audit logging for inventory movements.
    """
    queryset = MoveHistory.objects.select_related(
        'user', 'picking', 'product', 'source_location', 'destination_location'
    ).all()
    serializer_class = MoveHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MoveHistoryFilter
    search_fields = ['picking__reference', 'product__sku']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class WarehouseSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WarehouseSettings model.
    
    Provides settings management with singleton pattern.
    Only supports list, retrieve, update, and partial_update actions.
    """
    queryset = WarehouseSettings.objects.all()
    serializer_class = WarehouseSettingsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
    
    def get_object(self):
        """Override get_object to return singleton settings instance."""
        return WarehouseSettings.get_settings()
    
    def list(self, request, *args, **kwargs):
        """Override list to return single settings object (not array)."""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        """Set updated_by field to current user on update and validate location references."""
        # Validate location references
        validated_data = serializer.validated_data
        
        # Check default_receipt_location
        receipt_location = validated_data.get('default_receipt_location')
        if receipt_location and not Location.objects.filter(id=receipt_location.id).exists():
            raise serializers.ValidationError({
                'default_receipt_location': f'Location with id {receipt_location.id} does not exist.'
            })
        
        # Check default_delivery_location
        delivery_location = validated_data.get('default_delivery_location')
        if delivery_location and not Location.objects.filter(id=delivery_location.id).exists():
            raise serializers.ValidationError({
                'default_delivery_location': f'Location with id {delivery_location.id} does not exist.'
            })
        
        # Check default_adjustment_location
        adjustment_location = validated_data.get('default_adjustment_location')
        if adjustment_location and not Location.objects.filter(id=adjustment_location.id).exists():
            raise serializers.ValidationError({
                'default_adjustment_location': f'Location with id {adjustment_location.id} does not exist.'
            })
        
        # Set updated_by to current user
        serializer.save(updated_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics including total products, low stock items,
    pending receipts, and pending deliveries.
    """
    # Calculate total active products
    total_products = Product.objects.filter(is_active=True).count()
    
    # Calculate low stock items (quantity < 10 and > 0)
    low_stock_items = StockQuant.objects.filter(
        quantity__lt=10,
        quantity__gt=0
    ).count()
    
    # Calculate pending receipts (incoming pickings in draft/confirmed/assigned status)
    pending_receipts = Picking.objects.filter(
        operation_type__code='incoming',
        status__in=['draft', 'confirmed', 'assigned']
    ).count()
    
    # Calculate pending deliveries (outgoing pickings in draft/confirmed/assigned status)
    pending_deliveries = Picking.objects.filter(
        operation_type__code='outgoing',
        status__in=['draft', 'confirmed', 'assigned']
    ).count()
    
    return Response({
        'total_products': total_products,
        'low_stock_items': low_stock_items,
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
    })
