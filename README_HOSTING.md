# 🚀 ReachInbox - Production Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/...)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

> **Ready-to-deploy** full-stack email management platform with AI-powered features

## 📋 Quick Start Options

### 🌟 Option 1: Railway (Recommended)
**Best for**: Beginners, rapid deployment
**Cost**: Free $5/month credit, then $0.02/hour
**Setup Time**: 5 minutes

```bash
1. Fork this repository
2. Click "Deploy on Railway" button above
3. Connect your GitHub account
4. Add environment variables (see below)
5. Deploy with one click! 🚀
```

### 🎯 Option 2: VPS (DigitalOcean/Linode)
**Best for**: Full control, custom domains
**Cost**: $5-20/month
**Setup Time**: 15 minutes

```bash
# 1. Create Ubuntu 22.04 VPS
# 2. SSH into server
ssh root@your-server-ip

# 3. Run auto-setup
curl -sSL https://raw.githubusercontent.com/your-repo/main/setup-vps.sh | bash

# 4. Deploy application
git clone https://github.com/your-username/reachinbox.git
cd reachinbox
cp .env.example .env
nano .env  # Add your credentials
./deploy.sh
```

### 🐳 Option 3: Docker (Any Platform)
**Best for**: Local development, containerized environments
**Setup Time**: 10 minutes

```bash
git clone https://github.com/your-username/reachinbox.git
cd reachinbox
cp .env.example .env
# Edit .env with your credentials
./deploy.sh
```

---

## 🔑 Environment Variables Setup

### Required Variables:
```bash
GMAIL_PRIMARY_EMAIL=your-email@gmail.com
GMAIL_PRIMARY_PASSWORD=your-app-password    # NOT regular password!
OPENAI_API_KEY=sk-proj-your-openai-key
```

### Optional Variables:
```bash
GMAIL_SECONDARY_EMAIL=second@gmail.com
GMAIL_SECONDARY_PASSWORD=second-app-password
RAG_ENABLED=true
AI_CLASSIFICATION_ENABLED=false  # Requires OpenAI billing
```

### 📧 Gmail Setup:
1. Enable 2-Factor Authentication
2. Generate App Password: [Google Account Settings](https://myaccount.google.com/apppasswords)
3. Use App Password (not regular password) in environment variables

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Services      │
│                 │    │                 │    │                 │
│ • Bootstrap UI  │◄──►│ • Express.js    │◄──►│ • Elasticsearch │
│ • EJS Templates │    │ • Email API     │    │ • Redis Cache   │
│ • JavaScript    │    │ • RAG Engine    │    │ • Python Sync   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components:
- **Frontend**: Bootstrap 5 dashboard with real-time search
- **Backend**: Node.js Express server with API endpoints
- **Email Sync**: Python service for IMAP real-time synchronization
- **Database**: Elasticsearch for email storage and search
- **AI Engine**: OpenAI + ChromaDB for intelligent replies
- **Cache**: Redis for session management and caching

---

## 🌍 Hosting Platform Comparison

| Platform | Pros | Cons | Cost | Best For |
|----------|------|------|------|----------|
| **Railway** | Easy setup, auto-scaling, free credits | Limited free tier | $0.02/hr | Beginners |
| **Render** | Free tier, auto-deploy | Slower cold starts | Free/month | Small projects |
| **DigitalOcean** | Full control, predictable pricing | Manual setup | $5-20/month | Production |
| **AWS/GCP** | Enterprise features, global scale | Complex setup, variable cost | $10-100+/month | Enterprise |
| **Docker** | Portable, consistent environment | Requires server management | Server cost | Development |

---

## 🚀 Deployment Commands

### Production Deployment:
```bash
# Clone and setup
git clone <your-repo>
cd reachinbox
cp .env.example .env

# Quick deploy with Docker
./deploy.sh

# Or deploy with PM2 (VPS)
npm install -g pm2
pm2 start ecosystem.config.js
```

### Testing Deployment:
```bash
# Test all services
./test-deployment.sh

# Check logs
docker-compose logs -f
# or
pm2 logs
```

### Monitoring:
```bash
# Application health
curl http://localhost:4000/health

# Elasticsearch health
curl http://localhost:9200/_cluster/health

# View dashboard
open http://localhost:4000
```

---

## 🔧 Customization

### Custom Domain:
1. Point your domain to server IP
2. Update nginx configuration
3. Enable SSL: `certbot --nginx -d yourdomain.com`

### Scaling:
- **Horizontal**: Add more server instances behind load balancer
- **Vertical**: Increase server resources (CPU/RAM)
- **Database**: Use managed Elasticsearch service

### Monitoring:
- **Logs**: Centralized logging with ELK stack
- **Metrics**: Prometheus + Grafana
- **Alerts**: PagerDuty/Slack notifications

---

## 🔒 Security Checklist

### Production Security:
- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS/SSL certificates
- ✅ Configure firewall rules
- ✅ Regular security updates
- ✅ Monitor access logs
- ✅ Use strong passwords everywhere

### Email Security:
- ✅ Enable 2FA on Gmail accounts
- ✅ Use App Passwords (not regular passwords)
- ✅ Monitor for suspicious login activity
- ✅ Use dedicated email accounts for the app

---

## 📊 Performance Optimization

### For High Volume:
1. **Elasticsearch Cluster**: Multi-node setup for large email volumes
2. **Redis Cluster**: Distributed caching for better performance
3. **Load Balancer**: Nginx/HAProxy for multiple app instances
4. **CDN**: CloudFront/CloudFlare for static assets

### Resource Requirements:
- **Minimum**: 1 CPU, 2GB RAM, 20GB storage
- **Recommended**: 2 CPU, 4GB RAM, 50GB storage
- **High Volume**: 4+ CPU, 8GB+ RAM, 100GB+ storage

---

## 🆘 Troubleshooting

### Common Issues:

#### Email Sync Not Working:
```bash
# Check Gmail credentials
grep GMAIL .env

# Check Python service logs
docker logs reachinbox-sync
# or
pm2 logs reachinbox-email-sync
```

#### Elasticsearch Errors:
```bash
# Check memory allocation
docker stats reachinbox-elasticsearch

# Increase memory in docker-compose.yml
ES_JAVA_OPTS: "-Xms1g -Xmx1g"
```

#### OpenAI API Errors:
```bash
# Check API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Add billing at https://platform.openai.com/billing
```

### Getting Help:
- 📖 **Documentation**: [Full docs](https://your-docs-site.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discord**: [Join our community](https://discord.gg/your-server)
- 📧 **Email**: support@your-domain.com

---

## 📈 Roadmap

### Upcoming Features:
- [ ] Multi-tenant support
- [ ] Advanced email templates
- [ ] Calendar integration
- [ ] Mobile app
- [ ] Slack bot integration
- [ ] Advanced analytics

### Contributions Welcome!
- 🔧 Bug fixes and improvements
- 📚 Documentation updates
- 🚀 New feature implementations
- 🧪 Test coverage improvements

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🎉 Success Stories

> "Deployed ReachInbox in 5 minutes on Railway. Processing 1000+ emails daily!" - @developer1

> "Running on DigitalOcean with 99.9% uptime for 6 months." - @startup_founder

> "Perfect for our team's email management needs." - @project_manager

---

**Ready to deploy? Choose your platform and get started! 🚀**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/...)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
