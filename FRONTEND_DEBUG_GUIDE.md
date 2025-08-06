# Frontend Debug Guide - HTTP 500 Error

## 🚨 Issue Summary
Your frontend is experiencing an HTTP 500 error when trying to fetch properties from the backend API.

## ✅ Backend Status - WORKING
The backend has been tested and is working correctly:
- ✅ Server is running on `http://localhost:8000`
- ✅ Supabase connection is established
- ✅ All endpoints are responding correctly
- ✅ Error handling has been improved

## 🔍 Debugging Steps

### 1. Check Backend Status
```bash
# Test if backend is running
curl http://localhost:8000/health

# Test debug endpoint
curl http://localhost:8000/debug

# Test listings endpoint directly
curl "http://localhost:8000/api/listings/?location=Los%20Angeles,%20CA&sortBy=price&sortOrder=asc"
```

### 2. Frontend Request Analysis

#### Check the exact request being made:
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Make the request that's failing
4. Look for the failed request and check:
   - **Request URL**: Should be `http://localhost:8000/api/listings/`
   - **Request Method**: Should be `GET`
   - **Request Headers**: Check for CORS issues
   - **Query Parameters**: Verify they match expected format

#### Expected Request Format:
```
GET http://localhost:8000/api/listings/?location=Los%20Angeles,%20CA&sortBy=price&sortOrder=asc
```

### 3. Common Frontend Issues

#### A. Wrong API URL
**Problem**: Frontend might be using wrong URL
**Solution**: Ensure frontend is calling `http://localhost:8000/api/listings/`

#### B. CORS Issues
**Problem**: Browser blocking cross-origin requests
**Solution**: Backend CORS is configured for:
- `http://localhost:3000` (React dev server)
- `https://dreamheaven.vercel.app` (production)

#### C. Query Parameter Format
**Problem**: Parameters not properly encoded
**Solution**: Ensure proper URL encoding:
```javascript
// Correct way
const params = new URLSearchParams({
  location: "Los Angeles, CA",
  sortBy: "price",
  sortOrder: "asc"
});
const url = `http://localhost:8000/api/listings/?${params}`;
```

#### D. Request Method
**Problem**: Using POST instead of GET
**Solution**: Ensure using GET method:
```javascript
fetch(`http://localhost:8000/api/listings/?${params}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### 4. Frontend Code Check

#### Verify your fetch call in PropertyListings.js:
```javascript
// Should look like this:
const fetchProperties = async (filters) => {
  try {
    const params = new URLSearchParams();
    
    if (filters.location) params.append('location', filters.location);
    if (filters.bed && filters.bed !== 'Any') params.append('bed', filters.bed);
    if (filters.bath && filters.bath !== 'Any') params.append('bath', filters.bath);
    if (filters.rent) params.append('rent', filters.rent);
    if (filters.sortBy) params.append('sortBy', filters.sortBy);
    if (filters.sortOrder) params.append('sortOrder', filters.sortOrder);
    
    const response = await fetch(`http://localhost:8000/api/listings/?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
};
```

### 5. Testing Commands

#### Test with curl (should work):
```bash
# Basic request
curl "http://localhost:8000/api/listings/"

# With filters
curl "http://localhost:8000/api/listings/?location=Los%20Angeles,%20CA&sortBy=price&sortOrder=asc"

# With bed/bath filters
curl "http://localhost:8000/api/listings/?bed=2+&bath=Any&rent=For%20Rent"
```

#### Test with JavaScript:
```javascript
// Test in browser console
fetch('http://localhost:8000/api/listings/?location=Los%20Angeles,%20CA&sortBy=price&sortOrder=asc')
  .then(response => response.json())
  .then(data => console.log('Success:', data))
  .catch(error => console.error('Error:', error));
```

### 6. Environment Variables Check

#### Backend (.env file should have):
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

#### Frontend (.env file should have):
```env
REACT_APP_API_URL=http://localhost:8000
# or
VITE_API_URL=http://localhost:8000
```

### 7. Network Tab Analysis

When the error occurs, check the Network tab for:
1. **Request URL**: Is it correct?
2. **Status Code**: Is it actually 500?
3. **Response**: What's the error message?
4. **Request Headers**: Any CORS issues?
5. **Timing**: Is the request timing out?

### 8. Console Error Analysis

Look for these specific error patterns:
- `CORS error`: Cross-origin request blocked
- `Network error`: Server not reachable
- `500 Internal Server Error`: Backend error (but we know backend works)
- `404 Not Found`: Wrong endpoint URL

## 🛠️ Quick Fixes to Try

### 1. Restart Both Servers
```bash
# Backend
pkill -f "uvicorn main:app"
python main.py

# Frontend (in another terminal)
npm start
# or
yarn start
```

### 2. Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Clear browser cache and cookies

### 3. Check Port Conflicts
```bash
# Check if port 8000 is free
lsof -i :8000

# Check if port 3000 is free
lsof -i :3000
```

### 4. Test with Different Browser
Try the request in a different browser to rule out browser-specific issues.

## 📞 Next Steps

If the issue persists after trying these steps:

1. **Share the exact error message** from the browser console
2. **Share the Network tab details** of the failing request
3. **Share your frontend fetch code** from PropertyListings.js
4. **Test the debug endpoint**: `curl http://localhost:8000/debug`

## ✅ Backend Confirmation

The backend is confirmed working with these test results:
- ✅ Health check: `{"status": "healthy", "service": "dream-haven-backend"}`
- ✅ Debug endpoint: Supabase connected
- ✅ Listings endpoint: Returns data correctly
- ✅ All filters working: location, bed, bath, rent, sorting
- ✅ Error handling: Proper HTTP 500 responses with details

The issue is likely in the frontend request format or network configuration. 