"""
URL configuration for inventory API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    CategoryViewSet, ProductViewSet, LocationViewSet,
    OperationTypeViewSet, PickingViewSet, StockMoveViewSet,
    TaskViewSet, StockQuantViewSet, MoveHistoryViewSet, WarehouseSettingsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'operation-types', OperationTypeViewSet, basename='operationtype')
router.register(r'pickings', PickingViewSet, basename='picking')
router.register(r'stock-moves', StockMoveViewSet, basename='stockmove')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'stock-quants', StockQuantViewSet, basename='stockquant')
router.register(r'move-history', MoveHistoryViewSet, basename='movehistory')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    # Custom route for settings endpoint (singleton pattern)
    path('settings/', WarehouseSettingsViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'partial_update'
    }), name='warehouse-settings'),
]
