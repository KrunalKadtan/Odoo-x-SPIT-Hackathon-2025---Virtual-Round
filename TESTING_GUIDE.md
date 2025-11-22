# Testing Guide for New Frontend Features

## Prerequisites

Before testing, ensure the following are running:

### 1. PostgreSQL Database
```bash
# Check if PostgreSQL is running (Windows)
# Open Services and look for PostgreSQL service
# OR use command:
pg_isready -h localhost -p 5432
```

### 2. Backend Server
```bash
cd virtual-round-personal/backend

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate

# Apply migrations (IMPORTANT - First time only)
python manage.py migrate

# Run the server
python manage.py runserver
```

Expected output: `Starting development server at http://127.0.0.1:8000/`

### 3. Frontend Development Server
```bash
cd virtual-round-personal/frontend

# Install dependencies (if not already done)
npm install

# Start the dev server
npm run dev
```

Expected output: `Local: http://localhost:5173/`

---

## Testing the Settings Page

### Access the Page
1. Open browser: `http://localhost:5173`
2. Login with your credentials
3. Navigate to **Settings** from the sidebar (gear icon)

### Test Cases

#### TC1: View Current Settings
- **Expected**: Page loads and displays current warehouse settings
- **Check**: 
  - Low stock threshold value is displayed
  - Default locations dropdowns are populated
  - Last updated information is shown

#### TC2: Update Low Stock Threshold
1. Change the "Low Stock Threshold" value (e.g., from 10 to 15)
2. Click "Save Settings"
3. **Expected**: 
   - Success message appears: "Settings saved successfully!"
   - Page refreshes with new value
   - Last updated timestamp changes

#### TC3: Update Default Locations
1. Select a location from "Default Receipt Location" dropdown
2. Select a location from "Default Delivery Location" dropdown
3. Select a location from "Default Adjustment Location" dropdown
4. Click "Save Settings"
5. **Expected**: 
   - Success message appears
   - Selected locations are saved
   - Dropdowns show the selected values after refresh

#### TC4: Reset Form
1. Make changes to any field
2. Click "Reset" button
3. **Expected**: Form resets to current saved values

#### TC5: Validation
1. Try to set low stock threshold to negative number
2. **Expected**: Browser validation prevents submission

#### TC6: Error Handling
1. Stop the backend server
2. Try to save settings
3. **Expected**: Error message appears: "Failed to save settings. Please try again."

---

## Testing the Move History Page

### Access the Page
1. Navigate to **Move History** from the sidebar (clock icon)

### Test Cases

#### TC1: View History List
- **Expected**: Page loads and displays list of move history entries
- **Check**:
  - Entries are displayed in chronological order (newest first)
  - Each entry shows timestamp, action type badge, and user
  - Entry count is displayed at the top

#### TC2: View Entry Details
1. Look at any history entry
2. **Expected**: Entry shows:
   - Action type badge (color-coded)
   - Timestamp
   - User who performed the action
   - Action description
   - Related details (picking, product, locations, quantity, status changes)
   - Notes (if any)

#### TC3: Filter by Action Type
1. Select "Stock Move" from Action Type dropdown
2. Click "Apply Filters"
3. **Expected**: Only stock move entries are displayed

#### TC4: Filter by Date Range
1. Select a "From Date" (e.g., yesterday)
2. Select a "To Date" (e.g., today)
3. Click "Apply Filters"
4. **Expected**: Only entries within the date range are displayed

#### TC5: Clear Filters
1. Apply some filters
2. Click "Clear" button
3. **Expected**: All filters are reset and all entries are displayed

#### TC6: Empty State
1. Apply filters that return no results
2. **Expected**: Empty state message appears:
   - Icon displayed
   - "No history entries found"
   - "Try adjusting your filters or check back later"

#### TC7: Action Type Badges
- **Expected**: Different action types have different colored badges:
  - Stock Move: Blue badge
  - Status Change: Purple badge
  - Adjustment: Amber badge

---

## Testing API Integration

### Using Browser DevTools

1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to Settings or Move History page

#### Check API Calls

