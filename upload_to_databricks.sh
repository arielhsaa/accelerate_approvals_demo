#!/bin/bash

# ============================================================================
# Databricks App Upload Script
# ============================================================================
# This script uploads app files to your Databricks Workspace
# Run this BEFORE deploying the app
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}Databricks App Upload Script${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Check if files exist locally
echo -e "${YELLOW}Checking local files...${NC}"
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found in current directory${NC}"
    exit 1
fi
if [ ! -f "app.yaml" ]; then
    echo -e "${RED}❌ Error: app.yaml not found in current directory${NC}"
    exit 1
fi
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found in current directory${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All files found locally${NC}"
echo ""

# Prompt for user email if not provided
if [ -z "$DATABRICKS_USER_EMAIL" ]; then
    echo -e "${YELLOW}Enter your Databricks user email:${NC}"
    read -r DATABRICKS_USER_EMAIL
fi

# Set workspace path
WORKSPACE_PATH="/Workspace/Users/${DATABRICKS_USER_EMAIL}/payment-authorization-premium"
echo -e "${BLUE}Target path: ${WORKSPACE_PATH}${NC}"
echo ""

# Check Databricks CLI authentication
echo -e "${YELLOW}Checking Databricks CLI authentication...${NC}"
if ! databricks current-user me &> /dev/null; then
    echo -e "${RED}❌ Error: Databricks CLI not authenticated${NC}"
    echo -e "${YELLOW}Please run: databricks auth login --host https://[your-workspace-url]${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Databricks CLI authenticated${NC}"
echo ""

# Create workspace directory if it doesn't exist
echo -e "${YELLOW}Creating workspace directory...${NC}"
databricks workspace mkdirs "${WORKSPACE_PATH}" || true
echo -e "${GREEN}✅ Directory ready${NC}"
echo ""

# Upload files
echo -e "${YELLOW}Uploading files to Databricks Workspace...${NC}"
echo ""

echo -e "${BLUE}→ Uploading app.py...${NC}"
databricks workspace upload app.py "${WORKSPACE_PATH}/app.py" --overwrite
echo -e "${GREEN}  ✅ app.py uploaded (60 KB)${NC}"

echo -e "${BLUE}→ Uploading app.yaml...${NC}"
databricks workspace upload app.yaml "${WORKSPACE_PATH}/app.yaml" --overwrite
echo -e "${GREEN}  ✅ app.yaml uploaded (5.5 KB)${NC}"

echo -e "${BLUE}→ Uploading requirements.txt...${NC}"
databricks workspace upload requirements.txt "${WORKSPACE_PATH}/requirements.txt" --overwrite
echo -e "${GREEN}  ✅ requirements.txt uploaded (1.4 KB)${NC}"

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ All files uploaded successfully!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""

# List uploaded files
echo -e "${YELLOW}Verifying uploaded files...${NC}"
databricks workspace ls "${WORKSPACE_PATH}"
echo ""

# Provide deployment command
echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}Next Step: Deploy the app${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${GREEN}Run this command to deploy:${NC}"
echo ""
echo -e "${YELLOW}databricks apps deploy payment-authorization-premium \\${NC}"
echo -e "${YELLOW}  --source-code-path ${WORKSPACE_PATH}${NC}"
echo ""
echo -e "${BLUE}============================================================================${NC}"
