# Cheryl Quick Start Guide

Get Cheryl up and running in 5 minutes!

## Prerequisites

- **Python 3.9+** installed
- **Internet connection** (for installing dependencies)
- **Anthropic API key** (for Claude AI integration)

## Option 1: Quick Start (Recommended)

### Linux/Mac
```bash
cd /path/to/NDIS
./start_cheryl.sh
```

### Windows
```cmd
cd C:\path\to\NDIS
start_cheryl.bat
```

The script will:
1. Create a virtual environment (if needed)
2. Install dependencies
3. Create .env file from template
4. Start the Cheryl server

**Access Cheryl:**
- **Frontend Dashboard**: http://localhost:8000
- **Chat Interface**: http://localhost:8000/chat.html
- **API Documentation**: http://localhost:8000/docs

## Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
cd /path/to/NDIS
python -m venv venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required configuration in .env:**
```env
# Anthropic API Key (REQUIRED)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (SQLite for testing, PostgreSQL for production)
DATABASE_URL=sqlite:///./cheryl.db

# Company Information
COMPANY_NAME=Your NDIS Company Name
COMPANY_ABN=12345678901
TIMEZONE=Australia/Sydney
```

### 5. Initialize Database (Optional)

```bash
python scripts/init_db.py
```

### 6. Start the Server

```bash
python scripts/run_api.py
```

The server will start on http://localhost:8000

## Accessing Cheryl

### Frontend Interface (Recommended)

1. **Dashboard**: Open http://localhost:8000 in your browser
   - View statistics, recent activity, and upcoming tasks
   - Quick access to all modules

2. **Chat Interface**: Navigate to http://localhost:8000/chat.html
   - Interactive AI chat with Cheryl
   - Suggested prompts for common tasks
   - Real-time conversation

3. **Other Modules**:
   - HR & Compliance: http://localhost:8000/hr.html (coming soon)
   - Payroll: http://localhost:8000/payroll.html (coming soon)
   - Calendar: http://localhost:8000/calendar.html (coming soon)

### API Interface

**API Documentation**: http://localhost:8000/docs
- Interactive Swagger UI
- Test API endpoints
- View request/response schemas

**Health Check**: http://localhost:8000/health
- Verify server is running

## First Steps

### 1. Try the Chat Interface

Navigate to http://localhost:8000/chat.html and try these prompts:

- "What are the current SCHADS Award rates for 2026?"
- "Calculate pay for Level 2.1 worker, Saturday 9am-5pm"
- "What compliance documents do NDIS workers need?"
- "How do I onboard a new employee?"
- "Explain leave loading for annual leave"

### 2. Explore the Dashboard

Visit http://localhost:8000 to see:
- Staff statistics
- Compliance rates
- Expiring credentials
- Recent activity
- Upcoming tasks

### 3. Check API Documentation

Go to http://localhost:8000/docs to:
- View all available endpoints
- Test API calls
- Understand request/response formats

## Configuration

### API Keys

**Anthropic API Key** (Required for AI features):
1. Sign up at https://console.anthropic.com
2. Create an API key
3. Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

### Optional Integrations

Edit `.env` to configure:

**Email (SendGrid):**
```env
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=cheryl@yourcompany.com.au
```

**SMS (Twilio):**
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+61400000000
```

**Calendar (Google):**
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

### SCHADS Award Rates

Update rates annually in `config/cheryl_config.yaml`:
```yaml
payroll:
  schads_award:
    version: "2026"
    penalty_rates:
      saturday: 1.5
      sunday: 1.75
      # ...
```

## Troubleshooting

### Frontend not loading?

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check browser console** (F12) for errors

3. **Verify file paths:**
   - CSS files: http://localhost:8000/css/cheryl-core.css
   - JS files: http://localhost:8000/js/cheryl-core.js
   - Favicon: http://localhost:8000/favicon.svg

### API connection issues?

1. **Verify ANTHROPIC_API_KEY in .env**
2. **Check logs in terminal**
3. **Test health endpoint**: http://localhost:8000/health

### CSS/JS not loading?

1. **Clear browser cache** (Ctrl+Shift+R / Cmd+Shift+R)
2. **Check network tab** in browser dev tools
3. **Verify frontend directory exists** at `/path/to/NDIS/frontend/`

### Port already in use?

Change port in `.env`:
```env
API_PORT=8001
```

Or specify when running:
```bash
uvicorn cheryl.api.app:app --host 0.0.0.0 --port 8001
```

## Development Mode

For development with auto-reload:

```bash
uvicorn cheryl.api.app:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production setup with:
- Nginx reverse proxy
- SSL/HTTPS configuration
- PostgreSQL database
- Process management (systemd)
- Security hardening

## Next Steps

1. **Customize Configuration**
   - Edit `config/cheryl_config.yaml`
   - Set business hours
   - Configure modules
   - Update SCHADS rates

2. **Import Data**
   - Add employees
   - Set up participants
   - Configure rosters

3. **Explore Features**
   - Try different chat prompts
   - Test payroll calculations
   - Check compliance tracking

4. **Read Documentation**
   - [Features Guide](docs/FEATURES.md)
   - [API Reference](docs/api.md)
   - [NDIS Compliance](docs/ndis_compliance.md)

## Getting Help

- **Documentation**: Check the `docs/` directory
- **API Docs**: http://localhost:8000/docs
- **Frontend README**: `frontend/README.md`
- **Issues**: Report at project repository

## System Requirements

**Minimum:**
- Python 3.9+
- 2GB RAM
- 1GB disk space

**Recommended:**
- Python 3.11+
- 4GB RAM
- 5GB disk space
- PostgreSQL database

**Browser Support:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Summary

✅ **Easy Setup**: One command to start
✅ **Modern Frontend**: Clinical-styled HTML5 interface
✅ **AI-Powered**: Claude Sonnet 4.5 integration
✅ **NDIS-Specific**: Payroll, HR, compliance modules
✅ **24/7 Available**: Always-on AI assistant

**You're ready to use Cheryl!** 🎉

Navigate to http://localhost:8000 and start exploring.
