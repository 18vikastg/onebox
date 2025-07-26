# 🚀 QUICK START GUIDE - AI Email Classification with Slack

## 📋 Step-by-Step Usage Instructions

### **1. Test Your Slack Connection**
```bash
# Test your Slack webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🧪 Test from AI Email System!"}' \
  https://hooks.slack.com/services/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
```
✅ **Check your Slack channel** - you should see the test message!

---

### **2. Run Complete System Tests**
```bash
# Activate Python environment
source .venv/bin/activate

# Test Slack integration
python test_slack_integration.py

# Test step-by-step guide
python USAGE_GUIDE.py
```

---

### **3. Start the Web Dashboard**
```bash
# Start the web server
node index.js

# Open in browser: http://localhost:4000
# View all classified emails with category filters
```

---

### **4. Classify Individual Emails**
```python
# Python code to classify emails
from email_classifier import classify_single_email

# Example: Interested email (will trigger Slack notification)
email = {
    'subject': 'Interested in your AI solution',
    'sender': 'customer@company.com',
    'content': 'Hi, I saw your demo and want to buy this product. Can you send pricing?'
}

result = classify_single_email(email)
print(f"Category: {result['category']}")
# If result is "Interested" → Automatic Slack notification sent!
```

---

### **5. Process Batch Emails**
```python
# Process multiple emails at once
from email_classifier import classify_emails_batch

emails = [email1, email2, email3, ...]  # Your email list
results = classify_emails_batch(emails)
# All "Interested" emails → Slack notifications sent automatically!
```

---

### **6. Monitor Your System**

#### **Slack Notifications** 📱
- **When**: Only for emails classified as "Interested"
- **Format**: Rich message with subject, sender, confidence, preview
- **Channel**: Your configured Slack channel
- **Automatic**: No manual intervention needed

#### **Web Dashboard** 🌐
- **URL**: http://localhost:4000
- **Features**: View all emails, filter by category, search functionality
- **Real-time**: Updates as new emails are processed

#### **Logs** 📊
- **Classification stats**: Success rates, processing times
- **Notification status**: Slack delivery confirmations
- **Error handling**: Detailed error logs for troubleshooting

---

### **7. Production Usage Examples**

#### **Example A: Real-time Email Processing**
```python
# Process new emails as they arrive
for new_email in incoming_emails:
    result = classify_single_email(new_email)
    if result['category'] == 'Interested':
        print("🎯 New lead detected! Slack notification sent!")
```

#### **Example B: Bulk Email Analysis**
```python
# Analyze existing email database
all_emails = get_emails_from_database()  # Your email source
classified = classify_emails_batch(all_emails)

interested_count = sum(1 for email in classified if email['category'] == 'Interested')
print(f"Found {interested_count} interested leads!")
```

#### **Example C: Custom Webhook Integration**
```python
# Send to custom webhook (optional)
from notification_service import notify_interested_email

# This automatically sends to both Slack AND custom webhook
notify_interested_email(email_data, webhook_url="https://your-custom-webhook.com")
```

---

### **8. Key Features Working** ✅

| Feature | Status | Description |
|---------|--------|-------------|
| **AI Classification** | ✅ Working | 5 categories: Interested, Meeting Booked, Not Interested, Spam, Out of Office |
| **Slack Notifications** | ✅ Working | Rich messages only for "Interested" emails |
| **Web Dashboard** | ✅ Working | View and filter classified emails |
| **Batch Processing** | ✅ Working | Handle hundreds of emails efficiently |
| **Error Handling** | ✅ Working | Graceful failures with detailed logging |
| **Real-time Processing** | ✅ Working | Instant classification and notifications |

---

### **9. Your Slack Webhook Details** 🔗

**Webhook URL**: 
```
https://hooks.slack.com/services/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
```

**Manual Test Command**:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Hello from AI Email System!"}' \
  https://hooks.slack.com/services/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
```

**Rich Notification Format**:
```
🎯 New Interested Lead!

Subject: [Email Subject]
From: [Sender Email]  
Confidence: 92.5%
Detected: 2025-07-24 20:30:15

Email Preview:
Hi, I'm very interested in your solution...

[View in Dashboard] [Mark as Follow-up]
```

---

### **10. Next Steps** 🚀

1. **✅ Test Slack connection** (run the curl command above)
2. **✅ Run system tests** (python test_slack_integration.py)  
3. **✅ Start web dashboard** (node index.js)
4. **✅ Process your emails** (use the Python examples)
5. **✅ Monitor Slack channel** for lead notifications!

---

## 🎉 YOU'RE ALL SET!

Your AI Email Classification System with Slack integration is **production-ready**! 

You'll now automatically get Slack notifications whenever a potential interested customer emails you. Never miss a lead again! 🎯

---

*Need help? Check the logs or run `python USAGE_GUIDE.py` for detailed diagnostics.*
