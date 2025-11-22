"""
Inventory management models for StockMaster.

This module contains models for managing products, locations, stock movements,
and inventory operations.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Category(models.Model):
    """
    Hierarchical category model for organizing products.
    
    Supports parent-child relationships for nested categories.
    """
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.get_full_path()
    
    def get_full_path(self):
        """Return the full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.get_full_path()} / {self.name}"
        return self.name


class Product(models.Model):
    """
    Product model representing items in inventory.
    
    Contains SKU, pricing, and categorization information.
    """
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    uom = models.CharField(
        max_length=50,
        default='Units',
        help_text="Unit of Measure (e.g., kg, pcs, dozen, liters)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['sku']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"


class Location(models.Model):
    """
    Hierarchical location model for warehouse management.
    
    Supports different usage types (internal, customer, supplier, etc.).
    """
    USAGE_TYPES = [
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('supplier', 'Supplier Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location'),
    ]
    
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, default='internal')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'locations'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['name']
    
    def __str__(self):
        return self.get_full_path()
    
    def get_full_path(self):
        """Return the full hierarchical path of the location."""
        if self.parent:
            return f"{self.parent.get_full_path()} / {self.name}"
        return self.name


class OperationType(models.Model):
    """
    Operation type model defining rules for stock movements.
    
    Examples: Receipts, Deliveries, Internal Transfers, Returns.
    """
    OPERATION_CODES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('internal', 'Internal Transfer'),
        ('manufacturing', 'Manufacturing'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, choices=OPERATION_CODES)
    sequence_prefix = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    default_source_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_operation_types'
    )
    default_destination_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_operation_types'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'operation_types'
        verbose_name = 'Operation Type'
        verbose_name_plural = 'Operation Types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sequence_prefix})"


class Picking(models.Model):
    """
    Picking model representing the header for stock movements.
    
    Acts as a delivery order or transfer order containing multiple stock moves.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    reference = models.CharField(max_length=50, unique=True, db_index=True, blank=True)
    partner = models.CharField(max_length=200, blank=True)
    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.PROTECT,
        related_name='pickings'
    )
    source_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='source_pickings'
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='destination_pickings'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_pickings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pickings'
        verbose_name = 'Picking'
        verbose_name_plural = 'Pickings'
        ordering = ['-scheduled_date']
    
    def save(self, *args, **kwargs):
        """Auto-generate reference if not provided."""
        if not self.reference:
            # Generate reference based on operation type prefix and sequence
            prefix = self.operation_type.sequence_prefix if self.operation_type else 'PICK'
            # Get the last picking with this prefix
            last_picking = Picking.objects.filter(
                reference__startswith=prefix
            ).order_by('-id').first()
            
            if last_picking and last_picking.reference:
                # Extract number from last reference
                try:
                    last_num = int(last_picking.reference.replace(prefix, ''))
                    next_num = last_num + 1
                except (ValueError, AttributeError):
                    next_num = 1
            else:
                next_num = 1
            
            # Generate new reference with zero-padding
            self.reference = f"{prefix}{next_num:05d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.partner}"


class StockMove(models.Model):
    """
    Stock move model representing individual line items in a picking.
    
    Tracks movement of specific products between locations.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    picking = models.ForeignKey(
        Picking,
        on_delete=models.CASCADE,
        related_name='stock_moves'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='stock_moves'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    source_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='source_stock_moves'
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='destination_stock_moves'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_moves'
        verbose_name = 'Stock Move'
        verbose_name_plural = 'Stock Moves'
        ordering = ['picking', 'id']
    
    def __str__(self):
        return f"{self.picking.reference} - {self.product.sku} ({self.quantity})"


class Task(models.Model):
    """
    Task model for managing warehouse tasks and assignments.
    
    Can be linked to pickings for tracking work assignments.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    related_picking = models.ForeignKey(
        Picking,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class StockQuant(models.Model):
    """
    Stock quantity model for tracking current inventory levels.
    
    Represents the quantity of a product at a specific location.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_quants'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='stock_quants'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    reserved_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_quants'
        verbose_name = 'Stock Quantity'
        verbose_name_plural = 'Stock Quantities'
        unique_together = ['product', 'location']
        ordering = ['product', 'location']
    
    def __str__(self):
        return f"{self.product.sku} @ {self.location.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Calculate available quantity (total - reserved)."""
        return self.quantity - self.reserved_quantity


class MoveHistory(models.Model):
    """
    Move history model for audit logging of inventory movements and status changes.
    
    Tracks all inventory movements and picking status changes for accountability.
    """
    ACTION_TYPES = [
        ('stock_move', 'Stock Move'),
        ('status_change', 'Status Change'),
        ('adjustment', 'Adjustment'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='move_history'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    picking = models.ForeignKey(
        Picking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='move_history',
        db_index=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='move_history',
        db_index=True
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    source_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_move_history'
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_move_history'
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'move_history'
        verbose_name = 'Move History'
        verbose_name_plural = 'Move History'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['product']),
            models.Index(fields=['picking']),
        ]
    
    def __str__(self):
        if self.action_type == 'stock_move' and self.product:
            return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.product.sku} moved ({self.quantity})"
        elif self.action_type == 'status_change' and self.picking:
            return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.picking.reference} status: {self.old_status} → {self.new_status}"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.get_action_type_display()}"
    
    def get_action_display(self):
        """Return formatted action description."""
        if self.action_type == 'stock_move':
            if self.product and self.source_location and self.destination_location:
                return f"Moved {self.quantity} {self.product.sku} from {self.source_location.name} to {self.destination_location.name}"
            elif self.product:
                return f"Moved {self.quantity} {self.product.sku}"
            return "Stock movement"
        elif self.action_type == 'status_change':
            if self.picking:
                return f"{self.picking.reference} status changed from {self.old_status} to {self.new_status}"
            return f"Status changed from {self.old_status} to {self.new_status}"
        elif self.action_type == 'adjustment':
            if self.product:
                return f"Inventory adjustment for {self.product.sku}: {self.quantity}"
            return "Inventory adjustment"
        return self.get_action_type_display()


class WarehouseSettings(models.Model):
    """
    Warehouse settings model for storing configurable warehouse parameters.
    
    Implements singleton pattern to ensure only one settings record exists.
    """
    low_stock_threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Threshold for low stock alerts"
    )
    default_receipt_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receipt_settings'
    )
    default_delivery_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_settings'
    )
    default_adjustment_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjustment_settings'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_settings'
    )
    
    class Meta:
        db_table = 'warehouse_settings'
        verbose_name = 'Warehouse Settings'
        verbose_name_plural = 'Warehouse Settings'
    
    def __str__(self):
        return f"Warehouse Settings (Low Stock Threshold: {self.low_stock_threshold})"
    
    def save(self, *args, **kwargs):
        """Override save to enforce singleton pattern."""
        if not self.pk and WarehouseSettings.objects.exists():
            # If trying to create a new record when one already exists, update the existing one
            existing = WarehouseSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Retrieve or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
