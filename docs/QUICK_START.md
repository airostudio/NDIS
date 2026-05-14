# Cheryl Quick Start Guide

Welcome to Cheryl, your NDIS Virtual AI Executive Suite!

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (optional, can use SQLite for testing)
- Redis (optional, for caching)
- Anthropic API key (Claude)

## Installation

### 1. Clone and Setup

```bash
cd NDIS
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys and configuration:

```env
ANTHROPIC_API_KEY=your_api_key_here
COMPANY_NAME=Your NDIS Company Name
COMPANY_ABN=12345678901
DATABASE_URL=sqlite:///cheryl.db  # Or PostgreSQL URL
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Run Cheryl

#### Option A: Interactive CLI Mode

```bash
python main.py
```

This starts an interactive chat where you can test Cheryl's capabilities.

#### Option B: API Server Mode

```bash
python scripts/run_api.py
```

Then visit:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Quick Test

Try these example interactions:

### HR Questions
```
You: What compliance documents do NDIS workers need?
Cheryl: [Provides comprehensive list of NDIS compliance requirements]

You: How do I onboard a new employee?
Cheryl: [Provides detailed onboarding checklist]
```

### Payroll Questions
```
You: Calculate pay for Level 2.1 worker, Saturday 9am-5pm
Cheryl: [Calculates exact pay with SCHADS Award rates]

You: What are the current SCHADS rates?
Cheryl: [Shows all classification levels and penalty rates]

You: Explain superannuation requirements
Cheryl: [Explains SG, rates, and compliance]
```

### General Assistant
```
You: Schedule a team meeting for next Tuesday at 2pm
Cheryl: [Helps schedule the meeting]

You: Who should I call about payroll questions?
Cheryl: [Provides appropriate contact information]
```

## Key Features

### 1. NDIS HR & Compliance
- Worker screening tracking
- Compliance document management
- Incident reporting
- Onboarding automation

### 2. SCHADS Award Payroll
- Automatic penalty rate calculations
- Timesheet validation
- Leave management
- STP reporting support

### 3. Executive Assistant
- Calendar management
- Email handling
- Task tracking
- Contact management

### 4. Receptionist
- Call routing
- Visitor management
- Information provision

## Configuration

Edit `config/cheryl_config.yaml` to customize:

- Module settings
- Business hours
- Penalty rates (update annually)
- Notification preferences
- Integration settings

## Getting Help

### In-App
Ask Cheryl: "How do I use this feature?"

### Documentation
- [Full Documentation](../README.md)
- [API Reference](./api.md)
- [NDIS Compliance Guide](./ndis_compliance.md)

### Support
For issues or questions, contact your system administrator.

## Next Steps

1. **Configure integrations**: Connect calendar, email, and payroll systems
2. **Import data**: Add employees, participants, and contacts
3. **Customize**: Adjust settings in `config/cheryl_config.yaml`
4. **Train staff**: Introduce team to Cheryl's capabilities
5. **Monitor**: Review audit logs and usage

## Security Notes

- Never commit `.env` file to version control
- Use strong encryption keys
- Regularly update compliance documents
- Review audit logs weekly
- Backup database daily

## Troubleshooting

**Issue**: "No ANTHROPIC_API_KEY found"
- Solution: Add your API key to `.env` file

**Issue**: "Database connection failed"
- Solution: Check DATABASE_URL in `.env`

**Issue**: "Module not loading"
- Solution: Check `modules.{name}.enabled` in config

For more help, see the full documentation or contact support.
