"""
Django admin configuration for inventory models.

This module registers all inventory models with custom admin interfaces,
including inline editing for StockMove within Picking.
"""

from django.contrib import admin
from .models import Category, Product, Location, OperationType, Picking, StockMove, Task, StockQuant, MoveHistory, WarehouseSettings


class StockMoveInline(admin.TabularInline):
    """
    Inline admin for StockMove records within Picking.
    
    This allows viewing and editing stock move lines directly
    on the Picking (Delivery Order) admin page.
    """
    model = StockMove
    extra = 1
    autocomplete_fields = ['product', 'source_location', 'destination_location']
    readonly_fields = ['created_at', 'updated_at']
    fields = [
        'product',
        'quantity',
        'source_location',
        'destination_location',
        'status',
        'created_at',
        'updated_at'
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model (Hierarchical)."""
    
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    autocomplete_fields = ['parent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'parent', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    
    list_display = ['sku', 'name', 'category', 'cost', 'price']
    list_filter = ['category', 'created_at']
    search_fields = ['sku', 'name']
    autocomplete_fields = ['category']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('sku', 'name', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('cost', 'price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin interface for Location model (Hierarchical with usage type)."""
    
    list_display = ['get_full_path', 'usage_type', 'parent', 'created_at']
    list_filter = ['usage_type', 'created_at']
    search_fields = ['name', 'barcode']
    autocomplete_fields = ['parent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'parent', 'barcode', 'usage_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_path(self, obj):
        """Display the full hierarchical path of the location."""
        return obj.get_full_path() if hasattr(obj, 'get_full_path') else obj.name
    get_full_path.short_description = 'Full Path'


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    """Admin interface for OperationType model."""
    
    list_display = ['name', 'sequence_prefix', 'code', 'created_at']
    list_filter = ['code', 'created_at']
    search_fields = ['name', 'sequence_prefix', 'code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Operation Type Information', {
            'fields': ('name', 'code', 'sequence_prefix', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Picking)
class PickingAdmin(admin.ModelAdmin):
    """
    Admin interface for Picking model (Header for stock movements).
    
    Includes inline editing of StockMove records.
    """
    
    list_display = [
        'reference',
        'partner',
        'operation_type',
        'status',
        'scheduled_date',
        'created_at'
    ]
    list_filter = ['status', 'operation_type', 'scheduled_date', 'created_at']
    search_fields = ['reference', 'partner']
    autocomplete_fields = ['operation_type', 'source_location', 'destination_location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [StockMoveInline]
    
    fieldsets = (
        ('Picking Information', {
            'fields': (
                'reference',
                'partner',
                'operation_type',
                'status'
            )
        }),
        ('Locations', {
            'fields': ('source_location', 'destination_location')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'completion_date')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'scheduled_date'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    
    list_display = [
        'title',
        'assigned_to',
        'related_picking',
        'status',
        'priority',
        'due_date',
        'created_at'
    ]
    list_filter = ['status', 'priority', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'assigned_to__username']
    autocomplete_fields = ['assigned_to', 'related_picking']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'related_picking', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'due_date'


@admin.register(StockQuant)
class StockQuantAdmin(admin.ModelAdmin):
    """Admin interface for StockQuant model."""
    
    list_display = [
        'product',
        'location',
        'quantity',
        'reserved_quantity',
        'get_available_quantity',
        'updated_at'
    ]
    list_filter = ['location', 'updated_at']
    search_fields = ['product__sku', 'product__name', 'location__name']
    autocomplete_fields = ['product', 'location']
    readonly_fields = ['created_at', 'updated_at', 'get_available_quantity']
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('product', 'location', 'quantity', 'reserved_quantity')
        }),
        ('Calculated Fields', {
            'fields': ('get_available_quantity',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_available_quantity(self, obj):
        """Display available quantity."""
        return obj.available_quantity
    get_available_quantity.short_description = 'Available Quantity'


# Note: StockMove is NOT registered as a standalone admin
# It is only accessible through the Picking admin via TabularInline


@admin.register(MoveHistory)
class MoveHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for MoveHistory model (Audit Log).
    
    Provides read-only access to inventory movement history and status changes.
    All fields are read-only to maintain audit trail integrity.
    """
    
    list_display = [
        'timestamp',
        'action_type',
        'user',
        'picking',
        'product',
        'quantity',
        'source_location',
        'destination_location',
        'old_status',
        'new_status'
    ]
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['picking__reference', 'product__sku', 'product__name', 'notes']
    readonly_fields = [
        'timestamp',
        'user',
        'action_type',
        'picking',
        'product',
        'quantity',
        'source_location',
        'destination_location',
        'old_status',
        'new_status',
        'notes'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('timestamp', 'user', 'action_type')
        }),
        ('Related Records', {
            'fields': ('picking', 'product')
        }),
        ('Movement Details', {
            'fields': ('quantity', 'source_location', 'destination_location')
        }),
        ('Status Change Details', {
            'fields': ('old_status', 'new_status')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of history records."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of history records to maintain audit trail."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent modification of history records to maintain audit trail."""
        return False


@admin.register(WarehouseSettings)
class WarehouseSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for WarehouseSettings model (Singleton).
    
    Manages warehouse configuration parameters. Only one settings record
    can exist (singleton pattern).
    """
    
    list_display = [
        'low_stock_threshold',
        'default_receipt_location',
        'default_delivery_location',
        'default_adjustment_location',
        'updated_at',
        'updated_by'
    ]
    readonly_fields = ['updated_at', 'updated_by']
    autocomplete_fields = [
        'default_receipt_location',
        'default_delivery_location',
        'default_adjustment_location'
    ]
    
    fieldsets = (
        ('Stock Thresholds', {
            'fields': ('low_stock_threshold',)
        }),
        ('Default Locations', {
            'fields': (
                'default_receipt_location',
                'default_delivery_location',
                'default_adjustment_location'
            )
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent creation of multiple settings records (singleton pattern)."""
        return not WarehouseSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings record."""
        return False
