# Inventory Management System

A comprehensive inventory management system for StockMaster with support for products, locations, stock movements, and warehouse operations.

## Features

### Models

1. **Category** - Hierarchical product categorization
2. **Product** - Product management with SKU, pricing, and barcodes
3. **Location** - Hierarchical warehouse locations with usage types
4. **OperationType** - Define operation rules (Receipts, Deliveries, Transfers)
5. **Picking** - Stock movement headers (Delivery Orders, Receipts)
6. **StockMove** - Individual line items in pickings
7. **Task** - Warehouse task management
8. **StockQuant** - Real-time inventory levels by location
9. **MoveHistory** - Audit trail of all inventory movements and status changes
10. **WarehouseSettings** - Configurable warehouse parameters (singleton)

### API Endpoints

All endpoints are prefixed with `/api/inventory/`

#### Categories
- `GET /categories/` - List all categories
- `POST /categories/` - Create a category
- `GET /categories/{id}/` - Get category details
- `PUT /categories/{id}/` - Update category
- `DELETE /categories/{id}/` - Delete category
- `GET /categories/{id}/children/` - Get child categories

#### Products
- `GET /products/` - List all products
- `POST /products/` - Create a product
- `GET /products/{id}/` - Get product details
- `PUT /products/{id}/` - Update product
- `DELETE /products/{id}/` - Delete product
- `GET /products/{id}/stock_levels/` - Get stock levels for product

**Filters:** `category`, `is_active`
**Search:** `sku`, `name`, `barcode`

#### Locations
- `GET /locations/` - List all locations
- `POST /locations/` - Create a location
- `GET /locations/{id}/` - Get location details
- `PUT /locations/{id}/` - Update location
- `DELETE /locations/{id}/` - Delete location
- `GET /locations/{id}/stock_levels/` - Get stock at location

**Filters:** `usage_type`, `is_active`
**Search:** `name`, `barcode`

#### Operation Types
- `GET /operation-types/` - List all operation types
- `POST /operation-types/` - Create an operation type
- `GET /operation-types/{id}/` - Get operation type details
- `PUT /operation-types/{id}/` - Update operation type
- `DELETE /operation-types/{id}/` - Delete operation type

**Filters:** `code`
**Search:** `name`, `sequence_prefix`

#### Pickings
- `GET /pickings/` - List all pickings
- `POST /pickings/` - Create a picking (supports nested stock moves)
- `GET /pickings/{id}/` - Get picking details
- `PUT /pickings/{id}/` - Update picking (supports nested stock moves)
- `DELETE /pickings/{id}/` - Delete picking
- `POST /pickings/{id}/confirm/` - Confirm a picking
- `POST /pickings/{id}/validate/` - Validate and process stock movements
- `POST /pickings/{id}/cancel/` - Cancel a picking

**Filters:** `status`, `operation_type`
**Search:** `reference`, `partner`

##### Nested Stock Moves Creation

You can create a picking with all its stock moves in a single API call. This simplifies the workflow and ensures data consistency through atomic transactions.

**Example Request (with nested stock_moves):**
```bash
POST /api/inventory/pickings/
Content-Type: application/json

{
  "reference": "REC/001",
  "partner": "Supplier ABC",
  "operation_type": 1,
  "source_location": 2,
  "destination_location": 1,
  "scheduled_date": "2025-11-22T10:00:00Z",
  "notes": "Monthly stock receipt",
  "stock_moves": [
    {
      "product": 3,
      "quantity": "10.00",
      "notes": "Batch A123"
    },
    {
      "product": 4,
      "quantity": "25.00",
      "notes": "Batch B456"
    }
  ]
}
```

**Example Response:**
```json
{
  "id": 5,
  "reference": "REC/001",
  "partner": "Supplier ABC",
  "operation_type": {
    "id": 1,
    "name": "Receipts",
    "code": "receipt"
  },
  "source_location": {
    "id": 2,
    "name": "Suppliers"
  },
  "destination_location": {
    "id": 1,
    "name": "Main Warehouse / Stock"
  },
  "scheduled_date": "2025-11-22T10:00:00Z",
  "status": "draft",
  "notes": "Monthly stock receipt",
  "stock_moves": [
    {
      "id": 10,
      "product": {
        "id": 3,
        "sku": "LAP-001",
        "name": "Laptop"
      },
      "quantity": "10.00",
      "notes": "Batch A123",
      "status": "draft"
    },
    {
      "id": 11,
      "product": {
        "id": 4,
        "sku": "MOU-001",
        "name": "Mouse"
      },
      "quantity": "25.00",
      "notes": "Batch B456",
      "status": "draft"
    }
  ],
  "created_at": "2025-11-22T09:45:00Z",
  "updated_at": "2025-11-22T09:45:00Z"
}
```

