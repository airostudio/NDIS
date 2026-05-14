## Cheryl Deployment Guide

This guide covers deploying Cheryl in a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Nginx (for reverse proxy)
- SSL certificate
- Domain name

## Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip postgresql redis-server nginx

# Create cheryl user
sudo useradd -m -s /bin/bash cheryl
sudo usermod -aG sudo cheryl
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE cheryl_production;
CREATE USER cheryl_user WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE cheryl_production TO cheryl_user;
\q
```

### 3. Application Deployment

```bash
# Switch to cheryl user
sudo su - cheryl

# Clone repository
git clone <your-repo-url> /home/cheryl/cheryl
cd /home/cheryl/cheryl

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values
```

### 4. Environment Configuration

Production `.env` file:

```env
# AI Configuration
ANTHROPIC_API_KEY=your_production_api_key

# Database
DATABASE_URL=postgresql://cheryl_user:secure_password@localhost/cheryl_production

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=generate_random_secure_key_here
ENCRYPTION_KEY=generate_random_encryption_key_here

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=cheryl@yourcompany.com.au

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+61400000000

# Company Details
COMPANY_NAME=Your NDIS Company Pty Ltd
COMPANY_ABN=12345678901
TIMEZONE=Australia/Sydney

# SCHADS Rates (Update annually!)
SCHADS_LEVEL_2_1_RATE=28.45
SUPERANNUATION_RATE=11.5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=your_sentry_dsn

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 5. Initialize Database

```bash
python scripts/init_db.py
```

### 6. Systemd Service

Create `/etc/systemd/system/cheryl.service`:

```ini
[Unit]
Description=Cheryl NDIS AI Assistant
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=cheryl
Group=cheryl
WorkingDirectory=/home/cheryl/cheryl
Environment="PATH=/home/cheryl/cheryl/venv/bin"
ExecStart=/home/cheryl/cheryl/venv/bin/python scripts/run_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cheryl
sudo systemctl start cheryl
sudo systemctl status cheryl
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/cheryl`:

```nginx
server {
    listen 80;
    server_name cheryl.yourcompany.com.au;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cheryl.yourcompany.com.au;

    ssl_certificate /etc/letsencrypt/live/cheryl.yourcompany.com.au/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cheryl.yourcompany.com.au/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/cheryl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d cheryl.yourcompany.com.au
```

## Security Hardening

### 1. Firewall

```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 2. Fail2Ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Database Security

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Change to:
# local   all   all   md5
# host    all   all   127.0.0.1/32   md5

sudo systemctl restart postgresql
```

## Monitoring

### 1. Application Logs

```bash
# View Cheryl logs
sudo journalctl -u cheryl -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. System Monitoring

Consider setting up:
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics
- **Uptime monitoring** (e.g., UptimeRobot)

## Backup Strategy

### Database Backup

Create `/home/cheryl/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/cheryl/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump cheryl_production > "$BACKUP_DIR/cheryl_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/cheryl_$DATE.sql"

# Delete backups older than 30 days
find $BACKUP_DIR -name "cheryl_*.sql.gz" -mtime +30 -delete
```

Add to crontab:

```bash
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/cheryl/backup.sh
```

## Updates and Maintenance

### Application Updates

```bash
cd /home/cheryl/cheryl
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cheryl
```

### Database Migrations

When schema changes occur:

```bash
# Backup first!
/home/cheryl/backup.sh

# Run migrations
python scripts/migrate_db.py
```

## Scaling

### Horizontal Scaling

For high traffic:

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple Workers**: Run multiple Cheryl instances
3. **Redis Session Store**: Share sessions across instances
4. **Database Replication**: PostgreSQL read replicas

### Vertical Scaling

Recommended specs by usage:

**Small (< 50 employees):**
- 2 CPU cores
- 4 GB RAM
- 20 GB SSD

**Medium (50-200 employees):**
- 4 CPU cores
- 8 GB RAM
- 50 GB SSD

**Large (200+ employees):**
- 8 CPU cores
- 16 GB RAM
- 100 GB SSD

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u cheryl -n 50 --no-pager
```

**Database connection issues:**
```bash
sudo -u postgres psql -c "SELECT 1"
```

**High memory usage:**
```bash
sudo systemctl restart cheryl
```

## Compliance Considerations

For NDIS compliance:

1. **Data Encryption**: All sensitive data must be encrypted at rest
2. **Access Logs**: Maintain audit logs for 7 years
3. **Backup**: Daily backups with offsite storage
4. **Disaster Recovery**: Test recovery procedures quarterly
5. **Security Updates**: Apply security patches within 7 days

## Support

For production support:
- Check documentation
- Review logs
- Contact your system administrator
- Engage professional support if needed
