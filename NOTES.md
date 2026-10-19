# NOTES — 1990s "verifiably random" seeds

## 2026-10-19 14:10 round 1 start
Plan:
1. Prior-art search (MinghuaQu, X9.62 seeds, Certicom challenge seeds).
2. Collect seeds: OpenSSL crypto/ec/ec_curve.c has X9.62 + SECG seeds with params.
3. Implement X9.62/SEC1 seed->param verification (SHA-1 based) to confirm seeds.
4. Structure analysis of SECG seeds (MinghuaQu offset, shared tails).
5. Generator sweep with planted controls (lrand48 etc).

## 14:12 seeds collected + verified
- data/openssl/ec_curve.c (OpenSSL master) parsed by scripts/parse_openssl.py -> data/openssl_curves.json
- scripts/verify.py implements X9.62 A.3.3 (SHA-1 seed->W). ALL MinghuaQu seeds verify:
  prime (r*b^2 = a^3): secp112r1/r2, secp128r1/r2, secp160r1/r2, X9.62 prime192v2/v3, prime239v1-3 (no MQ).
  binary (b = W, top bit NOT cleared): sect113r1/r2, sect131r1/r2, sect193r1/r2, c2pnb163v1-3, c2tnb191v1-3, c2tnb239v1-3, c2tnb359v1.
- X9.62 c2pnb176w1, c2pnb208w1, c2pnb272w1, c2pnb304w1, c2pnb368w1, c2tnb431r1: NO seed in OpenSSL (not verifiably random). 
- WTLS4=sect113r1, WTLS5=c2pnb163v1, WTLS6=secp112r1, WTLS7=secp160r2, WTLS11=sect233r1 (NIST B-233): same seeds, nothing new.
- X9.62 prime192v2/v3, prime239v1-3 seeds have NO MQ -> NIST-style; candidate for lrand48 method.
- So ALL X9.62 binary example curve seeds contain MinghuaQu: Certicom generated both X9.62 c2* and SECG r-curves.

## 14:12 structure (scripts/structure.py)
Model: seed(40 nibbles) = F[:k] || hex("MinghuaQu") || F[k:], F = 22-nibble filler, k = nibble insertion pos.
k values: 0,2,5,6,6,6,8,9,10,10,11(x10),12,21(x3). "4-bit offset" = odd k.
Evidence for INSERTION (not overwrite): sect131r1 (k=0) F=985bd3adbada21b43a97e2, sect131r2 (k=11) F=985bd3adbada21b43a97e3
  -> same filler, last nibble +1. Overwrite model would need a 11-nibble coincidence.
sect113r2 F=10c0fb15760860def1eefd vs c2pnb163v1 F=d2c0fb15760860def1eef4 (both k=21): share 19 middle nibbles; first byte 10 vs d2, last nibble d vs 4.
First byte 0x10 in 5 SECG seeds (secp160r1, sect113r1, sect113r2, sect193r1, sect193r2); 0x00 in all 4 secp112/128.

## 14:15 Certicom challenge seeds (agent: data/agent/certicom.json, verify data/agent/certicom_verification.json)
- Certicom ECC challenge (1997) seedE/seedP/seedQ ALSO embed MinghuaQu (88 MQ seeds total incl. SECG + X9.62; data/all_seeds.json).
- scripts/cluster.py, scripts/words.py: seeds are REUSED across standards with small edits at the ENDS:
  c2pnb163v1 == ECC2-163.seedE; c2pnb163v3 == ECC2K-95.seedP (ECC2-79.seedP = same but last nibble 1);
  c2tnb191v1 == ECC2-191.seedE; c2tnb239v1 == ECC2-238.seedE; c2tnb359v1 == ECC2-353.seedE (ECC2-97.seedE last nibble 8);
  sect113r2 = c2pnb163v1 with first byte d2->10 and last nibble 4->d; c2pnb163v2 vs ECCp-359.seedQ first nibble + last nibble;
  ECC2-109/ECC2-353/ECC2K-108/ECC2K-358 seedP & seedQ: middle (around MQ) identical, top 4-8 nibbles and bottom 1-8 nibbles retyped.
  ECC2-131.seedP prefix "b5555555555" (visibly hand-typed), secp160r2 "b99b99b099b323..." (hand-typed look).
- X9.62 binary 'a' coefficients look hand-typed too: c2tnb191v3 a=6c01074756099122221056911c77d77e77a777e7e7e77fcb,
  c2tnb239v3 a=01238774666a67766d6676f778e676b66999176666e687666d8766c66a9f (runs of 6/7 = keyboard mashing).
- scripts/corpus2.py: fillers (>=7 nibbles) NOT copied from any curve parameter or SHA-1 of any seed (+-2). Expected chance hits 0.2, got only '5555555'.
- scripts/typing_stats.py: unique fillers nibble chi2=20.7 (15df, ns); adjacent-repeat .075 vs .0625 (~+1.9 sigma); prefix has '4' deficit (chi2 29, p~.02). Not decisive.
- Anthropic article (data/agent/raw/anthropic/ecdsa-curve-origins.txt): X9.62 prime192v2/v3, prime239v1-3 ALREADY explained (lrand48()>>23, May 1997) -> dropped.
  B-163 seed unexplained there (possible extra target).

