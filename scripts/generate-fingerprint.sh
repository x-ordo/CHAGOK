#!/bin/bash
# Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
# PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
#
# Build Fingerprint Generator
# This script generates unique fingerprints for each build deployment.
# These fingerprints enable tracking of unauthorized code distribution.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Legal Evidence Hub - Build Fingerprint${NC}"
echo -e "${GREEN}========================================${NC}"

# Generate build information
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_ID=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "$(date +%s)-$(hostname)")
BUILD_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
BUILD_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
BUILD_TAG=$(git describe --tags --always 2>/dev/null || echo "v0.0.0")

# Generate fingerprint hash
FINGERPRINT_INPUT="${BUILD_ID}|${BUILD_DATE}|${BUILD_COMMIT}|LEH-2024-PROPRIETARY"
BUILD_FINGERPRINT=$(echo -n "$FINGERPRINT_INPUT" | sha256sum | cut -c1-32)

echo -e "${YELLOW}Build Information:${NC}"
echo "  Date:        $BUILD_DATE"
echo "  ID:          $BUILD_ID"
echo "  Commit:      $BUILD_COMMIT"
echo "  Branch:      $BUILD_BRANCH"
echo "  Tag:         $BUILD_TAG"
echo "  Fingerprint: $BUILD_FINGERPRINT"

# Create build info JSON file
BUILD_INFO_FILE=".build-info.json"
cat > "$BUILD_INFO_FILE" << EOF
{
  "product": "Legal Evidence Hub",
  "version": "$BUILD_TAG",
  "build_id": "$BUILD_ID",
  "build_date": "$BUILD_DATE",
  "build_commit": "$BUILD_COMMIT",
  "build_branch": "$BUILD_BRANCH",
  "build_fingerprint": "$BUILD_FINGERPRINT",
  "copyright": "Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.",
  "license": "Proprietary",
  "tracking": {
    "enabled": true,
    "watermark": "LEH-2024-PROPRIETARY-8a7b6c5d4e3f2g1h"
  }
}
EOF

echo -e "${GREEN}Created: $BUILD_INFO_FILE${NC}"

# Export environment variables for build process
export LEH_BUILD_ID="$BUILD_ID"
export LEH_BUILD_TIMESTAMP="$BUILD_DATE"
export LEH_BUILD_COMMIT="$BUILD_COMMIT"
export LEH_BUILD_BRANCH="$BUILD_BRANCH"
export LEH_BUILD_FINGERPRINT="$BUILD_FINGERPRINT"

# Create .env.build file for CI/CD
ENV_BUILD_FILE=".env.build"
cat > "$ENV_BUILD_FILE" << EOF
# Auto-generated build environment variables
# DO NOT COMMIT THIS FILE
LEH_BUILD_ID=$BUILD_ID
LEH_BUILD_TIMESTAMP=$BUILD_DATE
LEH_BUILD_COMMIT=$BUILD_COMMIT
LEH_BUILD_BRANCH=$BUILD_BRANCH
LEH_BUILD_FINGERPRINT=$BUILD_FINGERPRINT

# Frontend build variables
NEXT_PUBLIC_BUILD_ID=$BUILD_ID
NEXT_PUBLIC_BUILD_TIMESTAMP=$BUILD_DATE
NEXT_PUBLIC_BUILD_COMMIT=$BUILD_COMMIT
EOF

echo -e "${GREEN}Created: $ENV_BUILD_FILE${NC}"

# Update LICENSE file with build info
if [ -f "LICENSE" ]; then
    sed -i.bak "s/\${BUILD_FINGERPRINT}/$BUILD_FINGERPRINT/g" LICENSE
    sed -i.bak "s/\${VERSION}/$BUILD_TAG/g" LICENSE
    sed -i.bak "s/\${BUILD_DATE}/$BUILD_DATE/g" LICENSE
    rm -f LICENSE.bak
    echo -e "${GREEN}Updated: LICENSE with build fingerprint${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fingerprint generation complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""
echo -e "${RED}NOTICE: This build contains code tracking mechanisms.${NC}"
echo -e "${RED}Unauthorized distribution can be traced.${NC}"