**Backward Compatibility:**
The `stock_moves` field is optional. You can still create pickings without nested moves and add stock moves separately.

**Example Request (without nested stock_moves):**
```bash
POST /api/inventory/pickings/
Content-Type: application/json

{
  "reference": "REC/002",
  "partner": "Supplier XYZ",
  "operation_type": 1,
  "source_location": 2,
  "destination_location": 1,
  "scheduled_date": "2025-11-23T10:00:00Z"
}
```

##### Nested Stock Moves Updates

You can update a picking and modify its stock moves in a single request. The system supports:
- **Adding new moves**: Include moves without an `id` field
- **Updating existing moves**: Include moves with an `id` field
- **Removing moves**: Omit moves from the array (they will be deleted)

**Example Request (updating with nested stock_moves):**
```bash
PUT /api/inventory/pickings/5/
Content-Type: application/json

{
  "reference": "REC/001-UPDATED",
  "partner": "Supplier ABC",
  "operation_type": 1,
  "source_location": 2,
  "destination_location": 1,
  "scheduled_date": "2025-11-22T10:00:00Z",
  "notes": "Updated receipt",
  "stock_moves": [
    {
      "id": 10,
      "product": 3,
      "quantity": "15.00",
      "notes": "Batch A123 - Updated quantity"
    },
    {
      "product": 5,
      "quantity": "30.00",
      "notes": "New product added"
    }
  ]
}
```

In this example:
- Move with `id: 10` is updated with new quantity and notes
- Move with `id: 11` is removed (not included in the array)
- A new move for product 5 is created (no `id` field)

##### Validation Errors

**Empty stock_moves array:**
```json
{
  "stock_moves": ["At least one stock move is required"]
}
```

**Invalid product ID:**
```json
{
  "stock_moves": [
    {},
    {
      "product": ["Product with id 999 does not exist"]
    }
  ]
}
```

**Negative quantity:**
```json
{
  "stock_moves": [
    {
      "quantity": ["Ensure this value is greater than or equal to 0."]
    }
  ]
}
```

**Transaction Rollback:**
If any stock move fails validation, the entire operation is rolled back. Neither the picking nor any stock moves will be created/updated.

#### Stock Moves
- `GET /stock-moves/` - List all stock moves
- `POST /stock-moves/` - Create a stock move
- `GET /stock-moves/{id}/` - Get stock move details
- `PUT /stock-moves/{id}/` - Update stock move
- `DELETE /stock-moves/{id}/` - Delete stock move

**Filters:** `status`, `picking`, `product`
**Search:** `product__sku`, `product__name`

#### Tasks
- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create a task
- `GET /tasks/{id}/` - Get task details
- `PUT /tasks/{id}/` - Update task
- `DELETE /tasks/{id}/` - Delete task
- `GET /tasks/my_tasks/` - Get tasks assigned to current user
- `POST /tasks/{id}/complete/` - Mark task as completed

**Filters:** `status`, `priority`, `assigned_to`
**Search:** `title`, `description`

#### Stock Quantities
- `GET /stock-quants/` - List all stock quantities (read-only)
- `GET /stock-quants/{id}/` - Get stock quantity details
- `GET /stock-quants/low_stock/` - Get products with low stock (< 10)
- `GET /stock-quants/out_of_stock/` - Get out of stock products

**Filters:** `product`, `location`
**Search:** `product__sku`, `product__name`, `location__name`

#### Move History
- `GET /move-history/` - List all inventory movement history (read-only)
- `GET /move-history/{id}/` - Get specific history record details

**Filters:** `product`, `picking`, `action_type`, `user`, `date_from`, `date_to`
**Search:** `picking__reference`, `product__sku`
**Ordering:** `-timestamp` (newest first)

History records are automatically created when:
- Stock moves are validated (action_type: 'stock_move')
- Picking status changes (action_type: 'status_change')

**Example Request:**
```bash
GET /api/inventory/move-history/?product=3&date_from=2025-11-01&date_to=2025-11-30
```