## 14:16-14:23 generator sweeps on MQ fillers (all NEGATIVE so far), planted controls pass
- scripts/lcg_lll.py: LLL (PARI qflll) recovery of lrand48 state from top-w-bit windows. Planted control
  (srand48(880000000), skip 37, lrand48()>>23 bytes, MQ inserted at nibble 7) -> recovered t exactly.
- scripts/run_lll.py: all 88 MQ seeds, insert & overwrite models, w=4 (hex char/call) and w=8 (byte/call), ends trimmed or not: 0 hits.
- scripts/lll_sweep.py: every bit alignment, w in {4,8,12,16,24,31(lrand48 words, top bit 0),32(mrand48)}: 0 hits on MQ fillers.
  CONTROL P-256 seed -> state found, srand48 t=871696354 = 1997-08-16 01:52:34 UTC (matches Anthropic article).
- Top-bit-zero signature for lrand48()>>17 words printed %08x: 126/264 (insert) word-top nibbles <8 -> ~50%, no signature.
- c/lcgbf.c: brute force of low windows [lo,lo+w) (lo+w<=32/34) for LCGs ANSI/BSD(1103515245,12345), MSVC(214013,2531011),
  Borland(22695477,1), lrand48 (lo+w<=34). w=4 and 8. Targets: data/targets{4,8}.txt (insert model F interior; overwrite prefix/suffix runs).
  220 jobs, 4 procs, ~2.5 min. Planted controls (MSVC rand()%16 nibbles; lrand48()&0xff bytes) both found.
  Real hits (data/lcgbf_hits.txt): 6 distinct, all on 40-bit runs at B=30-34 -> expected ~5 false positives. Checked by
  extension: none predicts the adjacent prefix (c2pnb163v2 MSVC lo=26: 1/11 prefix nibbles). => false positives.
- scripts/point_scan.py: Certicom seedP/seedQ last-nibble variants: published is first-valid-from-0 in only 1/8 -> last nibble is NOT a 0-based counter.

## 14:21 FIPS 186 DSA example SEED  ** exact result **
- 1994 FIPS 186 SEED d5014e4b...0427dbd (SHA-0, counter 38); FIPS 186-1/186-2 SEED ...0427dd3 (SHA-1, counter 105) = 1994 SEED + 22.
- scripts/dsa_scan.py: scanning SEED = 1994SEED + i (SHA-1), i=0..39: the ONLY q-prime seed is i=+22, with p found at counter=105
  -> 186-1 SEED = first SEED >= 1994 SEED (incrementing by 1) giving prime q under SHA-1. Reproduces published SEED, q, counter exactly.
  (So NIST re-derived the example for SHA-1 by incrementing the old SEED.) Chance: q-prime rate ~1/55 per seed; matching +22 exactly AND counter 105 is not chance.
- scripts/dsa_sha0_scan.py: 1994 SEED under SHA-0 valid (counter 38 reproduced). Previous valid seed below is -111 (...0427d4e), so
  1994 SEED is not first-valid after any round base (e.g. ...0427d00 -> first valid ...d08). Origin of 1994 SEED itself unexplained.
  LLL sweep (lrand48 all windows/alignments) on 1994 SEED, XSEED, KSEED, B-163 seed: no hits.

## 14:22-14:27 more tests
- scripts/inc_test.py: H_inc ("related seeds = common base, seed+=1 until valid") REJECTED: e.g. ECC2-109.seedP (..194e) vs ECC2-353.seedP (..1942):
  ECC2-109's point seed would already be valid at ..1942/..1943 (pattern 11.1..111.1.1 over 1942..194e). Edits are not a mechanical counter.
- scripts/lip_lll.py: FreeLIP zrandom (s*3^121 mod 2^107-1, 26-bit limbs) LLL at all 26 alignments; planted zrstarts(20000) control recovered;
  DSA 1994 SEED / XSEED / KSEED / B-163: no hits. (MQ fillers: only 88 bits < 107-bit state -> LLL underdetermined; would need small-seed brute force. NOT run.)
- c/randomsweep.c: BSD/glibc random() TYPE_3, init 16807 (glibc/FreeBSD) and 1103515245 (old BSD/SunOS), srandom(seed) for seed in
  [0,2e7) U [4.1e8,4.9e8) (t/2) U [8.2e8,9.8e8) (1995-12..2001-01), first 64 outputs, extraction o&0xf, o>>27, o&0xff, o>>23.
  Verified glibc srandom(1) -> 1804289383. Planted glibc nibble control found. Speed ~2e6 seeds/s/thread. (results below)
- SEC 2 v1 PDF gives sect163r1 seed 24b7b137c8a1|MQ|6fd0da2e5c (absent in OpenSSL). It does NOT verify (b != W; no +-300 or 1-nibble fix).
  Its filler F=24b7b137c8a16fd0da2e5c equals sect193r2's F=10b7b137c8a16fd0da2211 except first byte (24 vs 10) and last 3 nibbles,
  with MQ at k=12 vs k=5. Same pattern as sect131r1/r2 (same F, MQ moved 0 -> 11, last nibble +1).
- sect163r1 Gx = 0369979697ab43897789566789567f787a7876a654 -> visibly hand-typed ("789566789567f787a7876a654").

