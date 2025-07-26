# 🤖 AI Email Categorization Setup Guide

## Overview
Your email system now includes AI-powered categorization that automatically classifies emails into:
- **✅ Interested** - Shows interest in product/service
- **📅 Meeting Booked** - Contains meeting invites or scheduled calls  
- **❌ Not Interested** - Explicitly declines or says no
- **🚫 Spam** - Promotional content or suspicious offers
- **🏖️ Out of Office** - Automatic replies indicating absence

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd /home/vikas/Desktop/onebox\(1\)
pip install openai==0.28.1
```

### 2. Add Your OpenAI API Key
```bash
# Add to your .env file or export directly
export OPENAI_API_KEY="your-openai-api-key-here"

# Or add to your config.py file:
echo 'OPENAI_API_KEY="your-api-key-here"' >> config.py
```

### 3. Update Elasticsearch Mapping
```bash
python update_elasticsearch_mapping.py
```

### 4. Classify Existing Emails (Optional)
```bash
# This will classify all existing emails in your database
python classify_existing_emails.py

# To see statistics only:
python classify_existing_emails.py stats
```

### 5. Start the Enhanced Sync Service
```bash
# Your existing sync service now includes AI classification
python email_sync_service.py
```

## 🎯 How It Works

### Smart Classification Pipeline
1. **Rule-Based Pre-filtering** (Fast & Free)
   - Detects obvious patterns (out of office, spam keywords)
   - ~95% confidence for clear cases
   - No API costs for these emails

2. **AI Classification** (Accurate)
   - Uses OpenAI GPT-3.5-turbo for complex cases
   - Analyzes email content, tone, and intent
   - ~85% confidence for AI-classified emails

### Real-Time Classification
- **New emails** are automatically classified as they arrive
- **Background processing** doesn't slow down email sync
- **Fallback handling** ensures system works even if AI fails

## 💰 Cost Estimation

**OpenAI GPT-3.5-turbo Pricing:**
- ~$0.002 per email classification
- For 1,000 emails/month: ~$2/month
- Rule-based filtering reduces costs by 60-80%

**Example Monthly Costs:**
- 500 emails: ~$1/month
- 1,000 emails: ~$2/month  
- 5,000 emails: ~$10/month

## 🔧 Configuration Options

### email_classifier.py Features:
- **Batch Processing** - Classify multiple emails efficiently
- **Confidence Scoring** - Know how certain the AI is
- **Method Tracking** - See if email was classified by rules or AI
- **Error Handling** - Graceful fallbacks when AI is unavailable

### Web Dashboard Features:
- **Category Filtering** - Filter emails by classification
- **Visual Indicators** - Color-coded category badges
- **Confidence Display** - See AI confidence levels
- **Method Attribution** - Know if classified by rules or AI

## 📊 Monitoring & Analytics

### View Classification Statistics:
```bash
python classify_existing_emails.py stats
```

### Web Dashboard Analytics:
- Category breakdown with counts and percentages
- Classification method distribution
- Confidence score ranges

## 🛠️ Advanced Usage

### Custom Categories
Edit `email_classifier.py` to add your own categories:
```python
self.categories = [
    "Interested",
    "Meeting Booked", 
    "Not Interested",
    "Spam",
    "Out of Office",
    "Support Request",  # Your custom category
    "Invoice"           # Another custom category
]
```

### Adjust Classification Rules
Modify the `rule_based_classify()` function to add your own rules:
```python
# Custom rule example
if 'urgent' in subject.lower():
    return "High Priority"
```

### Batch Reclassification
```bash
# Reclassify all emails (useful after rule changes)
python classify_existing_emails.py
```

## 🔍 Testing the System

### 1. Test Individual Email:
```python
from email_classifier import classify_single_email

test_email = {
    "subject": "Meeting invitation - Project Discussion",
    "sender": "john@company.com", 
    "content": "Let's schedule a meeting to discuss the project."
}

result = classify_single_email(test_email)
print(result)
```

### 2. Check Web Dashboard:
- Visit http://localhost:4000
- Use the new "Category" filter dropdown
- See classification badges on emails

### 3. Monitor Logs:
```bash
# Watch classification in real-time
tail -f email_sync_service.log
```

## 🎉 Success Indicators

✅ **Setup Complete When:**
- New emails show category badges in web dashboard
- Category filter dropdown is populated
- Classification logs appear during email sync
- Statistics show classified emails

✅ **Working Correctly When:**
- Out of office emails are automatically detected
- Spam emails are caught by rules
- Meeting invites are properly categorized
- Interested/not interested emails are accurately classified

## 🚨 Troubleshooting

### Common Issues:

**1. "OPENAI_API_KEY not found"**
```bash
# Set the API key in your environment
export OPENAI_API_KEY="your-key-here"
# Or add to .bashrc for persistence
```

**2. "No category field in emails"**
```bash
# Update Elasticsearch mapping first
python update_elasticsearch_mapping.py
```

**3. "All emails show 'Uncategorized'"**
```bash
# Check if OpenAI API key is working
python -c "from email_classifier import classifier; print(classifier.ai_enabled)"
```

**4. "Categories not showing in web dashboard"**
```bash
# Restart the web server
# Categories are loaded at startup
```

## 📈 Next Steps

1. **Monitor Performance** - Watch classification accuracy over time
2. **Fine-tune Rules** - Add custom rules for your specific email patterns  
3. **Train Custom Model** - Use your classified data to train a custom model
4. **Automate Actions** - Set up automatic responses based on categories
5. **Analytics Dashboard** - Build detailed reports on email patterns

## 💡 Pro Tips

- **Start with existing emails** - Run batch classification first to see patterns
- **Monitor API usage** - OpenAI provides usage dashboards
- **Adjust confidence thresholds** - Fine-tune when to use AI vs rules
- **Regular reviews** - Manually check some classifications to improve rules
- **Backup classifications** - Export category data before major changes

Your AI email categorization system is now ready! 🚀
