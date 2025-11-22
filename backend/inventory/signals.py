"""
Signal handlers for inventory models.

Automatically creates history records when inventory changes occur.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import StockMove, Picking, MoveHistory


# Store previous picking status for comparison
_picking_previous_status = {}


@receiver(pre_save, sender=Picking)
def store_previous_picking_status(sender, instance, **kwargs):
    """
    Store the previous status of a picking before it's saved.
    
    This allows us to detect status changes in the post_save signal.
    """
    if instance.pk:
        try:
            old_instance = Picking.objects.get(pk=instance.pk)
            _picking_previous_status[instance.pk] = old_instance.status
        except Picking.DoesNotExist:
            _picking_previous_status[instance.pk] = None
    else:
        _picking_previous_status[instance.pk] = None


@receiver(post_save, sender=StockMove)
def create_stock_move_history(sender, instance, created, **kwargs):
    """
    Create a history record when a stock move is validated (status changes to 'done').
    
    Captures product, quantity, locations, user, and timestamp.
    Requirements: 1.1
    """
    # Only create history when status is 'done'
    if instance.status == 'done':
        # Check if we already have a history record for this move being done
        # to avoid duplicate entries on subsequent saves
        existing_history = MoveHistory.objects.filter(
            action_type='stock_move',
            picking=instance.picking,
            product=instance.product,
            quantity=instance.quantity,
            source_location=instance.source_location,
            destination_location=instance.destination_location
        ).first()
        
        # Only create if no existing history record found
        if not existing_history:
            MoveHistory.objects.create(
                action_type='stock_move',
                picking=instance.picking,
                product=instance.product,
                quantity=instance.quantity,
                source_location=instance.source_location,
                destination_location=instance.destination_location,
                user=instance.picking.created_by if instance.picking else None,
                notes=f"Stock move validated: {instance.notes}" if instance.notes else "Stock move validated"
            )


@receiver(post_save, sender=Picking)
def create_picking_status_change_history(sender, instance, created, **kwargs):
    """
    Create a history record when a picking status changes.
    
    Detects status changes by comparing old and new values.
    Captures old_status, new_status, picking reference, and user.
    Requirements: 1.2
    """
    # Get the previous status from our storage
    old_status = _picking_previous_status.get(instance.pk)
    
    # Only create history if status actually changed (and not on initial creation)
    if not created and old_status is not None and old_status != instance.status:
        MoveHistory.objects.create(
            action_type='status_change',
            picking=instance,
            old_status=old_status,
            new_status=instance.status,
            user=instance.created_by,
            notes=f"Picking status changed from {old_status} to {instance.status}"
        )
    
    # Clean up the stored status
    if instance.pk in _picking_previous_status:
        del _picking_previous_status[instance.pk]
