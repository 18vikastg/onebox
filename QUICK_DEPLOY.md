# 🚀 Quick Deployment Guide

## Option 1: Railway (Recommended for Beginners)

### Why Railway?
- ✅ One-click deployment
- ✅ Free $5/month credit
- ✅ Built-in databases
- ✅ Auto HTTPS
- ✅ Environment variable management

### Steps:
1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy with Template**: Use our Railway template
4. **Add Environment Variables**: Copy from `.env.example`
5. **Deploy**: One-click deployment

### Railway Template Button:
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/...)

---

## Option 2: Render (Free Tier Available)

### Why Render?
- ✅ Free tier (750 hours/month)
- ✅ Auto-deployments from Git
- ✅ Built-in SSL
- ✅ Easy scaling

### Steps:
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **New Web Service**: Connect your GitHub repo
3. **Configure Build Settings**:
   - Build Command: `npm install`
   - Start Command: `npm start`
4. **Add Environment Variables** from `.env.example`
5. **Deploy**

---

## Option 3: DigitalOcean App Platform

### Why DigitalOcean?
- ✅ $200 free credit for new users
- ✅ Managed platform
- ✅ Auto-scaling
- ✅ Multiple regions

### Steps:
1. **Create DO Account**: Get $200 credit at [digitalocean.com](https://digitalocean.com)
2. **App Platform**: Create new app from GitHub
3. **Configure Components**:
   - Web Service (Node.js)
   - Worker Service (Python)
   - Managed Database (PostgreSQL as Elasticsearch alternative)
4. **Deploy**

---

## Option 4: VPS Deployment (Most Control)

### Recommended VPS Providers:
- **DigitalOcean**: $6/month Droplet
- **Linode**: $5/month VPS
- **Vultr**: $5/month instance
- **AWS EC2**: t3.micro (free tier)

### Quick VPS Setup:
```bash
# 1. Create server (Ubuntu 22.04)
# 2. SSH into server
ssh root@your-server-ip

# 3. Run auto-setup script
curl -sSL https://your-domain.com/setup.sh | bash

# 4. Clone your repo
git clone https://github.com/your-username/reachinbox.git
cd reachinbox

# 5. Configure environment
cp .env.example .env
nano .env  # Add your credentials

# 6. Deploy
./deploy.sh
```

---

## Option 5: Docker Deployment (Any Platform)

### Prerequisites:
- Docker & Docker Compose installed
- `.env` file configured

### Deploy:
```bash
# Clone repository
git clone <your-repo>
cd reachinbox

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Deploy with Docker
./deploy.sh
```

### Access:
- **Application**: http://your-domain
- **Kibana**: http://your-domain:5601

---

## 🔧 Environment Variables Setup

Copy these into your hosting platform's environment variables:

```bash
# Essential Variables (Required)
GMAIL_PRIMARY_EMAIL=your-email@gmail.com
GMAIL_PRIMARY_PASSWORD=your-app-password
OPENAI_API_KEY=sk-proj-your-key-here

# Optional Variables
GMAIL_SECONDARY_EMAIL=second@gmail.com
GMAIL_SECONDARY_PASSWORD=second-app-password
NODE_ENV=production
PORT=4000
```

---

## 🌐 Domain Setup

### 1. **Custom Domain**:
- Buy domain from Namecheap, GoDaddy, etc.
- Point DNS to your hosting platform
- Enable SSL/HTTPS

### 2. **Subdomain Options**:
- `app.yourdomain.com` - Main application
- `kibana.yourdomain.com` - Analytics dashboard
- `api.yourdomain.com` - API endpoints

---

## 🔒 Security Checklist

### Production Security:
- ✅ Use environment variables for secrets
- ✅ Enable HTTPS/SSL
- ✅ Set up firewall rules
- ✅ Use strong passwords
- ✅ Enable 2FA on email accounts
- ✅ Regular security updates

### Gmail Security:
1. Enable 2-Factor Authentication
2. Generate App Passwords (not regular password)
3. Use dedicated Gmail accounts for the app
4. Monitor for suspicious activity

---

## 📊 Monitoring & Maintenance

### Health Checks:
- Application: `http://your-domain/health`
- Elasticsearch: `http://your-domain:9200/_cluster/health`

### Log Monitoring:
```bash
# Docker logs
docker-compose logs -f

# PM2 logs (VPS)
pm2 logs

# Application metrics
curl http://your-domain/api/stats
```

---

## 🚀 Quick Start (Choose One)

### For Beginners: Railway
1. Fork this repository
2. Sign up at railway.app
3. Deploy from GitHub
4. Add environment variables
5. Done! ✨

### For Developers: VPS
1. Get a $5 VPS from DigitalOcean
2. SSH into server
3. Run our setup script
4. Configure .env file
5. Execute ./deploy.sh

### For Docker Users: Any Platform
1. Install Docker & Docker Compose
2. Clone repository
3. Configure .env file
4. Run ./deploy.sh
5. Access at http://localhost

---

## 🆘 Troubleshooting

### Common Issues:
1. **Email sync not working**: Check Gmail app passwords
2. **Elasticsearch errors**: Increase memory allocation
3. **OpenAI errors**: Add billing to OpenAI account
4. **Port conflicts**: Change PORT in .env

### Get Help:
- 📧 Email: support@your-domain.com
- 🐛 Issues: GitHub Issues tab
- 💬 Discord: Join our server
- 📖 Docs: Full documentation link

---

**Choose your preferred deployment method and get started! 🚀**
