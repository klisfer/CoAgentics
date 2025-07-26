# 🔧 Fix API Port Issue (8000 vs 8002)

## 🚨 Problem
The frontend is making calls to `localhost:8000` instead of `localhost:8002` where the main2.py backend is running.

## ✅ Solution Steps

### Step 1: Create Environment File
Create `client/.env.local` with the following content:

```bash
# API Configuration for CoAgentics
# V1 API - Original system (runs on port 8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# V2 API - main2.py Financial Assistant (runs on port 8002)  
NEXT_PUBLIC_API_URL_V2=http://localhost:8002
```

### Step 2: Restart the Frontend
```bash
cd client
# Kill any existing dev server (Ctrl+C)
npm run dev
```

### Step 3: Verify the Configuration
Open browser console when testing and look for:
```
Making API call to: http://localhost:8002/chat
```

## 🧪 Test the Fix

### Quick Test:
1. Open `http://localhost:3000`
2. Make sure **v2 API** is selected (gear icon → v2)
3. Ask: *"What is my net worth?"*
4. Check browser console - should see:
   ```
   Making API call to: http://localhost:8002/chat
   ```

### If Still Getting Port 8000:

#### Option A: Clear Browser Cache
```bash
# Chrome/Edge: Open DevTools → Network tab → Disable cache
# Or try incognito/private browsing mode
```

#### Option B: Hard Restart Frontend
```bash
cd client
rm -rf .next
npm run dev
```

#### Option C: Check Environment Variables
In browser console, run:
```javascript
console.log('API URLs:', {
  v1: process.env.NEXT_PUBLIC_API_URL,
  v2: process.env.NEXT_PUBLIC_API_URL_V2
})
```

Should show:
```
{
  v1: "http://localhost:8000",
  v2: "http://localhost:8002"
}
```

## 🔍 Debug Commands

### Check What's Running on Ports:
```bash
# Check port 8002 (should show Python)
lsof -i :8002

# Check port 8000 (should be empty)
lsof -i :8000

# Check port 3000 (should show Next.js)
lsof -i :3000
```

### Test Backend Directly:
```bash
# Test main2.py backend
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","new_message":"Hello"}'

# Should get response like:
# {"session_id":"...","response_text":"..."}
```

### Check Frontend API Calls:
1. Open browser DevTools → Network tab
2. Send a message in chat with v2 selected
3. Look for the API call - should be to `localhost:8002/chat`

## 📋 Complete Working Setup

### Terminal 1: Fi MCP Server
```bash
# Start your Fi MCP server
cd /path/to/fi-mcp-server
./start-server.sh
# Should run on localhost:8080
```

### Terminal 2: main2.py Backend
```bash
cd server
source venv/bin/activate
python3 app/main2.py
# Should run on localhost:8002
```

### Terminal 3: Frontend
```bash
cd client
npm run dev
# Should run on localhost:3000
```

## 🎯 Expected Result

- **V1 API calls** → `http://localhost:8000/api/v1/...` (original system)
- **V2 API calls** → `http://localhost:8002/chat` (main2.py)
- **Demo calls** → Use V1 API for simple responses

## ⚠️ Common Issues

### Issue: Still seeing port 8000
**Cause:** Environment variables not loaded or cached
**Fix:** 
1. Restart frontend with `rm -rf .next && npm run dev`
2. Check `.env.local` file exists and has correct content
3. Try incognito/private browsing

### Issue: "Connection refused" on 8002
**Cause:** main2.py not running
**Fix:** Start main2.py with `python3 app/main2.py`

### Issue: API calls work but auth doesn't
**Cause:** Fi MCP server not running
**Fix:** Start Fi MCP server on port 8080

## ✅ Success Indicators

When working correctly, you should see:
- ✅ Console: "Making API call to: http://localhost:8002/chat"
- ✅ Network tab: POST to `localhost:8002/chat`
- ✅ No errors about connection refused
- ✅ Authentication flow works for financial questions 