## 14:28 SECG / Certicom "MinghuaQu" construction: what is pinned down so far
Data: 89 MQ seeds = 66 Certicom ECC-challenge (1997, seedE/P/Q) + 10 X9.62 c2* + 12 SECG r-curves (+ sect163r1 from SEC 2 PDF; 4 WTLS duplicates).
1. Every seed (all 3 sources) = 40 hex chars containing the 18-char hex of ASCII "MinghuaQu" (4d696e676875615175) at a
   character (nibble) position k in 0..21; the "4-bit offset" seeds are simply odd k. Byte-oriented code would give even k only,
   so the seeds were built/edited as HEX TEXT.
2. The other 22 nibbles F (filler) are statistically uniform (chi2 20.7/15df; digit 5-9 fraction .312 vs .3125; no
   lrand48 / rand / random / FreeLIP signature found). Contrast: several X9.62 binary 'a' coefficients and SEC2 sect163r1 Gx are
   visibly hand-typed (z=+4..+7 excess of digits 5-9, runs like 7e7e7e77, 6789567).
3. Fillers are REUSED across curves and standards with edits at the two ends of the 40-char string:
   - identical: c2pnb163v1=ECC2-163.seedE, c2pnb163v3=ECC2K-95.seedP, c2tnb191v1=ECC2-191.seedE, c2tnb239v1=ECC2-238.seedE,
     c2tnb359v1=ECC2-353.seedE, ECC2-109.seedE=ECC2K-163.seedP  (X9.62 example curves ARE Certicom challenge curves/seeds)
   - last nibble changed: c2pnb163v3/ECC2-79.seedP, c2tnb359v1/ECC2-97.seedE, ECC2-97.seedQ/ECC2-238.seedQ, ECC2K-95.seedQ/ECC2-109.seedE,
     ECC2-109.seedP/ECC2-353.seedP, ECC2-109.seedQ/ECC2-353.seedQ
   - first nibble/byte + last nibble changed: sect113r2 (10..d) vs c2pnb163v1 (d2..4); c2pnb163v2 vs ECCp-359.seedQ; ECCp-79.seedE/ECCp-109.seedP;
     ECCp-79.seedQ/ECCp-191.seedP; ECCp-131.seedP/ECCp-239.seedP; ECCp-131.seedQ/ECCp-239.seedQ
   - 4-11 leading and 3-8 trailing nibbles retyped: ECC2-109/ECC2K-108/ECC2K-358 seedP & seedQ; ECC2-131/ECC2K-130 seedP & seedQ
     (ECC2-131.seedP prefix "b5555555555" = typed)
   - SAME filler, MQ MOVED: sect131r1 (k=0) / sect131r2 (k=11), F identical except last nibble 2->3;
     sect193r2 (k=5) / sect163r1 (k=12), F identical except first byte 10->24 and last 3 nibbles.
4. The edits are not a mechanical counter: last-nibble "first valid from 0" fails (1/8), "seed+=1 from a common base" fails.
5. First byte 0x10 in 5 SECG seeds (secp160r1, sect113r1, sect113r2, sect193r1, sect193r2) and 0x00 in all 4 secp112/128 seeds:
   deliberate (P[>=5 of 12 random seeds start with one given byte] ~ C(12,5)/256^5 ~ 7e-10); sect113r2 = c2pnb163v1 with first byte overwritten d2->10 (and last nibble 4->d).
Working description: "take a random-looking 22-hex-digit filler (origin unknown), insert 'MinghuaQu' in hex at some character position,
then make new candidate seeds by retyping a few hex digits at either end (often the first byte set to 10/00 for SECG) until the curve
(or point) is acceptable". This regenerates no seed by rule; it is a description of provenance/edit-distance relations.

## 14:26-14:29 results
- random() sweep (data/random_hits.txt, data/random_log.txt; 24 jobs, 4 procs, ~3 min): planted control found; 4 real "hits", all on
  minimal 40-bit runs (expected noise ~ a few). Extension check: none predicts the next/previous nibble or the other side of MQ -> false positives.
  => fillers are NOT glibc/BSD random() (16807 or 1103515245 init) seeded with t, t/2 (1995-12..2001-01) or seeds < 2e7, first 64 outputs,
  extraction o&15, o>>27, o&255, o>>23.
- data/secg_bytescan.txt (binary MQ curves; validity = same a, same cofactor, n prime):
  * moving MQ to every position 0..22 in the same filler: only the published k is valid in 21/22 seeds (sect113r1 also valid at k=3).
    Empirical validity rate p~1/100 (from last/first-byte scans), so expected ~2.4 valid positions before published k; saw 1 (P~0.3): uninformative.
  * first byte: 0x10 is first-valid-from-0x00 for sect113r2, sect193r1, sect193r2 but not sect113r1 (0x0d valid). With p~1/100 this is
    expected anyway; 0x10 is better explained as a FIXED design choice than as a counter.
  * last byte: published is the lowest valid value for sect193r1 (0x30, 1 of 4 valid) and sect193r2 (0x11, 1 of 3); not for sect113r1, sect131r1/r2.
  -> no mechanical counter rule found.
- scripts/lip_small.py: FreeLIP zrstarts(s), s in [0,600000), 64 limbs; streams limb&15, limb&255, and every 8-limb zrandomb(2^160)-style
  160-bit candidate; 10-nibble window match against all filler pieces. Planted (zrstarts(31337), 7 discards, MQ inserted) found.
  One real hit (s=318987, ECCp-89.seedE, 'acfc32c58c'), expected ~1.2 by chance; neighbours mismatch -> false positive. NEGATIVE.
