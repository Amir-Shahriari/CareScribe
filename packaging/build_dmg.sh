#!/usr/bin/env bash
# Wrap the built CareScribe.app in a drag-to-Applications .dmg.
#
#   bash packaging/build_dmg.sh
#
# MUST RUN ON macOS. PyInstaller does not cross-compile, so both the .app this
# consumes and this script itself only work on a Mac. Requires the .icns from
# packaging/make_icon.py (which also only emits .icns on macOS).
#
# Output: dist/CareScribe.dmg — the user opens it, drags CareScribe into
# Applications, and can then drag it from Applications to the Dock.
set -euo pipefail
cd "$(dirname "$0")/.."

APP="dist/CareScribe.app"
DMG="dist/CareScribe.dmg"
STAGE="dist/dmg-stage"

[ -d "$APP" ] || { echo "No $APP — run packaging/build_macos.sh first"; exit 1; }

rm -rf "$STAGE" "$DMG"
mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
# The Applications symlink is what makes the drag gesture obvious.
ln -s /Applications "$STAGE/Applications"

hdiutil create -volname "CareScribe" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
rm -rf "$STAGE"
echo "Built $DMG"

# ---------------------------------------------------------------------------
# Signing and notarization — required for BOTH the .app and the .dmg.
#
# Gatekeeper blocks an unsigned, un-notarized download outright: the clinician
# sees "CareScribe cannot be opened because the developer cannot be verified"
# and has no reasonable way forward. Sign the app first, then the dmg.
#
#   codesign --deep --force --options runtime --timestamp \
#       --sign "Developer ID Application: YOUR NAME (TEAMID)" dist/CareScribe.app
#   # rebuild the dmg from the signed app, then:
#   codesign --force --timestamp \
#       --sign "Developer ID Application: YOUR NAME (TEAMID)" dist/CareScribe.dmg
#
#   xcrun notarytool submit dist/CareScribe.dmg \
#       --apple-id you@example.com --team-id TEAMID --password APP_SPECIFIC_PW --wait
#   xcrun stapler staple dist/CareScribe.dmg
#   spctl -a -vvv -t install dist/CareScribe.app   # verify
#
# Requires a paid Apple Developer account.
# ---------------------------------------------------------------------------
echo ""
echo "NOT SIGNED OR NOTARIZED. Gatekeeper will block this. See comments in this script."
