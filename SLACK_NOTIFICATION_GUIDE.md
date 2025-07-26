# 📱 SLACK NOTIFICATION GUIDE - What You'll Get

## 🎯 **SLACK NOTIFICATIONS BY EMAIL TYPE**

### **📱 EMAILS THAT TRIGGER SLACK NOTIFICATIONS:**

#### ✅ **"INTERESTED" EMAILS** → **SLACK NOTIFICATION SENT**
**Examples:**
- "Thank you for the demo! I'm very interested..."
- "Can you send me pricing information?"
- "I want to buy your product"
- "Very interested in your solution"
- "Let's schedule a call to discuss"

**Slack Notification Format:**
```
🎯 NEW INTERESTED LEAD DETECTED!

🔥 HIGH-PRIORITY LEAD ALERT
A potential customer has expressed strong interest in your services!

📧 Subject: [Email Subject]
👤 From: [Customer Email]
🎯 Confidence: XX.X%
⏰ Detected: 2025-07-24 21:00:15

📄 Email Preview:
[First 300 characters of the email...]

[🎯 View Lead in Dashboard] [📞 Contact Lead] [📊 View Analytics]

🤖 AI Email Classification System | Feature 4: Slack Integration
```

---

### **🔕 EMAILS THAT DO NOT TRIGGER SLACK NOTIFICATIONS:**

#### ❌ **"OUT OF OFFICE" EMAILS** → **NO NOTIFICATION**
- "I am currently out of office..."
- "Vacation until Monday"
- "Automatic reply"

#### ❌ **"MEETING BOOKED" EMAILS** → **NO NOTIFICATION**
- "Meeting scheduled for tomorrow"
- "Calendar invitation accepted"
- "Let's meet at 2 PM"

#### ❌ **"NOT INTERESTED" EMAILS** → **NO NOTIFICATION**
- "Not interested in your services"
- "Please remove me from your list"
- "No thank you"

#### ❌ **"SPAM" EMAILS** → **NO NOTIFICATION**
- "Win $1000 now!!!"
- "Amazing offer! Click here!"
- "Congratulations! You've won..."

---

## 🚀 **HOW TO RUN YOUR SYSTEM**

### **Option 1: Test with Sample Emails**
```bash
cd /home/vikas/Desktop/onebox(1)
source .venv/bin/activate
python test_ai_classification.py
```

### **Option 2: Classify Individual Emails**
```python
from email_classifier import classify_single_email

# This email WILL trigger Slack notification
interested_email = {
    'subject': 'Interested in your AI solution',
    'sender': 'customer@company.com',
    'content': 'Hi, I want to purchase your product. Send me pricing!'
}

result = classify_single_email(interested_email)
# ✅ Slack notification automatically sent!
```

### **Option 3: Start Web Dashboard**
```bash
node index.js
# Open: http://localhost:4000
# View all classified emails with filters
```

---

## 📱 **SLACK NOTIFICATION EXAMPLES**

### **Example 1: High-Interest Lead**
```
🎯 NEW INTERESTED LEAD DETECTED!

📧 Subject: Urgent: Need AI email solution ASAP
👤 From: ceo@bigcompany.com
🎯 Confidence: 98.5%
⏰ Detected: 2025-07-24 21:00:15

📄 Email Preview:
Hi, we need your AI email classification system immediately. Our team is overwhelmed with 2000+ emails daily. Can we schedule a call today to discuss implementation and pricing?

[🎯 View Lead] [📞 Contact Lead] [📊 Analytics]
```

### **Example 2: Demo Interest**
```
🎯 NEW INTERESTED LEAD DETECTED!

📧 Subject: Demo was amazing! Next steps?
👤 From: manager@startup.com
🎯 Confidence: 92.3%
⏰ Detected: 2025-07-24 21:05:30

📄 Email Preview:
Thank you for the demo yesterday. Our team is very impressed with the AI classification accuracy. What are the next steps to get this implemented?

[🎯 View Lead] [📞 Contact Lead] [📊 Analytics]
```

---

## 🎯 **MONITORING YOUR SYSTEM**

### **What to Watch:**
1. **📱 Slack Channel** - Rich notifications for interested leads
2. **🌐 Dashboard** - http://localhost:4000 (view all emails)
3. **📊 Logs** - Classification accuracy and notification status
4. **🔔 Notification Count** - How many leads you're capturing

### **Success Indicators:**
- ✅ Only "Interested" emails trigger Slack notifications
- ✅ No spam notifications for other email types
- ✅ High confidence scores (>80%)
- ✅ Rich message format with action buttons

---

## ⚡ **REAL-TIME BEHAVIOR**

When you process emails:

```
📧 Email arrives → 🤖 AI analyzes → 🎯 If "Interested" → 📱 INSTANT Slack notification
```

**Timeline:**
- Classification: ~1-2 seconds
- Slack notification: Instant
- Rich formatting: Automatic
- Action buttons: Ready to use

---

## 🎉 **YOU'RE ALL SET!**

Your AI Email Classification System with Slack notifications is **LIVE** and ready to catch every interested customer!

**Next Steps:**
1. 📱 **Monitor your Slack channel** for lead notifications
2. 🔄 **Process your real emails** through the system
3. 🎯 **Never miss a potential sale** again!

---

*Last updated: July 24, 2025*
*Feature 4: Slack & Webhook Integration - Active*
