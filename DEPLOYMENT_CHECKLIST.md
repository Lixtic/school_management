# Production Deployment Checklist

**Date Created**: October 21, 2025  
**Version**: 1.0  
**Status**: Ready for deployment

---

## ✅ Pre-Deployment Validation

### Code Quality
- [ ] All tests passing: `python manage.py test`
- [ ] No Django warnings: `python manage.py check --deploy`
- [ ] No linting errors
- [ ] All secrets removed from code
- [ ] No debug print statements
- [ ] Documentation complete

### Security Review
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` set via environment variable
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] CSRF/session cookies set to secure
- [ ] SSL certificate obtained
- [ ] Database credentials in environment variables
- [ ] Email credentials in environment variables

### Database Readiness
- [ ] PostgreSQL database created
- [ ] Migrations tested on production schema
- [ ] Database backups configured
- [ ] Connection pooling tested (conn_max_age=600)
- [ ] Database user has minimal required permissions

### Infrastructure Setup
- [ ] Application server ready (Gunicorn)
- [ ] Web server configured (Nginx)
- [ ] Redis cache cluster ready
- [ ] SMTP email service configured
- [ ] Log rotation configured
- [ ] Monitoring/alerting configured

---

## 🚀 Deployment Steps

### Step 1: Prepare Environment

```bash
# SSH into production server
ssh user@server.com

# Create deployment directory
mkdir -p /var/www/school-management
cd /var/www/school-management

# Clone repository
git clone <repo-url> .
git checkout asetena_systems

# Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify installation
python manage.py check --deploy
```

### Step 3: Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
DEBUG=false
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DATABASE_URL=postgresql://user:password@host:5432/school_db
REDIS_URL=redis://:password@redis-host:6379/1
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@school.edu
EMAIL_HOST_PASSWORD=your-app-password
ALLOWED_HOSTS=school.edu,www.school.edu
EOF

# Set permissions
chmod 600 .env

# Load environment
export $(cat .env | xargs)
```

### Step 4: Database Setup

```bash
# Run migrations
python manage.py migrate --noinput

# Create superuser (for admin access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Verify database
python manage.py check --deploy
```

### Step 5: Configure Gunicorn

```bash
# Create Gunicorn config
cat > gunicorn_config.py << 'EOF'
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
EOF

# Test Gunicorn
gunicorn --config gunicorn_config.py school_system.wsgi
```

### Step 6: Configure Nginx

```nginx
# /etc/nginx/sites-available/school-management
upstream school_management {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name school.edu www.school.edu;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name school.edu www.school.edu;
    
    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/school.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/school.edu/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client upload size
    client_max_body_size 10M;
    
    # Proxy settings
    location / {
        proxy_pass http://school_management;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/school-management/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/school-management/media/;
        expires 7d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/school-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d school.edu -d www.school.edu

# Auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 8: Systemd Service

```bash
# Create systemd service file
sudo cat > /etc/systemd/system/school-management.service << 'EOF'
[Unit]
Description=School Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/school-management
ExecStart=/var/www/school-management/venv/bin/gunicorn \
    --config gunicorn_config.py \
    school_system.wsgi

Environment="PATH=/var/www/school-management/venv/bin"
EnvironmentFile=/var/www/school-management/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable school-management
sudo systemctl start school-management
sudo systemctl status school-management
```

### Step 9: Configure Redis

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: requirepass your-strong-password
# Set: maxmemory 2gb
# Set: maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Step 10: Setup Logging

```bash
# Create log directory
sudo mkdir -p /var/log/school-management
sudo chown www-data:www-data /var/log/school-management

# Create logs directory in app
mkdir -p logs
sudo chown www-data:www-data logs

