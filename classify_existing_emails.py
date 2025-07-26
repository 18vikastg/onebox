#!/usr/bin/env python3
"""
Batch classify existing emails in Elasticsearch
This script will classify all emails that don't have categories yet
"""

import requests
import json
import logging
import time
from email_classifier import classify_single_email
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_unclassified_emails():
    """Get emails that don't have categories yet"""
    try:
        # Query for emails without category field
        query = {
            "query": {
                "bool": {
                    "must_not": [
                        {"exists": {"field": "category"}}
                    ]
                }
            },
            "size": 1000  # Process in batches of 1000
        }
        
        response = requests.post(
            "http://localhost:9200/emails/_search",
            headers={"Content-Type": "application/json"},
            json=query
        )
        
        if response.status_code == 200:
            data = response.json()
            emails = []
            for hit in data['hits']['hits']:
                email_data = hit['_source']
                email_data['_id'] = hit['_id']
                emails.append(email_data)
            
            logger.info(f"Found {len(emails)} unclassified emails")
            return emails
        else:
            logger.error(f"Failed to query emails: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching unclassified emails: {e}")
        return []

def update_email_classification(email_id, classification):
    """Update email with classification data"""
    try:
        update_data = {
            "doc": {
                "category": classification.get('category', 'Uncategorized'),
                "confidence_score": classification.get('confidence_score', 0.0),
                "classification_method": classification.get('classification_method', 'Unknown'),
                "classified_at": classification.get('classified_at'),
                "processing_time_ms": classification.get('processing_time_ms', 0)
            }
        }
        
        response = requests.post(
            f"http://localhost:9200/emails/_update/{email_id}",
            headers={"Content-Type": "application/json"},
            json=update_data
        )
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error updating email {email_id}: {e}")
        return False

def batch_classify_emails():
    """Main function to classify all unclassified emails"""
    logger.info("🤖 Starting batch email classification...")
    
    # Get unclassified emails
    emails = get_unclassified_emails()
    
    if not emails:
        logger.info("✅ No unclassified emails found. All emails are already classified!")
        return
    
    total_emails = len(emails)
    processed = 0
    successful = 0
    failed = 0
    
    stats = {
        "Interested": 0,
        "Meeting Booked": 0,
        "Not Interested": 0,
        "Spam": 0,
        "Out of Office": 0,
        "Uncategorized": 0
    }
    
    start_time = datetime.now()
    
    logger.info(f"📧 Processing {total_emails} emails...")
    
    for email in emails:
        try:
            # Prepare email data for classification
            email_data = {
                'subject': email.get('subject', ''),
                'sender': email.get('sender', ''),
                'content': email.get('body', '') or email.get('subject', ''),
                'account_email': email.get('account_email', '')
            }
            
            # Classify the email
            classification = classify_single_email(email_data)
            
            # Update in Elasticsearch
            if update_email_classification(email['_id'], classification):
                successful += 1
                category = classification.get('category', 'Uncategorized')
                stats[category] = stats.get(category, 0) + 1
                
                logger.info(f"✅ [{processed + 1}/{total_emails}] Classified: {email.get('subject', 'No Subject')[:50]}... -> {category}")
            else:
                failed += 1
                logger.error(f"❌ [{processed + 1}/{total_emails}] Failed to update: {email.get('subject', 'No Subject')[:50]}...")
            
            processed += 1
            
            # Progress update every 10 emails
            if processed % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = processed / elapsed if elapsed > 0 else 0
                eta = (total_emails - processed) / rate if rate > 0 else 0
                
                logger.info(f"📊 Progress: {processed}/{total_emails} ({processed/total_emails*100:.1f}%) | "
                           f"Rate: {rate:.1f} emails/sec | ETA: {eta:.0f}s")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.1)
            
        except Exception as e:
            failed += 1
            logger.error(f"❌ Error processing email {processed + 1}: {e}")
            processed += 1
    
    # Final statistics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 50)
    logger.info("🎉 BATCH CLASSIFICATION COMPLETE!")
    logger.info("=" * 50)
    logger.info(f"📊 Total Processed: {processed}")
    logger.info(f"✅ Successful: {successful}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"⏱️ Duration: {duration:.2f} seconds")
    logger.info(f"🚀 Average Rate: {processed/duration:.2f} emails/second")
    logger.info("")
    logger.info("📋 CATEGORY BREAKDOWN:")
    for category, count in stats.items():
        if count > 0:
            percentage = (count / successful * 100) if successful > 0 else 0
            logger.info(f"  {category}: {count} ({percentage:.1f}%)")
    logger.info("=" * 50)

def show_classification_stats():
    """Show current classification statistics"""
    try:
        # Get category aggregation
        query = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {
                        "field": "category",
                        "size": 20
                    }
                },
                "classification_methods": {
                    "terms": {
                        "field": "classification_method",
                        "size": 10
                    }
                }
            }
        }
        
        response = requests.post(
            "http://localhost:9200/emails/_search",
            headers={"Content-Type": "application/json"},
            json=query
        )
        
        if response.status_code == 200:
            data = response.json()
            total_emails = data['hits']['total']['value']
            
            print("\n📊 EMAIL CLASSIFICATION STATISTICS")
            print("=" * 40)
            print(f"Total Emails: {total_emails}")
            print("\nCategories:")
            
            if 'categories' in data['aggregations']:
                for bucket in data['aggregations']['categories']['buckets']:
                    category = bucket['key']
                    count = bucket['doc_count']
                    percentage = (count / total_emails * 100) if total_emails > 0 else 0
                    print(f"  {category}: {count} ({percentage:.1f}%)")
            
            print("\nClassification Methods:")
            if 'classification_methods' in data['aggregations']:
                for bucket in data['aggregations']['classification_methods']['buckets']:
                    method = bucket['key']
                    count = bucket['doc_count']
                    percentage = (count / total_emails * 100) if total_emails > 0 else 0
                    print(f"  {method}: {count} ({percentage:.1f}%)")
            
            print("=" * 40)
            
        else:
            logger.error(f"Failed to get statistics: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_classification_stats()
    else:
        print("🤖 AI Email Classification Batch Processor")
        print("=" * 50)
        print("This script will classify all existing emails in your Elasticsearch index.")
        print("Make sure you have added your OPENAI_API_KEY to your environment.")
        print("")
        
        # Check if OpenAI API key is available
        import os
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")
            print("Please set your OpenAI API key before running this script.")
            print("Example: export OPENAI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        response = input("Do you want to proceed? (y/n): ")
        if response.lower() == 'y':
            batch_classify_emails()
            print("\n📊 Final Statistics:")
            show_classification_stats()
        else:
            print("❌ Classification cancelled.")