- scripts/sha_strings.py: SHA-1 of dec(i), BE/LE4(i), "MinghuaQu"+i, "Minghua Qu"+i, i+"MinghuaQu", "MinghuaQu"||BE4(i),
  "MinghuaQu"||11-byte i, "Certicom"+i, 20-byte i (i<3e5): 10-nibble windows anywhere in digest vs fillers: only the planted control. NEGATIVE.
- 14:30 launched the LCG low-window brute force (c/lcgbf) and then random() sweep on full 160-bit targets B-163, DSA1994 SEED, XSEED, KSEED
  (data/ntargets*.txt, data/njobs.txt, data/nrjobs.txt).

## 14:32 hex-fragment reuse ALSO in other Certicom/SECG parameters (9-nibble window cross-index of all params; trivial 0/f runs ignored)
- secp160r1 Gx = 4a96b5688ef5|73284664698968c38bb913cbfc82 ; Certicom ECCp-131 P_x = 03df8|4a96b5688ef5|74fa91a32e197198a
  (ECCp-131 has h=1 so P_x = SHA-1 expansion of its seedP). 12 shared nibbles (48 bits); chance for any pair in corpus ~2e-7.
  => SECG secp160r1's base point x was made by editing the hex of the 1997 challenge point (prefix cut, tail retyped).
- ECCp-359 p ends ...58685c903f1643908ba9|69 ; ECCp-89 p = 01|58685c903f1643908ba9|55 (20 shared nibbles): challenge primes too
  were built by reusing hex fragments and retyping the last byte (until prime).
- ECC2-97.seedE = ECC2-353.seedE + 2, so b(ECC2-97) = low 97 bits of SHA1(seed353+2) = a block of b(ECC2-353): explains shared b substring.
- 14:31 c/lcgbf on full 160-bit targets (B-163, DSA1994 SEED, XSEED, KSEED; data/ntargets{4,8}.txt): 0 hits over all 220 window jobs.
  (The MQ-inserted planted seeds are not valid controls for full-run targets; added a full-run control PLANT_full = MSVC rand()&0xff x20 from
  srand(987654321): found at lo=16 w=8.)  => B-163/DSA seeds are not nibble/byte streams of ANSI/BSD, MSVC, Borland rand() or lrand48 low windows.

## 14:33 ** EXACT: FIPS 186 DSA example XSEED/XKEY = unseeded BSD/SunOS random() low bytes **
- c/randomsweep on full targets (data/nrandom_hits.txt, 23 MB because of periodicity): DSA_XSEED hit at pos=0, ext=2 (o & 0xff),
  init=1 (4.3BSD/SunOS srandom: state[i]=1103515245*state[i-1]+12345, discard 310), for EVERY seed == 1 (mod 512)
  (low byte of output depends only on seed mod 512 for this init). Natural reading: srandom(1) == the DEFAULT state of an unseeded
  4.3BSD/SunOS random() (the static randtbl is the srandom(1) state).
- scripts/bsd_random.py 1 -> "first 20 bytes random()&0xff: bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6" == XSEED (FIPS 186, 1994) == XKEY (186-1/186-2).
  160 of 160 bits; search space ~2^43 (2^32 seeds x 64 pos x 4 ext x 2 init) -> chance ~2^-117.
- Same generator does NOT give KSEED/KKEY 687a66d9..., SEED d5014e4b..., or B-163 85e25bfe...: scripts/bsd_classes.py (all 512 low-byte classes,
  first 30000 outputs, init 1) and srandom(1) stream 3M outputs x byte shifts 0..23, 1M outputs x nibble shifts: no hits.
- 14:34 running randomsweep for seeds [6.3e8,8.2e8) (1989-12..1995-12) and [3.15e8,4.1e8) (t/2), ext 0,1,3, both inits, on SEED/KSEED/B-163.
- scripts/bsd_fill.py: MQ fillers vs BSD random() (init=1) o&0xff for all 512 seed classes and o&0xf for all 32 classes, 30000 outputs each,
  10-nibble windows; planted control found; 0 real hits (chance ~0.04). NEGATIVE.
