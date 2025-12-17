#!/bin/bash
# Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
# PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
#
# Copyright Header Insertion Script
# Adds copyright headers to source files that don't have them.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Copyright Header Insertion Tool${NC}"
echo -e "${GREEN}========================================${NC}"

# Copyright headers
PYTHON_HEADER="# Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
# PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
# This file contains trade secrets and is protected by law.

"

TS_HEADER="/**
 * Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
 * PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
 * This file contains trade secrets and is protected by law.
 */

"

# Check marker
COPYRIGHT_MARKER="Copyright (c) 2024-2025 Legal Evidence Hub"

# Count statistics
PYTHON_ADDED=0
TS_ADDED=0
PYTHON_SKIPPED=0
TS_SKIPPED=0

# Process Python files
process_python() {
    local file="$1"

    # Skip __pycache__, .venv, node_modules
    if [[ "$file" == *"__pycache__"* ]] || [[ "$file" == *".venv"* ]] || [[ "$file" == *"node_modules"* ]]; then
        return
    fi

    # Skip empty files
    if [ ! -s "$file" ]; then
        return
    fi

    # Check if already has copyright
    if grep -q "$COPYRIGHT_MARKER" "$file" 2>/dev/null; then
        ((PYTHON_SKIPPED++))
        return
    fi

    # Create temp file with header + original content
    local temp_file=$(mktemp)

    # Handle shebang line
    if head -1 "$file" | grep -q "^#!"; then
        head -1 "$file" > "$temp_file"
        echo "" >> "$temp_file"
        echo -n "$PYTHON_HEADER" >> "$temp_file"
        tail -n +2 "$file" >> "$temp_file"
    else
        echo -n "$PYTHON_HEADER" > "$temp_file"
        cat "$file" >> "$temp_file"
    fi

    mv "$temp_file" "$file"
    echo -e "  ${GREEN}Added:${NC} $file"
    ((PYTHON_ADDED++))
}

# Process TypeScript/JavaScript files
process_typescript() {
    local file="$1"

    # Skip node_modules, .next, dist
    if [[ "$file" == *"node_modules"* ]] || [[ "$file" == *".next"* ]] || [[ "$file" == *"dist"* ]]; then
        return
    fi

    # Skip empty files
    if [ ! -s "$file" ]; then
        return
    fi

    # Check if already has copyright
    if grep -q "$COPYRIGHT_MARKER" "$file" 2>/dev/null; then
        ((TS_SKIPPED++))
        return
    fi

    # Create temp file with header + original content
    local temp_file=$(mktemp)
    echo -n "$TS_HEADER" > "$temp_file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    echo -e "  ${GREEN}Added:${NC} $file"
    ((TS_ADDED++))
}

# Mode: check-only or add
MODE="${1:-check}"

if [ "$MODE" = "add" ]; then
    echo -e "${YELLOW}Mode: Adding copyright headers${NC}"
    echo ""

    # Process Python files in backend and ai_worker
    echo "Processing Python files..."
    while IFS= read -r -d '' file; do
        process_python "$file"
    done < <(find "$PROJECT_ROOT/backend" "$PROJECT_ROOT/ai_worker" -name "*.py" -type f -print0 2>/dev/null)

    echo ""
    echo "Processing TypeScript/JavaScript files..."
    # Process TypeScript files in frontend
    while IFS= read -r -d '' file; do
        process_typescript "$file"
    done < <(find "$PROJECT_ROOT/frontend/src" -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -type f -print0 2>/dev/null)

else
    echo -e "${YELLOW}Mode: Check only (use 'add' argument to add headers)${NC}"
    echo ""

    # Count files without copyright
    PYTHON_MISSING=0
    TS_MISSING=0

    echo "Checking Python files..."
    while IFS= read -r -d '' file; do
        if [[ "$file" != *"__pycache__"* ]] && [[ "$file" != *".venv"* ]]; then
            if ! grep -q "$COPYRIGHT_MARKER" "$file" 2>/dev/null; then
                echo -e "  ${RED}Missing:${NC} $file"
                ((PYTHON_MISSING++))
            fi
        fi
    done < <(find "$PROJECT_ROOT/backend" "$PROJECT_ROOT/ai_worker" -name "*.py" -type f -print0 2>/dev/null)

    echo ""
    echo "Checking TypeScript/JavaScript files..."
    while IFS= read -r -d '' file; do
        if [[ "$file" != *"node_modules"* ]] && [[ "$file" != *".next"* ]]; then
            if ! grep -q "$COPYRIGHT_MARKER" "$file" 2>/dev/null; then
                echo -e "  ${RED}Missing:${NC} $file"
                ((TS_MISSING++))
            fi
        fi
    done < <(find "$PROJECT_ROOT/frontend/src" \( -name "*.ts" -o -name "*.tsx" \) -type f -print0 2>/dev/null)

    echo ""
    echo -e "${YELLOW}Summary:${NC}"
    echo "  Python files missing copyright: $PYTHON_MISSING"
    echo "  TypeScript files missing copyright: $TS_MISSING"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
if [ "$MODE" = "add" ]; then
    echo -e "${GREEN}Summary:${NC}"
    echo "  Python files updated: $PYTHON_ADDED"
    echo "  Python files skipped: $PYTHON_SKIPPED"
    echo "  TypeScript files updated: $TS_ADDED"
    echo "  TypeScript files skipped: $TS_SKIPPED"
fi
echo -e "${GREEN}========================================${NC}"