**Settings Page:**
- `GET /api/inventory/settings/` - Should return 200 OK
- `GET /api/inventory/locations/` - Should return 200 OK
- `PUT /api/inventory/settings/` - Should return 200 OK (when saving)

**Move History Page:**
- `GET /api/inventory/move-history/` - Should return 200 OK
- Query parameters should be visible when filters are applied

#### Check Response Data

**Settings Response:**
```json
{
  "id": 1,
  "low_stock_threshold": 10,
  "default_receipt_location": { "id": 1, "name": "..." },
  "default_delivery_location": { "id": 2, "name": "..." },
  "default_adjustment_location": null,
  "updated_at": "2025-11-22T...",
  "updated_by": { "id": 1, "username": "..." }
}
```

**Move History Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2025-11-22T...",
    "user": { "id": 1, "username": "..." },
    "action_type": "stock_move",
    "action_display": "Moved 10 PROD001 from...",
    "picking": { "id": 1, "reference": "..." },
    "product": { "id": 1, "sku": "...", "name": "..." },
    ...
  }
]
```

---

## Common Issues and Solutions

### Issue 1: "Failed to load settings"
**Cause**: Backend not running or database not accessible
**Solution**: 
- Check backend server is running
- Check PostgreSQL is running
- Verify migrations are applied: `python manage.py migrate`

### Issue 2: Empty locations dropdown
**Cause**: No locations in database
**Solution**: 
- Create locations via Django admin: `http://localhost:8000/admin/`
- Or create locations via API

### Issue 3: No move history entries
**Cause**: No inventory movements have been performed yet
**Solution**: 
- Perform some inventory operations (create and validate pickings)
- Or check if MoveHistory model is being populated by backend signals/logic

### Issue 4: 401 Unauthorized errors
**Cause**: JWT token expired or invalid
**Solution**: 
- Logout and login again
- Check token refresh logic in api.js

### Issue 5: CORS errors
**Cause**: Backend CORS configuration
**Solution**: 
- Verify `.env` has: `CORS_ALLOWED_ORIGINS=http://localhost:5173`
- Restart backend server after changing .env

---

## Responsive Design Testing

### Desktop (1920x1080)
- All elements should be properly spaced
- Forms should be readable and not too wide
- Cards should have appropriate margins

### Tablet (768x1024)
- Layout should adapt to smaller screen
- Filters should stack vertically if needed
- Navigation should remain accessible

### Mobile (375x667)
- All content should be scrollable
- Buttons should be full-width
- Forms should be easy to fill on small screens
- Text should be readable without zooming

---

## Performance Testing

### Settings Page
- Initial load should be < 2 seconds
- Save operation should complete < 1 second
- No console errors

### Move History Page
- Initial load should be < 3 seconds (depends on entry count)
- Filter application should be instant
- Smooth scrolling through entries
- No memory leaks (check DevTools Memory tab)

---

## Accessibility Testing

### Keyboard Navigation
- Tab through all form fields
- Enter key should submit forms
- Escape key should close modals (if any)

### Screen Reader
- Form labels should be read correctly
- Error messages should be announced
- Success messages should be announced

### Color Contrast
- All text should be readable
- Badges should have sufficient contrast
- Focus states should be visible

---

## Success Criteria

✅ Settings page loads without errors
✅ Settings can be viewed and updated
✅ Move history page loads without errors
✅ History entries are displayed correctly
✅ Filters work as expected
✅ All API calls return 200 OK
✅ No console errors
✅ Responsive on all screen sizes
✅ Forms validate correctly
✅ Error handling works properly

---

## Reporting Issues

If you encounter any issues:

1. Check browser console for errors
2. Check Network tab for failed API calls
3. Check backend logs for server errors
4. Note the exact steps to reproduce
5. Take screenshots if applicable

---

## Next Steps After Testing

Once testing is complete and successful:

1. ✅ Mark features as production-ready
2. ✅ Update user documentation
3. ✅ Train users on new features
4. ✅ Monitor for any issues in production
5. ✅ Gather user feedback for improvements