# Configure logrotate
sudo cat > /etc/logrotate.d/school-management << 'EOF'
/var/log/school-management/*.log
/var/www/school-management/logs/*.log
{
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload school-management > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## 🧪 Post-Deployment Validation

### Verify Application

```bash
# Check application is running
curl http://127.0.0.1:8000/

# Check Django checks
python manage.py check --deploy

# Test database
python manage.py dbshell
\dt  # PostgreSQL: list tables
```

### Verify HTTPS

```bash
# Test SSL
curl -I https://school.edu

# Should show:
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
```

### Test Application Features

```bash
# Check login page
curl https://school.edu/

# Test admin login
curl -c cookies.txt https://school.edu/admin/
curl -b cookies.txt -X POST https://school.edu/admin/login/

# Check static files loading
curl https://school.edu/static/css/loader.css
```

### Monitor Logs

```bash
# Watch application logs
tail -f /var/log/school-management/error.log
tail -f /var/log/school-management/access.log

# Watch Django logs
tail -f logs/django.log
tail -f logs/security.log

# Watch Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔄 Rollback Procedure

If deployment fails, follow these steps:

```bash
# 1. Stop the service
sudo systemctl stop school-management

# 2. Revert code to previous version
git checkout HEAD~1

# 3. Run migrations if needed
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start service
sudo systemctl start school-management

# 6. Verify
curl https://school.edu/
```

---

## 📊 Monitoring Setup

### Application Health Check

Create a monitoring endpoint:

```python
# school_system/urls.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Test database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

# Add to urlpatterns
path('health/', health_check, name='health_check'),
```

### Uptime Monitoring

```bash
# Using cron to monitor
# Every 5 minutes, check if app is running
*/5 * * * * curl -f https://school.edu/health/ || systemctl restart school-management
```

---

## 🔐 Security Hardening Checklist

- [ ] Firewall configured (ufw)
- [ ] SSH key-based authentication only
- [ ] Regular security updates applied
- [ ] Database backups encrypted and stored offsite
- [ ] API rate limiting configured
- [ ] DDoS protection enabled
- [ ] Web Application Firewall (WAF) configured
- [ ] Intrusion detection system (IDS) running
- [ ] Security headers validated
- [ ] SSL/TLS version enforced (1.2+)

---

## 🔄 Regular Maintenance

### Daily
- [ ] Check application logs for errors
- [ ] Monitor server resources (CPU, RAM, disk)
- [ ] Verify database backups completed

### Weekly
- [ ] Review security logs
- [ ] Check for available updates
- [ ] Test backup restoration

### Monthly
- [ ] Full security audit
- [ ] Performance review
- [ ] Update documentation
- [ ] Test disaster recovery plan

---

## 📞 Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| DevOps Lead | +1-XXX-XXX-XXXX | 24/7 |
| Database Admin | +1-XXX-XXX-XXXX | 24/7 |
| Security Officer | +1-XXX-XXX-XXXX | Business hours |

---

## 🚨 Incident Response

### Application Down

1. Check service status: `sudo systemctl status school-management`
2. Check logs: `tail -f logs/django.log`
3. Restart service: `sudo systemctl restart school-management`
4. If still down, rollback: See "Rollback Procedure"
5. Alert team members

### Database Down

1. Check Redis: `redis-cli ping`
2. Check PostgreSQL: `psql -U postgres`
3. Check connections: `systemctl status postgresql`
4. Verify backups exist
5. Restore from backup if needed

### High CPU/Memory

1. Identify process: `top` or `htop`
2. Check logs for errors
3. Kill problematic process if needed
4. Review code for memory leaks
5. Restart service if necessary

---

## 📋 Sign-Off

- [ ] All checklist items completed
- [ ] Application tested and working
- [ ] Backups verified
- [ ] Monitoring configured
- [ ] Team trained on procedures
- [ ] Deployment complete

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Verified By**: ___________  

---

## 📚 Related Documentation

- [Settings Refactor Guide](SETTINGS_REFACTOR.md)
- [Session Completion Report](SESSION_COMPLETE.md)
- [Developer Quick Reference](DEVELOPER_QUICK_REF.md)
- [Django Deployment Docs](https://docs.djangoproject.com/en/5.0/howto/deployment/)

---

**Version**: 1.0  
**Last Updated**: Oct 21, 2025  
**Status**: Ready for production deployment
