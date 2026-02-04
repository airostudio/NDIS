# Velma - NDIS Virtual AI Executive Suite

Velma is a comprehensive AI-powered virtual executive assistant designed specifically for NDIS (National Disability Insurance Scheme) companies. It combines executive assistant, receptionist, HR, and payroll functions into a single, intelligent 24/7 system.

## Features

### Executive Assistant Capabilities
- **Calendar & Time Management**: Schedule meetings, manage conflicts, send reminders
- **Communication Management**: Email filtering, correspondence drafting, inbox management
- **Task & Project Coordination**: Deadline tracking, to-do lists, team coordination
- **Administrative Support**: Document preparation, expense tracking, travel arrangements
- **Relationship Management**: Contact database, important dates, networking

### Receptionist Functions
- **Call Management**: Answer and route calls, screen priority, take messages
- **Visitor Management**: Check-in, badge visitors, maintain logs
- **Appointment Coordination**: Schedule, confirm, manage cancellations
- **Information Hub**: FAQ handling, directions, resource guidance
- **Facility Management**: Conference room booking, office resources

### NDIS-Specific HR & Compliance
- **Worker Screening**: NDIS Worker Screening Checks, WWCC, First Aid, CPR, Police Checks
- **Onboarding**: NDIS Worker Orientation Module tracking
- **Contract Management**: Employment type management, SCHADS classification
- **Performance & Safety**: Incident reports, performance reviews
- **Policy Governance**: Staff handbook, NDIS Code of Conduct, WHS compliance

### NDIS Payroll with SCHADS Award
- **Complex Payroll Calculations**: Shift penalties, allowances, broken shifts
- **Award Interpretation**: Automatic SCHADS Award compliance
- **STP & Superannuation**: Single Touch Payroll Phase 2, Superannuation Guarantee
- **Leave Management**: Annual leave, sick leave, leave loading (17.5%)
- **Audit Readiness**: Complete record linking for NDIS Commission audits

### AI Core Capabilities
- 24/7 Availability
- Multi-channel Support (Phone, Chat, Email, SMS)
- Intelligent Routing & Escalation
- Context Awareness & Memory
- Proactive Assistance
- Security & Privacy Compliance

## System Architecture

```
velma/
├── core/               # Core AI engine and orchestration
├── modules/            # Function-specific modules
│   ├── calendar/       # Calendar and time management
│   ├── communication/  # Email and correspondence
│   ├── receptionist/   # Call and visitor management
│   ├── hr/             # NDIS HR and compliance
│   ├── payroll/        # SCHADS Award payroll
│   ├── tasks/          # Task and project coordination
│   └── relationships/  # Contact and relationship management
├── integrations/       # External system integrations
├── interfaces/         # Multi-channel interfaces
├── database/           # Database models and migrations
├── api/                # REST API endpoints
└── utils/              # Shared utilities
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd NDIS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init_db.py

# Run Velma
python main.py
```

### Configuration

Edit `config/velma_config.yaml` to customize:
- AI model settings
- Integration credentials
- Business rules
- SCHADS Award rates
- Notification preferences

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Module Documentation](docs/modules/)
- [API Reference](docs/api.md)
- [NDIS Compliance Guide](docs/ndis_compliance.md)
- [Integration Guide](docs/integrations.md)

## Security & Privacy

Velma is designed with security and privacy at its core:
- End-to-end encryption for sensitive data
- Role-based access control (RBAC)
- Audit logging for all operations
- NDIS Quality and Safeguards Commission compliance
- GDPR and Australian Privacy Principles compliance

## Support

For issues, questions, or feature requests, please contact [your support details]

## License

[Your License]

## Version

Current Version: 1.0.0
Last Updated: February 2026
