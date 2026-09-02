#!/usr/bin/env bash
# Build the CareScribe macOS desktop app.
#
#   bash packaging/build_macos.sh
#
# Produces dist/CareScribe.app. MUST BE RUN ON macOS — PyInstaller does not
# cross-compile, so this cannot be produced from Windows or Linux.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -r packaging/requirements-build.txt

python3 packaging/make_icon.py

python3 -m PyInstaller packaging/carescribe.spec --noconfirm --clean

test -d dist/CareScribe.app || { echo "Build failed"; exit 1; }
echo "Built dist/CareScribe.app"

echo "Verifying the frozen app launches..."
python3 packaging/verify_frozen.py dist/CareScribe.app || {
    echo "Frozen app failed its launch smoke check"; exit 1;
}

bash packaging/build_dmg.sh

# ---------------------------------------------------------------------------
# Signing and notarization. UNSIGNED BUILDS ARE BLOCKED BY GATEKEEPER.
#
# macOS will refuse to open an unsigned, un-notarized app downloaded from the
# internet — the user gets "CareScribe cannot be opened because the developer
# cannot be verified". Do not ship that to a clinician.
#
#   # 1. Sign with a Developer ID Application certificate, hardened runtime on:
#   codesign --deep --force --options runtime --timestamp \
#       --sign "Developer ID Application: YOUR NAME (TEAMID)" dist/CareScribe.app
#
#   # 2. Notarize (Apple scans it; takes a few minutes):
#   ditto -c -k --keepParent dist/CareScribe.app dist/CareScribe.zip
#   xcrun notarytool submit dist/CareScribe.zip \
#       --apple-id you@example.com --team-id TEAMID --password APP_SPECIFIC_PW --wait
#
#   # 3. Staple the ticket so it works offline:
#   xcrun stapler staple dist/CareScribe.app
#   spctl -a -vvv -t install dist/CareScribe.app   # verify
#
# Requires a paid Apple Developer account.
# ---------------------------------------------------------------------------
echo ""
echo "NOT SIGNED OR NOTARIZED. Gatekeeper will block this. See comments in this script."
