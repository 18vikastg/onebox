#!/usr/bin/env python3
"""
Update Elasticsearch index to include email classification fields
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_elasticsearch_mapping():
    """Update the emails index mapping to include classification fields"""
    
    # New mapping for classification fields
    mapping_update = {
        "properties": {
            "category": {
                "type": "keyword"
            },
            "confidence_score": {
                "type": "float"
            },
            "classification_method": {
                "type": "keyword"
            },
            "classified_at": {
                "type": "date"
            },
            "processing_time_ms": {
                "type": "integer"
            }
        }
    }
    
    try:
        # Update the mapping
        url = "http://localhost:9200/emails/_mapping"
        response = requests.put(url, json=mapping_update)
        
        if response.status_code == 200:
            logger.info("✅ Successfully updated Elasticsearch mapping for email classification")
            return True
        else:
            logger.error(f"❌ Failed to update mapping: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating Elasticsearch mapping: {e}")
        return False

def verify_mapping():
    """Verify the updated mapping"""
    try:
        url = "http://localhost:9200/emails/_mapping"
        response = requests.get(url)
        
        if response.status_code == 200:
            mapping = response.json()
            properties = mapping.get('emails', {}).get('mappings', {}).get('properties', {})
            
            classification_fields = ['category', 'confidence_score', 'classification_method']
            missing_fields = [field for field in classification_fields if field not in properties]
            
            if not missing_fields:
                logger.info("✅ All classification fields are present in the mapping")
                return True
            else:
                logger.warning(f"⚠️ Missing classification fields: {missing_fields}")
                return False
        else:
            logger.error(f"❌ Failed to verify mapping: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying mapping: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Updating Elasticsearch mapping for email classification...")
    
    if update_elasticsearch_mapping():
        print("✅ Mapping update completed successfully")
        
        if verify_mapping():
            print("✅ Mapping verification successful")
        else:
            print("⚠️ Mapping verification failed")
    else:
        print("❌ Mapping update failed")
