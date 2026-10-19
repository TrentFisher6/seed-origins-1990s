# Where some 1990s "random" crypto constants came from

On 2026-10-16 Anthropic [showed](https://www.anthropic.com/research/ecdsa-curve-origins) that the NIST P-curve seeds of 1997–98 are bytes from `lrand48()` seeded with the Unix time. That raised an obvious question: what about the other unexplained "random" values in standards of the same era? This repo answers part of it, with code that reproduces every claim.

## Findings

### 1. The FIPS 186 DSA example key comes from an unseeded BSD `random()`

The worked DSA example in FIPS 186 (1994), Appendix 5, derives its private key from a 160-bit seed. FIPS 186 calls it XSEED, and FIPS 186-1 and 186-2 call it XKEY:

    bd029bbe 7f51960b cf9edb2b 61f06f0f eb5a38b6

These are the **first 20 values of `random() & 0xff` from a 4.3BSD-family libc in a program that never called `srandom()`.**

```c
for (i = 0; i < 20; i++) printf("%02x", random() & 0xff);   /* on 4.3BSD / SunOS 4 */
```

- All 160 bits match. The search that found this covered about 2^43 candidates, so the chance of an accidental match is about 2^-117.
- 4.3BSD's `random.c` starts in the state of `initstate(1, …)`, and its static `randtbl` matches the state we compute. So this is exactly what an unseeded program produces.
- glibc's default state is different. The example was therefore made on a BSD-derived Unix, most likely SunOS 4.

### 2. The FIPS 186-1 example SEED is the 1994 SEED + 22

FIPS 186 (1994) printed `SEED = d5014e4b … e0427dbd` (counter 38, SHA-0). When the example was redone for SHA-1 in FIPS 186-1 and 186-2, the published SEED became `… e0427dd3` (counter 105). That is the **first value at or above the old SEED, counting up by 1, for which the Appendix 2 procedure gives a prime q under SHA-1**. The 22 seeds before it give composite q. In other words, NIST kept the old seed and incremented it until it worked.

### 3. The "MinghuaQu" seeds were hand-edited from a reused pool

Eighty-nine seeds contain the ASCII hex of `MinghuaQu`:
- the Certicom ECC Challenge of 1997 (66 seeds)
- ten ANSI X9.62 binary example curves
- 13 SEC 2 r-curves, such as secp112r1, secp160r1 and sect193r1

DiSSECT and others had noted the name inside the secp112/128/160 seeds, and SECG's chair said in 2013 that some seeds "look similar to each other". This repo quantifies that and traces it further:

- **The structure.** Each seed is a 22-hex-digit filler with `MinghuaQu` inserted at an arbitrary *hex-character* position. In 45 of 82 distinct seeds that position is odd, so the seeds were edited as hex text, not generated as bytes.
- **The reuse.** Fillers are reused across documents and years, with a few digits retyped at the ends:
  - The 1997 challenge curves ECC2-163/191/238/353 *are* X9.62 c2pnb163v1, c2tnb191v1, c2tnb239v1 and c2tnb359v1.
  - SEC 2's sect113r2 (2000) is X9.62 c2pnb163v1 with its first byte and last digit changed.
  - Random fillers at the same positions give 0.57 such links on average (maximum 4 in 200 trials). The real seeds give **26**.
- **The same editing elsewhere.** Hex fragments are also shared between other parameters: secp160r1's base-point x shares 12 hex digits with the 1997 challenge point ECCp-131 (chance about 2e-7), and the challenge prime ECCp-359 ends with 20 digits of ECCp-89's prime.
- **No known generator behind the fillers.** The fillers themselves look uniformly random. No 1990s libc PRNG, FreeLIP, or SHA-1-of-counter scheme we tried regenerates them (see the ruled-out table in [REPORT.md](REPORT.md)).

SEC 2 describes its r-curves as chosen "by repeatedly selecting a random seed and counting the number of points … until appropriate parameters were found". In practice a "random seed" was often an existing string from the 1997 pool with a few digits retyped. That doesn't break any of these curves. It does mean the seeds give weaker "verifiably random" assurance than a reader of the standard would assume, because hand-edited candidates leave the generator free to choose. That freedom is exactly the concern of [BADA55](https://bada55.cr.yp.to/vr.html). Most of these curves are obsolete, so the interest here is historical and methodological.

## Still unexplained

- The DSA example's KSEED/KKEY (`687a66d9…`) and the 1994 SEED. Neither occurs in the unseeded `random()` stream or in any generator we tried.
- Where the MinghuaQu filler digits came from: an internal Certicom RNG, typed hex, or something else.

## Reproduce

The exact results need only Python 3 and its standard library:

```sh
python3 scripts/reproduce_exact.py        # finding 1 and finding 2
```

To check every constant against the primary documents, first fetch them. The documents aren't redistributed here; fetching needs `curl` and `pdftotext`.

```sh
./fetch_sources.sh
python3 scripts/check_constants.py        # also recomputes the printed x, k, q, p of the DSA examples
```

For finding 3, and for the negative sweeps (the C tools, the LLL code and the Python scripts), see the "Reproduction" section of [REPORT.md](REPORT.md).

One known quirk: `scripts/verify.py` prints `False` for the NIST binary curves (sect233r1/283r1/409r1/571r1, wtls11). The plain X9.62 check used there doesn't apply to those curves, which this work doesn't study.

## How this was done

The investigation was run by AI research agents (Claude Opus 5.5 in Claude Code), one agent per problem, in time-boxed rounds with a reviewer agent between rounds. The setup was inspired by the Anthropic result above.

- The agents wrote the sweeps, used planted controls for every search, and checked constants against archived copies of the standards.
- A human set up the project, and the DSA result was independently re-implemented and confirmed.
- Treat the MinghuaQu analysis as carefully checked by machine but **not yet reviewed by a domain expert**. Corrections are welcome as issues.

The full technical report is [REPORT.md](REPORT.md), and the raw lab notebook, with timestamps and dead ends, is [NOTES.md](NOTES.md).

## Prior work

- Anthropic, [Origins of the NIST ECDSA curve seeds](https://www.anthropic.com/research/ecdsa-curve-origins) (2026), and Filippo Valsorda's [seed bounty](https://words.filippo.io/seeds-solved/).
- DiSSECT, [SECG standard page](https://dissect.crocs.fi.muni.cz/standards/secg).
- Bernstein et al., [BADA55: how to manipulate curve standards](https://bada55.cr.yp.to/vr.html).
- The [bitcointalk thread](https://bitcointalk.org/index.php?topic=289795.msg3183975) (2013) relaying SECG chair Dan Brown's comments on the seeds.

As far as we could find, no earlier publication links the DSA example values to BSD `random()`, or describes the cross-document reuse of the MinghuaQu seeds. If you know of one, please open an issue.

## Layout and license

| Path | Contents |
|---|---|
| `scripts/` | Python analysis and sweeps |
| `c/` | C brute-force tools |
| `data/` | Parsed parameters and sweep outputs |
| `data/openssl/ec_curve.c` | From OpenSSL, under the Apache License 2.0 |

The code in this repo is under the MIT license.
