# Deploying Velma to Vercel

This guide explains how to deploy Velma to Vercel and connect it to your backend API.

## Important: Velma Architecture

Velma has **two components:**

1. **Frontend** (HTML/CSS/JavaScript) - Can be deployed to Vercel ✅
2. **Backend** (Python FastAPI) - Needs to be deployed separately ❌ (Vercel is optimized for Node.js)

## Deployment Options

### Option 1: Frontend Only on Vercel (Demo Mode)

Deploy just the frontend to Vercel with demo responses (no real backend).

**Pros:**
- ✅ Quickest deployment
- ✅ Works immediately
- ✅ No backend setup needed
- ✅ Perfect for demos/testing

**Cons:**
- ❌ No real AI responses
- ❌ No database
- ❌ No actual payroll calculations

### Option 2: Frontend on Vercel + Backend Elsewhere (Recommended)

Deploy frontend to Vercel, backend to Railway/Render/fly.io.

**Pros:**
- ✅ Full functionality
- ✅ Real AI responses
- ✅ Database integration
- ✅ Scalable

**Cons:**
- Requires separate backend deployment

---

## Option 1: Deploy Frontend Only (Demo Mode)

### Step 1: Push to GitHub

```bash
cd /path/to/NDIS
git add -A
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Connect to Vercel

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect `vercel.json`

### Step 3: Configure Build Settings

Vercel should auto-configure based on `vercel.json`:

- **Framework Preset:** Other
- **Build Command:** `echo 'No build needed'`
- **Output Directory:** `frontend`
- **Install Command:** (leave empty)

### Step 4: Deploy

Click "Deploy" - Done! ✅

Your Velma frontend will be live at:
```
https://your-project.vercel.app
```

**Demo Mode Active** - The frontend will show demo responses since there's no backend API.

---

## Option 2: Full Deployment (Frontend + Backend)

### Step 1: Deploy Backend API

Choose a platform for your Python backend:

#### A. Railway (Recommended)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables:
   ```env
   ANTHROPIC_API_KEY=your_key_here
   DATABASE_URL=postgresql://...
   ```
5. Railway will auto-detect Python and deploy

#### B. Render

1. Go to https://render.com
2. Click "New Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn velma.api.app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

#### C. Fly.io

```bash
fly launch
fly secrets set ANTHROPIC_API_KEY=your_key_here
fly deploy
```

#### D. Self-Hosted VPS

Use the deployment guide in `docs/DEPLOYMENT.md`.

### Step 2: Get Backend API URL

After backend deployment, you'll get a URL like:
- Railway: `https://your-app.up.railway.app`
- Render: `https://your-app.onrender.com`
- Fly.io: `https://your-app.fly.dev`

### Step 3: Configure Frontend

Edit `frontend/config.js`:

```javascript
window.VELMA_CONFIG = {
    API_BASE_URL: 'https://your-backend-api.railway.app',  // Your backend URL
    DEMO_MODE: false,  // Disable demo mode
    COMPANY_NAME: 'Your NDIS Company'
};
```

### Step 4: Deploy Frontend to Vercel

1. Push changes to GitHub:
   ```bash
   git add frontend/config.js
   git commit -m "Configure production API URL"
   git push
   ```

2. Vercel will auto-deploy the update

3. Visit `https://your-project.vercel.app`

✅ **You now have full Velma functionality!**

---

## Configuration

### Frontend Configuration (config.js)

```javascript
window.VELMA_CONFIG = {
    // Your backend API URL
    API_BASE_URL: 'https://your-backend.railway.app',

    // Demo mode (true = no backend needed, false = use real API)
    DEMO_MODE: false,

    // Company information
    COMPANY_NAME: 'Your NDIS Company',

    // Feature flags
    FEATURES: {
        CHAT: true,
        DASHBOARD: true,
        HR: true,
        PAYROLL: true,
        CALENDAR: true,
        TASKS: true
    }
};
```

### Backend Environment Variables

Set these on your backend platform (Railway/Render/etc.):

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...

