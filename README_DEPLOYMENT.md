# Velma NDIS - Deployment Guide

## ✅ Ready for Vercel Deployment

This project is now configured for **instant deployment to Vercel** as a pure HTML5 static site.

## 📁 Project Structure

```
NDIS/
├── index.html              ← Main dashboard
├── chat.html              ← AI Chat interface
├── payroll.html           ← SCHADS Payroll Calculator
├── config.js              ← Frontend configuration
├── favicon.svg            ← Site favicon
├── css/                   ← Stylesheets
│   ├── velma-core.css
│   └── velma-components.css
├── js/                    ← JavaScript
│   ├── velma-core.js
│   ├── chat.js
│   ├── dashboard.js
│   └── schads-calculator.js
├── vercel.json            ← Vercel configuration
├── frontend/              ← Original frontend (backup)
└── velma/                 ← Python backend (optional)
```

## 🚀 Deploy to Vercel

### One-Click Deploy

1. **Push to GitHub:**
   ```bash
   git add -A
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Click "Deploy" (no configuration needed!)

3. **Done! 🎉**
   - Your site will be live at `https://your-project.vercel.app`
   - All features work instantly

## 🎯 What Works Out of the Box

### ✅ Dashboard (index.html)
- Statistics overview
- Recent activity
- Upcoming tasks
- Compliance alerts

### ✅ AI Chat (chat.html)
- Interactive chat interface
- Demo mode with realistic responses
- Suggested prompts for common queries
- Session persistence

### ✅ Payroll Calculator (payroll.html)
- Complete SCHADS Award calculator
- All 11 classification levels
- Automatic penalty rate calculations
- Allowances (sleepover, meal, travel, broken shift)
- Superannuation calculation
- Real-time results
- **100% JavaScript - No backend needed!**

## 💡 Features

### Pure HTML5 Platform
- ✅ No build step required
- ✅ No Node.js dependencies
- ✅ No Python backend needed
- ✅ Works 100% in the browser
- ✅ Instant loading
- ✅ Free hosting on Vercel

### SCHADS Payroll Calculator
- All classification levels (1.1 to 4.3)
- Penalty rates: Afternoon, Night, Saturday, Sunday, Public Holiday
- Allowances: Sleepover, Broken Shift, Meal, Travel
- Superannuation (11.5%)
- Leave loading (17.5%)
- Period-by-period breakdown
- Print-friendly results

### Demo Mode
- Realistic AI responses for common queries
- SCHADS rates information
- Compliance requirements
- Pay calculation examples
- Onboarding guides
- Leave loading explanations

## 🔧 Configuration

### 1. Edit `config.js` to customize:

```javascript
window.VELMA_CONFIG = {
    // Set to your backend API if you deploy one
    API_BASE_URL: '',

    // true = demo mode (no backend), false = use real API
    DEMO_MODE: true,

    // Your company details
    COMPANY_NAME: 'Your NDIS Company',

    // Enable/disable features
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

### 2. Configure AI Chat (Required for Full Functionality)

To enable real AI responses instead of demo mode, add your Anthropic API key to Vercel:

**Via Vercel Dashboard:**
1. Go to your project **Settings** → **Environment Variables**
2. Add `ANTHROPIC_API_KEY` with your API key from https://console.anthropic.com/
3. Optionally add `AI_MODEL` (default: `claude-sonnet-4-5-20250929`)
4. **Redeploy** your application

**Via Vercel CLI:**
```bash
vercel env add ANTHROPIC_API_KEY
# Paste your API key
vercel --prod
```

**For detailed instructions, see:** [VERCEL_SETUP.md](VERCEL_SETUP.md)

**Benefits:**
- ✅ API key stored securely on server (never exposed to clients)
- ✅ Real AI responses powered by Claude
- ✅ Automatic fallback to demo mode if not configured

## 🌐 Access Your Site

After deployment, you can access:

- **Dashboard:** `https://your-project.vercel.app`
- **Chat:** `https://your-project.vercel.app/chat.html`
- **Payroll:** `https://your-project.vercel.app/payroll.html`

## 🔄 Updates

To update your deployed site:

```bash
# Make changes to HTML/CSS/JS files
git add -A
git commit -m "Update description"
git push origin main
```

Vercel will automatically redeploy within seconds!

## 📱 Mobile Responsive

All pages are fully responsive and work on:
- Desktop
- Tablet
- Mobile phones
- All modern browsers

## 🎨 Customization

### Colors
Edit `css/velma-core.css`:
```css
:root {
  --color-primary: #0066CC;
  --color-secondary: #00A896;
}
```

### Company Name
Edit `config.js`:
```javascript
COMPANY_NAME: 'Your NDIS Company Name'
```

### Rates (Update Annually)
Edit `js/schads-calculator.js`:
```javascript
this.BASE_RATES = {
    "2.1": 28.45,  // Update with current rates
    // ...
};
```

## 📊 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android 90+)

## 💰 Cost

**FREE** on Vercel:
- Unlimited bandwidth (within limits)
- Automatic SSL
- CDN hosting worldwide
- Instant deployments

## 🆘 Troubleshooting

### Site not loading?
1. Check Vercel deployment status
2. Verify files are in root directory (not `frontend/`)
3. Check browser console for errors (F12)

### CSS not loading?
1. Clear browser cache (Ctrl+Shift+R)
2. Check that `css/` folder exists in root
3. Verify paths in HTML files are `/css/...`

### Calculator not working?
1. Check browser console for JavaScript errors
2. Ensure `js/schads-calculator.js` is loaded
3. Try in a different browser

## 📚 Documentation

- `frontend/README.md` - Frontend details
- `QUICK_START.md` - Local development
- `DEPLOYMENT_VERCEL.md` - Advanced deployment

## ✨ What's Next?

Add more features (all pure HTML5):
1. HR Compliance Tracker
2. Timesheet Manager
3. Leave Calculator
4. Employee Database (localStorage)
5. Report Generator
6. CSV/PDF Export

All can be added without a backend!

## 🎉 You're Ready!

Your Velma NDIS platform is ready to deploy. Just push to GitHub and connect to Vercel!

**Questions?** Check the documentation or open an issue.
