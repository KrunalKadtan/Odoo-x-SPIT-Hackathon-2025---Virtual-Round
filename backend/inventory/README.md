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
- `POST /pickings/` - Create a picking
- `GET /pickings/{id}/` - Get picking details
- `PUT /pickings/{id}/` - Update picking
- `DELETE /pickings/{id}/` - Delete picking
- `POST /pickings/{id}/confirm/` - Confirm a picking
- `POST /pickings/{id}/validate/` - Validate and process stock movements
- `POST /pickings/{id}/cancel/` - Cancel a picking

**Filters:** `status`, `operation_type`
**Search:** `reference`, `partner`

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
