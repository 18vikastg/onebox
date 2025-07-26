#!/bin/bash

# ReachInbox Deployment Test Script
# Tests all components after deployment

echo "🧪 Testing ReachInbox Deployment..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$url"); then
        if [ "$response" -eq "$expected_status" ]; then
            echo -e "${GREEN}✓ PASS${NC} ($response)"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $response)"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection failed)"
        ((FAILED++))
    fi
}

test_docker_service() {
    local service=$1
    local name=$2
    
    echo -n "Testing Docker service $name... "
    
    if docker ps | grep -q "$service"; then
        echo -e "${GREEN}✓ RUNNING${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        ((FAILED++))
    fi
}

echo "📡 Testing HTTP Endpoints:"
test_endpoint "http://localhost:4000/health" "Main Application Health"
test_endpoint "http://localhost:4000" "Main Application Homepage"
test_endpoint "http://localhost:9200/_cluster/health" "Elasticsearch Health"
test_endpoint "http://localhost:5601/api/status" "Kibana Status"
test_endpoint "http://localhost:4000/api/stats" "Application API"

echo ""
echo "🐳 Testing Docker Services:"
test_docker_service "reachinbox-web" "Web Application"
test_docker_service "reachinbox-sync" "Email Sync Service"
test_docker_service "reachinbox-elasticsearch" "Elasticsearch"
test_docker_service "reachinbox-redis" "Redis"
test_docker_service "reachinbox-kibana" "Kibana"

echo ""
echo "📁 Testing File System:"
echo -n "Testing logs directory... "
if [ -d "./logs" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ MISSING${NC}"
    ((FAILED++))
fi

echo -n "Testing environment file... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ MISSING${NC} (Copy from .env.example)"
    ((FAILED++))
fi

echo -n "Testing vector database... "
if [ -d "./reply_vector_db" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ MISSING${NC} (Will be created on first run)"
fi

echo ""
echo "🔍 Testing Email Configuration:"
if [ -f ".env" ]; then
    if grep -q "GMAIL_PRIMARY_EMAIL=" .env && [ -n "$(grep GMAIL_PRIMARY_EMAIL= .env | cut -d'=' -f2)" ]; then
        echo -e "Primary Gmail: ${GREEN}✓ CONFIGURED${NC}"
        ((PASSED++))
    else
        echo -e "Primary Gmail: ${RED}✗ NOT CONFIGURED${NC}"
        ((FAILED++))
    fi
    
    if grep -q "OPENAI_API_KEY=" .env && [ -n "$(grep OPENAI_API_KEY= .env | cut -d'=' -f2)" ]; then
        echo -e "OpenAI API: ${GREEN}✓ CONFIGURED${NC}"
        ((PASSED++))
    else
        echo -e "OpenAI API: ${YELLOW}⚠ NOT CONFIGURED${NC}"
    fi
fi

echo ""
echo "📊 Test Summary:"
echo "=================================="
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo "Total Tests: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Your ReachInbox deployment is ready!${NC}"
    echo ""
    echo "📱 Access your application:"
    echo "  • Main App: http://localhost:4000"
    echo "  • Kibana:   http://localhost:5601"
    echo "  • Health:   http://localhost:4000/health"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Configure your domain/SSL if needed"
    echo "  2. Set up monitoring and backups"
    echo "  3. Test email synchronization"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
    echo ""
    echo "🔧 Common fixes:"
    echo "  • Make sure all Docker containers are running"
    echo "  • Check .env file configuration"
    echo "  • Verify network connectivity"
    echo "  • Check logs: docker-compose logs -f"
    exit 1
fi
