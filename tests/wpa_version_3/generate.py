#!/usr/bin/env python3
"""Generate harness.c by extracting the body of the live wpa_ver_supported()
from src/drivers/driver_nl80211.c into harness.c.in.

Keeping the block extracted (rather than copied) means the test fails loudly
if upstream restructures the code, instead of silently testing a stale copy.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
SRC = os.path.join(ROOT, 'src', 'drivers', 'driver_nl80211.c')

FUNC = 'static int wpa_ver_supported(struct wpa_driver_nl80211_data *drv,'
START = '\tif (proto & WPA_PROTO_WPA)'
END = '\treturn ver;\n}'


def extract():
    text = io.open(SRC, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    try:
        start = text.index(START, text.index(FUNC))
        end = text.index(END, start)
    except ValueError:
        sys.exit('marker not found in %s; upstream layout changed' % SRC)
    block = text[start:end].rstrip() + '\n'
    for token in ('NL80211_WPA_VERSION_2', 'NL80211_WPA_VERSION_3',
                  'CONFIG_DISABLE_WPA_VERSION_3'):
        if token not in block:
            sys.exit('extracted block is missing %s' % token)
    return block


def main():
    block = extract()
    tpl = io.open(os.path.join(HERE, 'harness.c.in'),
                  encoding='utf-8', newline='').read().replace('\r\n', '\n')
    if '@BLOCK@' not in tpl:
        sys.exit('harness.c.in has no @BLOCK@ placeholder')
    out = tpl.replace('@BLOCK@', block.rstrip())
    io.open(os.path.join(HERE, 'harness.c'), 'w',
            encoding='utf-8', newline='\n').write(out)
    print('generated harness.c (%d bytes)' % len(out))


if __name__ == '__main__':
    main()
