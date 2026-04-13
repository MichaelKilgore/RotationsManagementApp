#!/bin/bash
set -e

echo "Building RotationsManagementApp..."
.venv/bin/pyinstaller App.spec --noconfirm

echo ""
echo "Done! App is at: dist/RotationsManagementApp.app"
