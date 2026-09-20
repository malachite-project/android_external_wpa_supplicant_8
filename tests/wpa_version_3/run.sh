#!/bin/sh
# Build the extracted WPA-version block with and without the opt-in and
# assert the nl80211 WPA version bits sent for each security configuration.
set -e
cd "$(dirname "$0")"
CC="${CC:-gcc}"
python3 generate.py
$CC -Wall -Wextra -Werror -o harness_off harness.c
$CC -Wall -Wextra -Werror -DCONFIG_DISABLE_WPA_VERSION_3 -o harness_on harness.c
./harness_off
./harness_on
echo "wpa_version_3: all cases PASS"