# Company Info
COMPANY_NAME=Your NDIS Company
COMPANY_ABN=12345678901
TIMEZONE=Australia/Sydney

# Optional integrations
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
GOOGLE_CLIENT_ID=...
```

---

## Vercel Project Settings

### Environment Variables (if needed)

In Vercel dashboard → Settings → Environment Variables:

```env
# If you need any frontend-specific variables
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Custom Domain

1. Go to Settings → Domains
2. Add your custom domain
3. Follow DNS instructions
4. Enable SSL (automatic)

---

## Troubleshooting

### Frontend loads but shows demo responses

**Problem:** Frontend is in demo mode
**Solution:**
1. Check `config.js` has correct `API_BASE_URL`
2. Set `DEMO_MODE: false`
3. Verify backend is running
4. Check browser console for errors

### CSS/JS files not loading

**Problem:** 404 errors for static files
**Solution:**
1. Check `vercel.json` routes configuration
2. Verify `outputDirectory: "frontend"`
3. Clear Vercel build cache and redeploy

### CORS errors when connecting to backend

**Problem:** Backend blocking frontend requests
**Solution:** Add your Vercel domain to backend CORS config:

```python
# In velma/api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Backend API returns 404

**Problem:** Backend not deployed or URL wrong
**Solution:**
1. Verify backend is running: `curl https://your-backend.railway.app/health`
2. Check `config.js` has correct URL
3. Ensure backend has CORS enabled

---

## Cost Estimates

### Vercel (Frontend)
- **Free tier:** 100GB bandwidth, unlimited deployments
- **Pro ($20/month):** 1TB bandwidth, better performance
- **For most NDIS companies:** Free tier is sufficient

### Railway (Backend)
- **Free tier:** $5 credit/month
- **Typical usage:** $5-20/month depending on traffic
- **Includes:** PostgreSQL database, 8GB RAM

### Render (Backend Alternative)
- **Free tier:** Limited (sleeps after 15 min inactivity)
- **Starter ($7/month):** Always on, 512MB RAM
- **Standard ($25/month):** 2GB RAM, better performance

---

## Recommended Setup for Production

For a production NDIS company:

1. **Frontend:** Vercel (Free or Pro)
2. **Backend:** Railway Starter ($5-15/month)
3. **Database:** Railway PostgreSQL (included)
4. **Domain:** Your own domain ($10-20/year)
5. **Email:** SendGrid (Free tier: 100 emails/day)
6. **Total Cost:** ~$15-30/month

---

## Alternative: All-in-One Deployment

If you prefer not to split frontend/backend:

### Railway (Frontend + Backend together)

1. Deploy entire project to Railway
2. Railway serves both API and frontend
3. One platform, one bill
4. Cost: ~$10-20/month

### Render (Frontend + Backend together)

Similar to Railway, deploy everything together.

---

## Performance Tips

### Frontend (Vercel)
1. ✅ Enable Vercel Analytics
2. ✅ Use custom domain for better caching
3. ✅ Enable compression (automatic)
4. ✅ Monitor build times

### Backend (Railway/Render)
1. ✅ Use PostgreSQL (not SQLite)
2. ✅ Enable caching
3. ✅ Monitor API response times
4. ✅ Scale up if needed

---

## Support & Next Steps

### After Deployment

1. **Test thoroughly:**
   - Try all chat prompts
   - Test payroll calculations
   - Verify compliance tracking

2. **Monitor:**
   - Check Vercel analytics
   - Monitor backend logs
   - Watch for errors

3. **Customize:**
   - Update SCHADS rates annually
   - Add your branding
   - Configure integrations

### Get Help

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Velma Docs:** See `docs/` directory

---

## Summary

✅ **Demo Mode (Easiest):** Frontend-only on Vercel, demo responses
✅ **Production (Recommended):** Frontend on Vercel + Backend on Railway
✅ **All-in-One:** Deploy everything to Railway/Render

Choose the option that fits your needs and budget!

**Current Status:** Your Vercel deployment shows 404 because `vercel.json` needs to be configured properly. Follow the steps above to fix it.
