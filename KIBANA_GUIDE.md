# 📊 Kibana Email Dashboard Setup Guide

## 🚀 Quick Start
1. **Welcome Screen**: Click "Explore on my own"
2. **Create Index Pattern**:
   - Go to: Management → Stack Management → Index Patterns
   - Index pattern: `emails*`
   - Time field: `date_synced`
3. **View Data**: Analytics → Discover

## 📈 Your Email Data Fields
- `account_email`: Which email account (vikastg2000@gmail.com, vikastg2020@gmail.com)
- `subject`: Email subject line
- `sender`: Who sent the email
- `date_received`: When the email was received
- `date_synced`: When we stored it in Elasticsearch
- `uid`: Unique email ID

## 🔍 Cool Things You Can Do
- **Filter by account**: `account_email: "vikastg2000@gmail.com"`
- **Search subjects**: `subject: "Google"`
- **Time range**: Last 7 days, 30 days, etc.
- **Create visualizations**: Pie charts, bar graphs, etc.

## 📊 Sample Searches
- `sender: "*google*"` - All Google emails
- `subject: "job"` - All job-related emails
- `account_email: "vikastg2020@gmail.com" AND subject: "training"` - Training emails from specific account

## 🎯 Direct URLs
- **Dashboard**: http://localhost:4000 (Simple web interface)
- **Kibana**: http://localhost:5601 (Advanced analytics)
- **Elasticsearch**: http://localhost:9200 (Raw API)
