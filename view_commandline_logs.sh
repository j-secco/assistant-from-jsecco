#!/bin/bash
# Simple script to view the latest command-line logs

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}📋 Command-Line Log Viewer${NC}"
echo "=========================="

if [ ! -d "logs" ]; then
    echo -e "${RED}❌ No logs directory found.${NC}"
    exit 1
fi

# Find latest command-line logs
LATEST_SESSION=$(ls logs/commandline_session_*.log 2>/dev/null | sort | tail -1)
LATEST_ERROR=$(ls logs/commandline_errors_*.log 2>/dev/null | sort | tail -1)

if [ -z "$LATEST_SESSION" ]; then
    echo -e "${RED}❌ No command-line session logs found.${NC}"
    echo "Run 'python3 src/main.py' to generate logs."
    exit 1
fi

echo -e "${BLUE}📄 Latest Session Log: ${LATEST_SESSION}${NC}"
echo "----------------------------------------"
cat "$LATEST_SESSION"

echo
echo -e "${RED}🔥 Latest Error Log: ${LATEST_ERROR}${NC}"
echo "----------------------------------------"
if [ -f "$LATEST_ERROR" ] && [ -s "$LATEST_ERROR" ]; then
    cat "$LATEST_ERROR"
else
    echo "No errors logged in this session."
fi

echo
echo -e "${GREEN}✅ Log viewing complete${NC}"
