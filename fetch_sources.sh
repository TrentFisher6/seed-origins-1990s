#!/bin/sh
# Download the primary documents the constants are checked against and extract their text.
# Not redistributed here; needs curl and pdftotext (poppler).
set -e
cd "$(dirname "$0")/data/agent/raw" 2>/dev/null || { mkdir -p "$(dirname "$0")/data/agent/raw"; cd "$(dirname "$0")/data/agent/raw"; }
mkdir -p fips sec2 certicom
get() { [ -s "$1" ] || curl -fsSL -A "Mozilla/5.0" -o "$1" "$2"; pdftotext "$1" "${1%.pdf}.txt"; echo "ok  $1"; }
get fips/fipspub186-legacy.pdf https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub186.pdf
get fips/fips186-1-csrc.pdf    https://csrc.nist.gov/files/pubs/fips/186-1/final/docs/fips186-1.pdf
get fips/fips186-2.pdf         https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf
get sec2/sec2-v1.pdf           https://www.secg.org/SEC2-Ver-1.0.pdf
get sec2/sec2-v2.pdf           https://www.secg.org/sec2-v2.pdf
get certicom/challenge-2009.pdf https://www.certicom.com/content/dam/certicom/images/pdfs/challenge-2009.pdf
cp certicom/challenge-2009.txt certicom/ch09.txt