**Example Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "timestamp": "2025-11-22T10:30:00Z",
      "user": {
        "id": 1,
        "login_id": "admin01"
      },
      "action_type": "stock_move",
      "picking": {
        "id": 5,
        "reference": "REC/001"
      },
      "product": {
        "id": 3,
        "sku": "LAP-001",
        "name": "Laptop"
      },
      "quantity": "10.00",
      "source_location": {
        "id": 2,
        "name": "Suppliers"
      },
      "destination_location": {
        "id": 1,
        "name": "Main Warehouse / Stock"
      },
      "old_status": null,
      "new_status": null,
      "notes": "Receipt validated"
    },
    {
      "id": 2,
      "timestamp": "2025-11-22T10:25:00Z",
      "user": {
        "id": 1,
        "login_id": "admin01"
      },
      "action_type": "status_change",
      "picking": {
        "id": 5,
        "reference": "REC/001"
      },
      "product": null,
      "quantity": null,
      "source_location": null,
      "destination_location": null,
      "old_status": "confirmed",
      "new_status": "done",
      "notes": "Picking validated"
    }
  ]
}
```

#### Warehouse Settings
- `GET /settings/` - Get current warehouse settings
- `PUT /settings/` - Update all warehouse settings
- `PATCH /settings/` - Partially update warehouse settings

Settings are stored as a singleton (only one record exists). The `updated_by` field is automatically set to the current user.

**Example Request:**
```bash
PUT /api/inventory/settings/
Content-Type: application/json

{
  "low_stock_threshold": 15,
  "default_receipt_location": 1,
  "default_delivery_location": 3,
  "default_adjustment_location": 6
}
```

**Example Response:**
```json
{
  "id": 1,
  "low_stock_threshold": 15,
  "default_receipt_location": {
    "id": 1,
    "name": "Main Warehouse / Stock",
    "barcode": "LOC-STOCK"
  },
  "default_delivery_location": {
    "id": 3,
    "name": "Customers",
    "barcode": "LOC-CUST"
  },
  "default_adjustment_location": {
    "id": 6,
    "name": "Inventory Adjustment",
    "barcode": "LOC-ADJ"
  },
  "updated_at": "2025-11-22T10:30:00Z",
  "updated_by": {
    "id": 1,
    "login_id": "admin01"
  }
}
```

**Validation Errors:**
```json
{
  "default_receipt_location": ["Location with id 999 does not exist"]
}
```

```json
{
  "low_stock_threshold": ["Ensure this value is greater than or equal to 0."]
}
```

## Admin Interface

Access the Django admin at `/admin/` to manage inventory data with a user-friendly interface.

### Features:
- **Inline editing** of StockMove within Picking admin
- **Autocomplete fields** for foreign keys (products, locations)
- **Advanced filtering** and search capabilities
- **Hierarchical display** for categories and locations
- **Read-only timestamps** for audit trails

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Populate sample data:
```bash
python manage.py populate_inventory
```

4. Create a superuser (if not using sample data):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Sample Data

The `populate_inventory` command creates:
- 5 categories (Electronics, Computers, Accessories, Furniture, Office Chairs)
- 6 locations (Main Warehouse with hierarchical structure)
- 3 operation types (Receipts, Deliveries, Internal Transfers)
- 4 products (Laptop, Mouse, Keyboard, Chair)
- 4 stock quantities
- 3 pickings with stock moves
- 2 tasks
- 1 admin user (login_id: admin01, password: Admin@123)

## Workflow Example

### Receiving Stock (Receipt)

**Option 1: Nested Write (Recommended)**
1. Create a Picking with nested stock_moves in a single request
2. Confirm the picking: `POST /api/inventory/pickings/{id}/confirm/`
3. Validate to update stock: `POST /api/inventory/pickings/{id}/validate/`

**Option 2: Separate Requests**
1. Create a Picking with operation type "Receipts"
2. Add StockMove lines for products being received
3. Confirm the picking: `POST /api/inventory/pickings/{id}/confirm/`
4. Validate to update stock: `POST /api/inventory/pickings/{id}/validate/`

### Delivering to Customer

1. Create a Picking with operation type "Delivery Orders"
2. Add StockMove lines for products to deliver
3. Confirm and validate the picking
4. Stock is automatically deducted from source location

### Internal Transfer

1. Create a Picking with operation type "Internal Transfers"
2. Add StockMove lines for products to move
3. Validate to move stock between locations

## Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get tokens from the authentication endpoints:
- Login: `POST /api/auth/login/`
- Signup: `POST /api/auth/signup/`

## Models Relationships

```
Category (self-referential)
    └── Product
            └── StockMove
                    └── Picking
                            └── OperationType
            └── StockQuant
                    └── Location (self-referential)

Task
    └── Picking
    └── User (assigned_to)
```

## Status Workflows

### Picking Status Flow
1. **draft** → Initial state
2. **confirmed** → Ready for processing
3. **assigned** → Assigned to warehouse worker
4. **in_progress** → Being processed
5. **done** → Completed (stock updated)
6. **cancelled** → Cancelled

### Task Status Flow
1. **pending** → Not started
2. **in_progress** → Being worked on
3. **completed** → Finished
4. **cancelled** → Cancelled

## Notes

- Stock quantities are automatically updated when pickings are validated
- StockMove is not accessible as a standalone admin section (only via Picking inline)
- All timestamps are automatically managed
- Hierarchical paths are automatically calculated for categories and locations
