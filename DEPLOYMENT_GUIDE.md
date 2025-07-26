# 🚀 ReachInbox Full-Stack Deployment Guide

This guide covers multiple hosting options for your ReachInbox email management application.

## 📋 Pre-Deployment Checklist

### 1. **Environment Variables Setup**
Create a `.env` file for sensitive data:

```bash
# Gmail Credentials
GMAIL_PRIMARY_EMAIL=your-email@gmail.com
GMAIL_PRIMARY_PASSWORD=your-app-password
GMAIL_SECONDARY_EMAIL=your-secondary@gmail.com  
GMAIL_SECONDARY_PASSWORD=your-secondary-app-password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Application Configuration
NODE_ENV=production
PORT=4000
```

### 2. **Update Configuration Files**
- Remove hardcoded credentials from `config.py`
- Use environment variables instead
- Secure sensitive information

---

## 🏠 Option 1: VPS/Cloud Server Deployment (Recommended)

### **Platforms**: DigitalOcean, AWS EC2, Google Cloud, Linode

### **Step 1: Server Setup**
```bash
# Ubuntu 22.04 LTS recommended
sudo apt update && sudo apt upgrade -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.11+
sudo apt install python3 python3-pip python3-venv -y

# Install Docker & Docker Compose
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
```

### **Step 2: Application Deployment**
```bash
# Clone your application
git clone <your-repo-url>
cd reachinbox-app

# Install Node.js dependencies
npm install

# Setup Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install additional Python packages
pip install elasticsearch==8.15.1 chromadb sentence-transformers

# Setup environment variables
cp .env.example .env
nano .env  # Edit with your credentials
```

### **Step 3: Docker Services**
```bash
# Start Elasticsearch & Kibana
docker-compose up -d

# Verify services
docker ps
curl http://localhost:9200
```

### **Step 4: Process Management with PM2**
```bash
# Install PM2
sudo npm install -g pm2

# Create ecosystem file
```

### **Step 5: Nginx Reverse Proxy**
```bash
# Install Nginx
sudo apt install nginx -y

# Configure Nginx (see nginx.conf below)
sudo nano /etc/nginx/sites-available/reachinbox
sudo ln -s /etc/nginx/sites-available/reachinbox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## ☁️ Option 2: Docker-based Deployment

### **Complete Docker Setup**
See `docker-compose.production.yml` below for full stack deployment.

---

## 🌐 Option 3: Railway Deployment (Easiest)

### **Why Railway?**
- Easy deployment with GitHub integration
- Built-in database services
- Automatic HTTPS
- Environment variable management

### **Steps:**
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables
4. Deploy with one click

---

## 🔧 Option 4: Render Deployment

### **Why Render?**
- Free tier available
- Automatic deployments
- Built-in PostgreSQL/Redis
- Easy environment management

### **Steps:**
1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Configure build & start commands
4. Add environment variables

---

## 📊 Option 5: AWS/GCP Full Stack

### **AWS Services Needed:**
- **EC2**: Application server
- **RDS**: PostgreSQL database (alternative to Elasticsearch)
- **ElastiCache**: Redis for caching
- **S3**: File storage
- **CloudFront**: CDN
- **Route 53**: Domain management

### **GCP Services Needed:**
- **Compute Engine**: Application server
- **Cloud SQL**: PostgreSQL database
- **Memorystore**: Redis
- **Cloud Storage**: File storage
- **Cloud CDN**: Content delivery

---

## 🔒 Security Considerations

### **1. Environment Variables**
- Never commit API keys to Git
- Use `.env` files for local development
- Use platform environment variables for production

### **2. Network Security**
- Configure firewall rules
- Use HTTPS/SSL certificates
- Restrict Elasticsearch access
- Implement rate limiting

### **3. Email Security**
- Use Gmail App Passwords
- Enable 2FA on all accounts
- Monitor for suspicious activity

---

## 📈 Monitoring & Maintenance

### **1. Application Monitoring**
- Use PM2 for process monitoring
- Set up log rotation
- Monitor resource usage

### **2. Database Monitoring**
- Monitor Elasticsearch cluster health
- Set up automated backups
- Monitor disk space usage

### **3. Error Tracking**
- Implement error logging
- Set up alerts for critical errors
- Monitor API response times

---

## 🚀 Quick Start Commands

### **Local Development**
```bash
npm run dev                    # Start both Node.js and Python services
```

### **Production Start**
```bash
pm2 start ecosystem.config.js # Start with PM2
```

### **Docker Production**
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

Choose the deployment option that best fits your needs and budget. For beginners, I recommend starting with Railway or Render for ease of use.
