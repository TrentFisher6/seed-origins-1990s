// Brute-force low-window LCG: find states S (mod 2^B, B=lo+w) such that window bits [lo,lo+w) of
// successive states step^1(S), step^2(S),... equal a target run. Usage: lcgbf a c lo w targets.txt
// targets.txt: lines "label v0 v1 v2 ..." (decimal values, each < 2^w)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXT 4096
#define MAXL 64
typedef struct { char lab[64]; int L; uint32_t v[MAXL]; } T;
T t[MAXT]; int nt;
int head[1<<16], nxt[MAXT];
int main(int argc, char **argv) {
  uint64_t a = strtoull(argv[1],0,0), c = strtoull(argv[2],0,0);
  int lo = atoi(argv[3]), w = atoi(argv[4]);
  FILE *f = fopen(argv[5], "r"); char line[4096];
  while (fgets(line, sizeof line, f)) {
    char *p = strtok(line, " \n"); if (!p) continue;
    strncpy(t[nt].lab, p, 63); t[nt].L = 0;
    while ((p = strtok(0, " \n")) && t[nt].L < MAXL) t[nt].v[t[nt].L++] = atoi(p);
    nt++;
  }
  int B = lo + w; uint64_t mask = (B >= 64) ? ~0ULL : ((1ULL << B) - 1), wm = (1u << w) - 1;
  int K = (16 + w - 1) / w; // number of outputs forming a >=16-bit key
  for (int i = 0; i < (1<<16); i++) head[i] = -1;
  for (int i = 0; i < nt; i++) { uint32_t key = 0; for (int j = 0; j < K; j++) key = (key << w) | t[i].v[j]; key &= 0xFFFF; nxt[i] = head[key]; head[key] = i; }
  long hits = 0;
  for (uint64_t S = 0; S <= mask; S++) {
    uint64_t x = S; uint32_t key = 0;
    for (int j = 0; j < K; j++) { x = (a * x + c) & mask; key = (key << w) | ((x >> lo) & wm); }
    key &= 0xFFFF;
    for (int i = head[key]; i >= 0; i = nxt[i]) {
      uint64_t y = S; int ok = 1;
      for (int j = 0; j < t[i].L; j++) { y = (a * y + c) & mask; if (((y >> lo) & wm) != t[i].v[j]) { ok = 0; break; } }
      if (ok) { printf("HIT %s lo=%d w=%d S=%llx\n", t[i].lab, lo, w, (unsigned long long)S); hits++; }
    }
    if (S == mask) break;
  }
  fprintf(stderr, "lo=%d w=%d done hits=%ld\n", lo, w, hits);
  return 0;
}