- scripts/g_func.py: FIPS 186 G(t,c) (SHA-0/1 compression, both t's) and SHA-1(v+-d) over XSEED/KSEED/SEED/B-163/x/k: only the expected x=G(t,XKEY) (sanity check). KSEED not derived from the others this way.
- 14:37 randomsweep on SEED/KSEED/B-163 for seeds [6.3e8,8.2e8) (1989-12..1995-12) and [3.15e8,4.1e8) (t/2), ext 0-3, both inits: 0 hits.
- 14:39 scripts/reproduce_exact.py (stdlib only, <0.1 s) reproduces both exact results (XSEED; 186-1 SEED +22 / counter 105 / q).
- "Unseeded" check: 4.3BSD random.c static randtbl begins 0x9a319039, 0x32d9c024 (from memory of the source); these are exactly consecutive
  words r[341], r[342] of the srandom(1) state computed here -> the default (never-seeded) BSD/SunOS random() state == srandom(1).
  glibc differs (16807 init; unseeded first output 1804289383), so the generating machine was a BSD-libc system (SunOS 4.x / Ultrix / 4.3BSD-derived).
- scripts/bsd_multibyte.py: srandom(1) stream 200k outputs, 16/24/32-bit-per-call extractions (BE/LE, low/high): no KSEED/SEED94/B-163/MQ-filler windows.
- scripts/drand_streams.py: unseeded drand48 (0x1234ABCD330E) 300k lrand48 outputs and srand48(0..3999) x 2000 outputs, all byte shifts 0-23
  and nibble shifts 0-27: one MQ-filler hit (srand48(2892), ECC2-238.seedP '930de1c511', expected ~0.8 by chance; neighbours mismatch) -> NEGATIVE.
- c/lrand_mid.c: srand48(t) for t in [6.3e8,9.8e8) (1989-12..2001-01) and [3.15e8,4.9e8) (t/2), 64 outputs, byte = (lrand48()>>sh)&0xff for
  sh=10..22 (the state-bit windows NOT covered by LLL-top or low-window brute force). Targets: KSEED, SEED94, B-163 (8 bytes), MQ insert-model
  fillers (6 bytes). Planted (t=760000000, sh=15, pos 30) found (recurs every 2^24 t, as expected). Real hits: 0. (~2 min, 4 procs)

## ROUND 1 SUMMARY (14:43)
EXACT:
 (a) FIPS 186 DSA example XSEED (1994) = XKEY (186-1/-2) = first 20 bytes of random()&0xff from an UNSEEDED 4.3BSD/SunOS random().
 (b) FIPS 186-1/-2 SEED = 1994 SEED + 22 = first increment of the 1994 SEED giving a prime q under SHA-1; p at counter 105 (matches).
     Repro: python3 scripts/reproduce_exact.py
DROPPED (already explained by Anthropic 2026-10): X9.62 prime192v2/v3, prime239v1-3; NIST P-*, B-233..B-571.
DESCRIBED, generator open: all MinghuaQu seeds (66 Certicom 1997 + 10 X9.62 c2* + 12 SECG + SEC2 sect163r1): see "construction" section.
 SECG rule as far as it goes: seed = F[:k] || hex("MinghuaQu") || F[k:], with F a 22-hex-digit filler and k a hex-CHARACTER position
 (odd k -> "4-bit offset"). Fillers are reused from the Certicom/X9.62 pool or between sibling SECG curves, with the first byte often
 overwritten (0x10 for 5 SECG seeds, 0x00 for the 4 secp112/128 seeds) and 1-3 trailing hex digits retyped until the curve is acceptable.
 The same hex-fragment editing appears in other Certicom parameters: secp160r1 Gx reuses 12 hex digits of ECCp-131's P_x;
 ECCp-359's p reuses 20 hex digits of ECCp-89's p; several X9.62 'a' values and sect163r1 Gx are keyboard-typed.
 No single rule regenerates the fillers; they pass uniformity tests and match no generator tried.
NEGATIVE on fillers (all with planted controls): lrand48/drand48 (LLL top windows w=4..32 all alignments; low windows brute force; mid windows
 time-seeded 1990-2001; unseeded and srand48(<4000) streams), rand() ANSI/BSD/MSVC/Borland (all 2^32 states, nibble & byte windows),
 BSD/glibc random() (time-seeded 1990-2001, t/2, seeds<2e7, all 512 low-byte classes long streams), FreeLIP (seeds<6e5), SHA-1 of counters/strings.
OPEN: DSA KSEED/KKEY 687a66d9... and the 1994 SEED d5014e4b...; B-163 seed (also negative here); MQ filler generator.

## 14:45 extra (after round summary)
- scripts/bsd_types.py: 4.3BSD random() with initstate TYPE_1/2/3/4 (deg 7/15/31/63), pointer-faithful simulation (control: TYPE_3 seed 1
  reproduces XSEED, asserted). All 512 seed classes x 20000 outputs, low byte (and low nibble for 32 classes): no KSEED / SEED94 / B-163 /
  MQ-filler windows. NEGATIVE (13.6 s).
- c/randomsweep, seeds [0, 2^20) (pids / small ints), first 20000 outputs, ext 0-3, both inits, on full DSA/B-163 targets and MQ-filler
  targets (data/pidjobs2.txt, data/pid2_hits.txt; 2m45s on 4 procs). Positive control: DSA_XSEED hit for all 2048 seeds == 1 mod 512 (init=1, ext=2).
  Other hits: 3, all on sect131r2's minimal 40-bit runs (pre/suf); expected false positives ~3 per job at this N -> noise. No KSEED/SEED94/B-163.
- 14:47 stopped experiments for the round.
- 14:48 scripts/fips_prng.py: FIPS 186 App.3 PRNG chain (x_j=G(t,XKEY), XKEY=1+XKEY+x_j) from XSEED and from KSEED, SHA-0/1, both t, 2000 steps,
  raw and mod q(1994/186-1): KSEED, SEED94, B-163 never appear. NEGATIVE.
- Extension check of the 3 sect131r2 hits in data/pid2_hits.txt: the adjacent digit is wrong in all three (pre: '1' vs '9'; suf: 'a','b' vs '3'/'2')
  -> false positives, as expected.
- (scripts/g_func.py now guarded so it can be imported.)
- 14:49 scripts/sha0_strings.py (sha0 asserted on "abc"; moved to scripts/sha0.py): SHA-0 and SHA-1 of i in [0,1e5) as decimal / BE4 / LE4 / BE20,
  and of {NIST, DSA, DSS, seed, SEED, KSEED, XSEED, NSA, test, example}+i (i<2000): no full match to KSEED, SEED94 or B-163. NEGATIVE.
- Round 1 experiments ended 14:50.
- 14:49 MQ fillers vs FIPS 186 App.3 G-PRNG chains (start XSEED, KSEED, 0, 1; SHA-0/1; both t; 3000 steps; 10-nibble windows anywhere): 0 hits
  (chance ~0.001). NEGATIVE. (inline script; same windows as scripts/bsd_fill.py)
- 14:50 scripts/sha_chain.py: is a filler's digits 2..9 (insert model) = digits 2..9 of SHA-1(z+d) for any published seed z (103 bases) and
  |d| <= 2e6? Planted (z0+777) found. ~11 distinct real hits vs ~8 expected by chance (8-digit key); spot checks (sect113r1, ECCp-359.seedP)
  diverge right after the 8 matched digits -> noise. Output data/sha_chain2_*.txt. NEGATIVE (46 s, 4 procs).
- Round 1 experiments ended 14:50.
- 14:53 BSD/glibc random() with srandom(t), t in 1993-01-01..1994-05-11 (725846400..768000000), first 1000 outputs, ext 0-3, both inits
  (ext 2/init 1 skipped: exhaustively covered by class analysis): 0 hits for KSEED / SEED94 / B-163 (data/dsa93_*.txt, 2m52s, 4 procs).
  NEGATIVE. Round 1 experiments ended.

## ROUND 2 (deadline 15:53)
## 14:58 constants checked against the archived documents (scripts/check_constants.py -> data/check_constants.txt)
Texts: data/agent/raw/fips/{fipspub186-legacy,fips186-1-csrc,fips186-2}.txt (pdftotext of nvlpubs/csrc PDFs), sec2-v1.txt, certicom/ch09.txt.
- FIPS 186 (1994-05-19) Appendix 5 "Example of the DSA" (printed page 18): SEED d5014e4b 60ef2ba8 b6211b40 62ba3224 e0427dbd, "counter was at 38",
  XSEED bd029bbe 7f51960b cf9edb2b 61f06f0f eb5a38b6, KSEED 687a66d9 0648f993 867e121f 4ddf9ddb 01205584 (OCR shows 867el21f).
- FIPS 186-1 (1998) Appendix 5 (page 19) and FIPS 186-2 (2000) Appendix 5 (page 21): SEED ...e0427dd3, "counter was at 105", XKEY = same bytes as XSEED, KKEY = KSEED.
- Independent of transcription: recomputing from the constants reproduces values printed in the documents:
  1994: SHA-0 p/q gen from SEED94 -> counter 38 and printed q; x = G_SHA0(t,XSEED) mod q = 6b2cd935...c8f8ef67 (printed); k = G_SHA0(t,KSEED) mod q = 79577ddc... (printed).
  186-1/-2: SHA-1 gen from SEED -> counter 105, printed q and p; x = 2070b322... and k = 358dad57... (printed).
  (1994 p is OCR-damaged in the scan, e.g. "d41Ia4a0", so it is checked only via q/x/k.)
- SEC 2 v1 (2000) text contains every SECG MinghuaQu seed exactly as in OpenSSL, plus sect163r1's 24b7b137...2e5c.
- Certicom challenge-2009 PDF text (appendix, "Original date: November 6, 1997") contains all 66 seedE/seedP/seedQ exactly as in data/agent/certicom.json.
=> No constant used in the exact results was typed from memory.

## 14:57 prior-work search (WebSearch, standard + extended)
Queries: 'FIPS 186 DSA example XSEED "bd029bbe" random'; 'FIPS 186 DSA example SEED d5014e4b origin'; 'FIPS 186 example XSEED unseeded BSD random()
srandom(1) test vector origin' (extended); '"MinghuaQu" seed SECG curves'; 'Certicom ECC challenge seed "Minghua Qu" X9.62 c2pnb163v1 seed analysis'.
- XSEED/SEED: only copies of the example (OpenSSL crypto/dsa/fips186a.txt mirrors; FIPS 186 Change Notice 1 at
  https://public.websites.umich.edu/~x509/ssleay/fip186/186chg-1.htm, which replaced App. 5 for SHA-1). Nobody explains where the SEED or
  XSEED came from, and no link to BSD random() was found. => the XSEED = unseeded-random() finding and the "SEED + 22" relation appear new.
- MinghuaQu: https://dissect.crocs.fi.muni.cz/standards/secg (DiSSECT) notes that the six secp112/128/160 r-seeds share a segment reading
  "MinghuaQu" and that the seed choice is unexplained (it cites a 2017 tweet; round-1 agent). https://bada55.cr.yp.to/vr.html discusses
  "verifiably random" generally. Nothing found on: sect* seeds also embedding MQ, X9.62 c2* seeds, Certicom challenge seeds embedding MQ,
  cross-standard seed reuse, nibble-offset insertion, or edited ends. => the family/reuse analysis appears new.

## 14:57 supervisor-requested cheap models
- KSEED / 1994 SEED in the unseeded random() stream right after XSEED (outputs 20-200), other extractions: ALREADY COVERED in round 1 and dropped:
  scripts/bsd_random.py searched the srandom(1) stream from output 0 to 3M with byte = (o>>sh)&0xff for every sh 0..23 (incl. >>8, >>16) and nibble
  shifts; scripts/bsd_multibyte.py searched 16/24/32-bit-per-call extractions (BE/LE, low/high) from output 0 to 200k. Pieces searched were the first
  and last 5 bytes, so a SEED made of stream bytes then incremented (as 186-1 did) would still have been caught by its first 5 bytes. No hit.
- Overwrite model for libc RNGs: already covered in round 1 (c/lcgbf + c/randomsweep 'pre'/'suf' targets = runs of the 40-nibble string on either
  side of the 18 overwritten nibbles; every seed has one side >= 11 nibbles; hits were checked ACROSS the 18-nibble gap, e.g. c2pnb163v2 1/11).
  LLL 'ovw' model in scripts/run_lll.py likewise used all non-MQ positions with the 18-position gap. Not re-run (per guidance: no more libc sweeps).
- NEW scripts/sha_chain_ovw.py: overwrite model with SHA-1: s = SHA-1(z+d) with MQ written over positions k..k+17, z any of 82 distinct published
  MQ seeds (including the seed's own neighbours z=s), |d| <= 1e6; aligned 8-nibble key on the longer side. Planted (z=sect233r1 seed, d=4242,
  MQ at 13) found. 2 real hits vs ~3.5 expected by chance; both diverge after 8-9 nibbles (be8df98b8626.. vs h 8df98b86|a2; 37a5b90a.. pos 26-34
  then '9' vs 'c') -> noise. NEGATIVE. (49 s, 5 procs)

## 15:00 chronology / reuse graph (scripts/chronology.py -> data/chronology.txt)
Edge = same MQ position and >= 24/40 equal nibbles, or same filler with MQ moved. 89 MQ seeds -> 17 components + 45 singletons.
- Cross-document components (all point from the 1997 challenge pool to X9.62 and SEC 2):
  * the challenge's binary curves ECC2-163/191/238/353 use EXACTLY the seeds of X9.62 c2pnb163v1, c2tnb191v1, c2tnb239v1, c2tnb359v1 (same curves);
  * X9.62 c2pnb163v3 == the challenge POINT seed ECC2K-95.seedP (ECC2-79.seedP differs in the last nibble);
  * X9.62 c2pnb163v2 == challenge point seed ECCp-359.seedQ with first and last nibble retyped;
  * SEC 2 sect113r2 == c2pnb163v1 / ECC2-163.seedE with first byte -> 10 and last nibble retyped. This is the only SECG seed linked to the
    older pool; it fixes direction 1997/98 -> 2000.
- Within SEC 2 only: sect131r1/r2 and sect193r2/sect163r1 (same filler, MQ moved). 10 of 13 SECG seeds and 4 of 10 X9.62 seeds are singletons.
- Within the challenge: reuse links small (exercise) and large (level II) sizes, not neighbours in size: ECC2-97<->ECC2-353 (seedE),
  ECC2-109<->ECC2-353 (seedP and seedQ), ECC2K-108<->ECC2K-358, ECC2-97.seedQ<->ECC2-238.seedQ, ECCp-79<->ECCp-191, ECCp-131<->ECCp-239,
  ECCp-79.seedE<->ECCp-109.seedP. Roles cross freely: a curve seed in one is a point seed in another (ECC2-109.seedE = ECC2K-163.seedP;
  ECCp-79.seedE ~ ECCp-109.seedP; X9.62 curve seed c2pnb163v3 = challenge point seed). Reading: one pool of MQ strings, drawn on for any
  purpose and retyped at the ends when a candidate failed. No order by size or date can be read from the graph beyond 1997 pool -> X9.62/SEC 2.
- Koblitz challenge curves (ECC2K-*) have no seedE (fixed a,b) but their point seeds sit in the same components as the random curves.

## 14:58 REPORT.md written (Parts A exact DSA, B MinghuaQu construction, C negatives table, Open). Claims re-checked against NOTES/data.

## 14:59 sect163r1 explained (KNOWN, documented)
- scripts/sect163r1_check.py: bit-reversing the 163-bit X9.62 W from S=24b7b137...2e5c gives SEC 2's b exactly (W itself does not).
- Prior documentation: SEC 2 v2 (data/agent/raw/sec2/sec2-v2.txt, §3.2, "Page 17 of 33") says: "for historical reasons the method used to
  generate E from S differs slightly from ... ANSI X9.62. Specifically the coefficient b produced from S is the reverse of the coefficient that
  would have been produced by the method described in ANSI X9.62." So this is a reproduction of a documented quirk, not a new finding.
  sect163r1's seed is therefore genuine, and its filler link to sect193r2 (MQ moved 5->12, ends retyped) stands.
- 15:00 SEC 2 v2 §2.1/§3.1 (sec2-v2.txt lines 211-214, 670-673) states the r-parameters "were chosen by repeatedly selecting a random seed and
  counting the number of points ... until appropriate parameters were found" and that binary a is "random or a = 1". The reuse/edit graph
  (seeds recycled from the 1997 challenge and X9.62, ends retyped) shows "selecting a random seed" was in practice editing existing hex strings.
- 15:01 scripts/reuse_null.py (null control for the reuse graph): keep each seed's MQ position, randomise its 22 filler nibbles, 200 trials.
  Null edges: mean 0.57, max 4; over 200 trials 113 null edges at 24-25/40, 1 at 26, 0 moved-MQ. Real: 26 edges (22 at 27-39/40, one at 24, one at 26, 2 moved-MQ). Edges >= 27/40 are individually significant
  (P per same-k pair ~ C(22,7..)/16^.. < 1e-3 x ~400 pairs). The 24-26/40 edges (ECC2K-108/358 family, ECC2-131/ECC2K-130.seedP) are weaker one
  by one, but their equal nibbles form one contiguous block next to MQ, while chance agreements would be scattered; they also sit in components
  with strong edges.
- 15:03 Verified (no longer from memory): 4.3BSD /usr/src/lib/libc/gen/random.c (https://www.tuhs.org/cgi-bin/utree.pl?file=4.3BSD/usr/src/lib/libc/gen/random.c)
  says "Initially, everything is set up as if from : initstate( 1, &randtbl, 128 );", srandom fills state[i] = 1103515245*state[i-1] + 12345,
  discards 10*rand_deg outputs, and randtbl starts 0x9a319039, 0x32d9c024, 0x9b663182, 0x5da1f342, 0xde3b81e0, 0xdf0a6fb5.
  Computed srandom(1) state (31 words), rotated by 28, begins with exactly these 6 words. => unseeded 4.3BSD random() == srandom(1): confirmed.
- 15:02 two more primary-source searches ('ANSI X9.62 draft 1997 example curves seed ... how seeds chosen'; 'FIPS 186 1994 DSA example KSEED
  XSEED generated SunOS random() NIST test vectors history'): only DiSSECT, BADA55, the Anthropic article, and copies of fips186a.txt (OpenSSL's copy
  credits Wei Dai for the SHA-1 version). No X9F1 drafts or account of the KSEED/SEED origin online. Nothing new.
- 15:02 Round 2 work complete: REPORT.md written; constants verified; prior work recorded; cheap models (overwrite/SHA-1 neighbours) negative;
  chronology and null control done; sect163r1 explained (documented quirk). STATUS set to stuck/15% for the open parts.
- 15:03 scripts/bsd_reversed.py: KSEED / SEED94 in the unseeded random() stream (1e6 outputs, byte shifts 0-23) with byte order reversed
  (whole 20 bytes, per-32-bit word LE, nibble-swapped bytes); XSEED forward asserted as control. No hits. (Last check within the XSEED mechanism.)
- 15:04 scripts/typed_control.py: control for the "keyboard-typed" claim. 59 SHA-1-derived values (binary b's, Certicom U_x/V_x): max z(5-9 excess) = 2.42.
  Clearly above it: X9.62 c2tnb239v3.a z=7.2, sect163r1 Gx 6.5, c2tnb359v1.a 5.4, c2tnb191v1.a 4.0. Borderline (2.5-2.9, could be chance among ~50 values):
  c2tnb239v1/v2.a, secp112r1/secp160r1 Gx, c2tnb191v3.a (the last has visible runs 7e7e7e77 anyway).
- 15:04 WTLS curve 7 (side note): WAP WTLS spec 05-Nov-1999 (data/agent/raw/other/wtls.txt, page 84-85 of 96) defines assigned number 7 with
  p = FFFFFFFF...7FFFFFFF and S = 1053CDE4 2C14D696 E6768756 1517533B F3F83345, i.e. secp160r1. OpenSSL ec_curve.c maps
  NID_wap_wsg_idm_ecid_wtls7 to _EC_SECG_PRIME_160R2 (secp160r2, seed b99b99b0...). Either OpenSSL mislabels it or a later WTLS revision
  changed curve 7 (not checked; only the 1999 spec was available). Irrelevant to the seed origins; the seeds are the same family either way.

## 15:05 prior work, round 2 follow-up (DiSSECT citations followed)
- DiSSECT x962 page: no mention of the c2*/prime v2-v3 seeds, MinghuaQu or Certicom.
- DiSSECT secg page cites a 2017 tweet (@BRIAN_____) and a bitcointalk thread: https://bitcointalk.org/index.php?topic=289795.msg3183975
  In that 2013 thread BurtW relays SECG chair Dan Brown: "I noticed that some of the seeds look similar to each other, and had very non-random
  looking hex representations"; "a large middle portion of some of the seeds contain the string" MinghuaQu; "I would not be surprised if the
  remainder of the seeds also had some meaning"; "John Goyo recalls that two former employees generated the domain parameters ... not sure if we
  have maintained all the archives." (via WebFetch summary; quotes as returned by the fetch tool)
  => The SIMILARITY of SECG seeds and the embedded name were noticed by SECG itself in 2013, qualitatively. New here: the quantified reuse graph
  with null control, the link back to the 1997 Certicom challenge and X9.62 seeds, nibble-position insertion, edited ends, and the same editing in
  base points and challenge primes.
- 15:06 scripts/meaning_scan.py (prompted by Brown's "remainder of the seeds also had some meaning"): the non-MQ digits contain no more ASCII
  (both nibble alignments, forward/reversed) and no more decimal-only stretches than random fillers at the same positions (300-trial null:
  #runs P=0.55, longest P=0.44, decimal digits P=0.34). The only 4+ char runs are 'UUUUU' (= the typed b5555555555) and chance strings ('B4jP', 'frrw').
  => no second embedded word or number found.
