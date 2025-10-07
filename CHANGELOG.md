## v0.3.6 - 2025-10-07
Enhance translation system compatibility

TRANSLATION IMPROVEMENTS: Enhanced config flow translations with comprehensive data_description fields for better Home Assistant compatibility. Improved field descriptions and user guidance text. Verified translation structure matches Home Assistant standards and working integration examples. Ready for latest HA versions with proper friendly text support.

## v0.3.5 - 2025-10-07
Add comprehensive friendly text to config flow

UI IMPROVEMENTS: Added helpful descriptions for all config flow fields including email, password, usage days, and auto-restart settings. Enhanced user experience with clear guidance text under each input field in both initial setup and options configuration.

## v0.3.4 - 2025-10-07
Improve config flow UX and add debug notifications

UX IMPROVEMENTS: Implemented conditional config flow steps - restart time field only shows when auto-restart is enabled, providing cleaner user experience. Added comprehensive debug notifications for auto-restart feature including scheduling confirmations, success/failure alerts, and settings change notifications. Enhanced user guidance with dedicated restart time configuration step.

## v0.3.3 - 2025-10-07
Fix multiple integration errors

CRITICAL FIXES: Fixed config flow schema serialization error with time picker. Fixed sensor attribute errors with last_update_success. Fixed date parsing to return proper date objects for date sensors. Fixed monetary sensor state class warnings. Integration now works completely without setup or runtime errors.

## v0.3.2 - 2025-10-07
Fix critical config flow and timezone bugs

CRITICAL FIXES: Fixed broken config flow class structure that was causing 'not_implemented' error. Fixed timezone handling error in auto-restart scheduling. Improved config flow UI to always show restart time field with clearer descriptions. Integration now sets up properly and auto-restart feature works correctly.

## v0.3.1 - 2025-10-07
Fix initialization race condition

Fixed auto-restart initialization race condition that was causing 'not_implemented' error during integration setup. Auto-restart scheduling now happens after coordinator is fully initialized, preventing setup conflicts.

**[2025-10-07]** 0.2.0


**[2025-10-07]** 0.1.2


**[2025-10-07]** 0.1.1

# CHANGE LOG
**[2025-10-07]** 0.3.0

- **Major feature: Automatic daily integration restart**
	- Optionally restart the Contact Energy integration at a user-set time (default 03:00, disabled by default) to improve reliability and speed of historical data downloads
	- Uses Home Assistant time picker for configuration
	- Immediate effect when options are changed
	- Next scheduled restart is logged
	- 5 retry attempts with 5-minute intervals if restart fails; error notification if all fail
	- Option to enable/disable from both setup and options
- **Updated all version numbers** to 0.3.0

**[2025-10-07]** 0.2.0

- **Major improvement: Background data downloading** - Large datasets (>30 days) now download in the background to prevent UI blocking

**[2025-10-07]** 0.0.14

- **bumped version to 0.0.14 across README and info**

**[2025-10-07]** 0.0.13

- **deleted manifest.json**
- **bumped version to 0.0.13 across README and info**

**[2025-10-07]** 0.0.12

- **removed undocumented "domain" field from hacs.json**
- **bumped version to 0.0.12 across manifest, README, and info**

**[2025-10-07]** 0.0.11

- **added instructions in hacs.json**
- **bumped version to 0.0.11 across manifest, README, info, and hacs.json**
**[2025-10-07]** 0.0.10

- **fixed error in a link in README.md**
- **removed reference to Australia from the country field in hacs.json**
- **bumped version to 0.0.10 across manifest, README, info, and hacs.json**
**[2025-10-07]** 0.0.9

- **removed** all non-HACS files and folders (scripts, .github, support material, release notes)
- **fixed** all references to assets folder and PNG assets
- **confirmed** manifest.json is in correct location
- **bumped** version to 0.0.9 across manifest, README, and info

**[2025-10-07]** 0.0.8

- **added** explicit .hacs file to specify domain
- **removed** zip_release and filename from hacs.json
- **bumped** version to 0.0.8 across manifest, README, and info

**[2025-10-07]** 0.0.7

- **fixed** README.md to use logo.svg instead of assets PNG
- **bumped** version to 0.0.7 across manifest, README, and info

**[2025-10-07]** 0.0.6

- **bumped** version to 0.0.6 across manifest, README, and info
- **updated** SVG assets and branding

**[2025-10-07]** 0.0.5

- **updated** icon.svg and logo.svg to reference provided SVG assets

**[2025-10-07]** 0.0.4

- **updated** icon.svg and logo.svg to reference provided PNG assets
- **bumped** version to 0.0.4 across manifest, README, and info

**[2025-10-07]** 0.0.3

- **bumped** version to 0.0.3 across manifest, README, and info
- **referenced** uploaded Contact Energy PNG logo in README and info

**[2025-10-07]** 0.0.2

- **added** HACS store images (icon.svg, logo.svg) and info.md

**[2025-10-07]** 0.0.1

- **created** my repository and uploaded the original files from [notf0und's repository](https://github.com/notf0und/ha-contact-energy)
- **created** this CHANGELOG.md
- **added** Attributions to codyc1515 and notf0und to README.md
- **added** rationale and explanation to README.md
- **labelled** this version 0.0.1
- **created** mainfest.json with correct version number
- **updated** manifest.json with correct owner and document paths
- **updated** hacs.json to align metadata and iot_class

**[2025-10-07]** 0.0.5

 **updated** icon.svg and logo.svg to reference provided SVG assets

**[2025-10-07]** 0.0.6

- **bumped** version to 0.0.6 across manifest, README, and info
- **updated** SVG assets and branding

**[2025-10-07]** 0.0.7

- **fixed** README.md to use logo.svg instead of assets PNG
- **bumped** version to 0.0.7 across manifest, README, and info

**[2025-10-07]** 0.0.8

- **added** explicit .hacs file to specify domain
- **removed** zip_release and filename from hacs.json
- **bumped** version to 0.0.8 across manifest, README, and info

**[2025-10-07]** 0.0.9

- **removed** all non-HACS files and folders (scripts, .github, support material, release notes)
- **fixed** all references to assets folder and PNG assets
- **confirmed** manifest.json is in correct location
- **bumped** version to 0.0.9 across manifest, README, and info

**[2025-10-07]** 0.0.4

- **updated** icon.svg and logo.svg to reference provided PNG assets
- **bumped** version to 0.0.4 across manifest, README, and info

**[2025-10-07]** 0.0.3

- **bumped** version to 0.0.3 across manifest, README, and info
- **referenced** uploaded Contact Energy PNG logo in README and info

**[2025-10-07]** 0.0.2

- **added** HACS store images (icon.svg, logo.svg) and info.md


**[2025-10-07]** 0.0.1

- **created** my repository and uploaded the original files from [notf0und's repository](https://github.com/notf0und/ha-contact-energy)
- **created** this CHANGELOG.md
- **added** Attributions to codyc1515 and notf0und to README.md
- **added** rationale and explanation to README.md
- **labelled** this version 0.0.1
- **created** mainfest.json with correct version number
- **updated** manifest.json with correct owner and document paths
- **updated** hacs.json to align metadata and iot_class
