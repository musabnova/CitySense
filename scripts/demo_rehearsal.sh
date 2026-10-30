#!/usr/bin/env bash
# ==============================================================================
# CITYSENSE 5-MINUTE LIVE DEMONSTRATION WALKTHROUGH SCRIPT
# ==============================================================================
# PRD Reference: Section 8.2 (5-Minute Demonstration Protocol)
# Run via Git Bash, WSL, or macOS/Linux: bash scripts/demo_rehearsal.sh
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}==============================================================================${NC}"
echo -e "${CYAN}         CITYSENSE: FROM COMPLAINTS TO ACTION - 5-MINUTE LIVE DEMO            ${NC}"
echo -e "${CYAN}==============================================================================${NC}"
echo -e "Platform Version : 0.1.0-alpha"
echo -e "Backend Server   : http://localhost:8000"
echo -e "Frontend Portals : http://localhost:3000"
echo -e "${CYAN}==============================================================================${NC}\n"

# 1. Health Handshake
echo -e "${YELLOW}>> Performing Pre-Flight Health Checks...${NC}"
if curl -s http://localhost:8000/api/health/db | grep -q "healthy"; then
    echo -e "${GREEN}[OK] Backend API & Database Connection Healthy${NC}"
else
    echo -e "${RED}[WARN] Backend server not detected on port 8000.${NC}"
    echo -e "       Start with: python -m apps.api.standalone_server"
fi

echo -e "\n${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}MINUTE 1: CAPTURE — CITIZEN MOBILE INTAKE (Maya)${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "1. Open mobile browser or Chrome DevTools (390x844 iPhone viewport):"
echo -e "   ${CYAN}URL: http://localhost:3000/report${NC}"
echo -e "2. Drag map pin to MG Road corridor (12.9716, 77.5946)."
echo -e "3. Enter problem description:"
echo -e "   'Severe monsoon waterlogging near St. Jude School. 2 feet standing water.'"
echo -e "4. Click 'Send report'."
echo -e "5. Note the generated 12-character Tracking ID (e.g. ${YELLOW}CS-XXXX-XXXX${NC})."
echo -e "   Notice: EXIF metadata is stripped, and coordinates are anchored."
read -p "Press [Enter] when Minute 1 is completed to proceed to Minute 2..."

echo -e "\n${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}MINUTE 2: UNDERSTAND — AI TRIAGE & EXPLAINABILITY (David)${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "1. Switch to the Administrative Command Console:"
echo -e "   ${CYAN}URL: http://localhost:3000/dashboard${NC}"
echo -e "2. Inspect the left-hand 'Fix First' queue:"
echo -e "   - Maya's report appears prioritized based on multi-factor scoring."
echo -e "   - Category verified automatically as 'Waterlogging & Drainage'."
echo -e "   - One-sentence concise AI summary compressed (< 25 words)."
echo -e "3. Click on the card to inspect the 'Why High?' Explainability Card:"
echo -e "   - Points breakdown: Near a school (+40), Linked duplicates (+20), Hazard (+15)."
echo -e "   - Point to the human-in-the-loop microcopy:"
echo -e "     ${YELLOW}\"AI can misread photos. An officer confirms.\"${NC}"
read -p "Press [Enter] when Minute 2 is completed to proceed to Minute 3..."

echo -e "\n${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}MINUTE 3: REVEAL — SPATIAL HOTSPOT & ACTION BRIEF SYNTHESIS${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "1. Look at the GIS map canvas in the center:"
echo -e "   - Notice the rust-red dashed ellipse over the MG Road corridor."
echo -e "   - Capsule badge reads: 'MG Road Hotspot - 8 Reports'."
echo -e "2. Click on the MG Road cluster badge."
echo -e "3. Click 'Generate Action Brief' in the modal:"
echo -e "   - Synthesizes dual-department action: storm drain desilting + asphalt repair."
echo -e "   - Generation completes in under 15 seconds (typical: < 20 ms)."
echo -e "   - Displays consolidated impact across 8 underlying citizen tickets."
read -p "Press [Enter] when Minute 3 is completed to proceed to Minute 4..."

echo -e "\n${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}MINUTE 4: ACT — WORK ORDER DISPATCH & FIELD RESOLUTION (Carlos)${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "1. In the Action Brief / Incident Panel, select:"
echo -e "   Crew: 'Drainage Crew A' or 'Public Works - Stormwater Drainage Division'."
echo -e "2. Click 'Assign Work Order':"
echo -e "   - Notice atomic status transition: master + child reports -> 'Assigned'."
echo -e "   - Notice mock integration logs: [Demo Data - Mocked SMS Service] fired."
echo -e "3. Switch to the Field Maintenance Portal:"
echo -e "   ${CYAN}URL: http://localhost:3000/tasks${NC}"
echo -e "4. Select 'Drainage Crew A'. See the assigned job card."
echo -e "5. Click 'Mark Fixed', enter repair notes: 'Culvert cleared, silt grate fitted.'"
echo -e "6. Click 'Mark Fixed' CTA -> Updates PostgreSQL/SQLite status to 'Resolved'."
read -p "Press [Enter] when Minute 4 is completed to proceed to Minute 5..."

echo -e "\n${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}MINUTE 5: FEEDBACK LOOP — CITIZEN RESOLUTION VERIFICATION (Maya)${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "1. Open the Citizen Status Tracker:"
echo -e "   ${CYAN}URL: http://localhost:3000/track/[Tracking-ID]${NC}"
echo -e "2. Verify the vertical timeline node has progressed to 'Resolved'."
echo -e "3. Point out:"
echo -e "   - Resolution notes logged by Carlos are visible to Maya."
echo -e "   - If report was a duplicate, duplicate consolidation banner is visible."
echo -e "   - QR code can be scanned on another mobile phone to share status."
echo -e "4. Conclude presentation:"
echo -e "   ${GREEN}\"CitySense closes the municipal loop — From Complaints to Action.\"${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}\n"
echo -e "${GREEN}DEMONSTRATION REHEARSAL COMPLETE.${NC}"

