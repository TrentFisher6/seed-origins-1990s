// BSD/glibc random() TYPE_3 sweep: srandom(seed) for seed in [s0,s1); outputs o_k (31-bit), first N.
// Extraction e: 0: o&0xf  1: o>>27  2: o&0xff  3: o>>23 . init: 0 = 16807 (glibc/FreeBSD), 1 = 1103515245 LCG (old BSD/SunOS)
// targets file as for lcgbf (values per extraction width). Usage: randomsweep s0 s1 N ext init targets
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXT 4096
typedef struct { char lab[64]; int L; uint32_t v[64]; } T;
T t[MAXT]; int nt; int head[1<<16], nxt[MAXT];
int main(int argc, char **argv) {
  uint64_t s0 = strtoull(argv[1],0,0), s1 = strtoull(argv[2],0,0); int N = atoi(argv[3]), e = atoi(argv[4]), init = atoi(argv[5]);
  FILE *f = fopen(argv[6], "r"); char line[4096];
  while (fgets(line, sizeof line, f)) { char *p = strtok(line, " \n"); if (!p) continue; strncpy(t[nt].lab, p, 63); t[nt].L = 0;
    while ((p = strtok(0, " \n")) && t[nt].L < 64) t[nt].v[t[nt].L++] = atoi(p); nt++; }
  int w = (e < 2) ? 4 : 8, K = 16 / w;
  for (int i = 0; i < 65536; i++) head[i] = -1;
  for (int i = 0; i < nt; i++) { uint32_t key = 0; for (int j = 0; j < K; j++) key = (key << w) | t[i].v[j]; nxt[i] = head[key]; head[key] = i; }
  uint32_t *r = malloc(sizeof(uint32_t) * (N + 400)); uint32_t *o = malloc(sizeof(uint32_t) * (N + 8)); long hits = 0;
  for (uint64_t sd = s0; sd < s1; sd++) {
    int32_t x = (int32_t)(uint32_t)sd; if (init == 0 && x == 0) x = 1;
    r[0] = (uint32_t)x;
    for (int i = 1; i < 31; i++) {
      if (init == 0) { int32_t hi = (int32_t)r[i-1] / 127773, lo = (int32_t)r[i-1] % 127773; int32_t word = 16807 * lo - 2836 * hi; if (word < 0) word += 2147483647; r[i] = word; }
      else r[i] = 1103515245u * r[i-1] + 12345u;
    }
    for (int i = 31; i < 34; i++) r[i] = r[i-31];
    for (int i = 34; i < 344 + N; i++) r[i] = r[i-31] + r[i-3];
    for (int k = 0; k < N; k++) { uint32_t ov = r[k+344] >> 1;
      o[k] = e == 0 ? (ov & 0xf) : e == 1 ? (ov >> 27) : e == 2 ? (ov & 0xff) : (ov >> 23); }
    for (int k = 0; k + K <= N; k++) {
      uint32_t key = 0; for (int j = 0; j < K; j++) key = (key << w) | o[k+j];
      for (int i = head[key]; i >= 0; i = nxt[i]) { int ok = 1;
        for (int j = 0; j < t[i].L; j++) if (k + j >= N || o[k+j] != t[i].v[j]) { ok = 0; break; }
        if (ok) { printf("HIT %s seed=%llu pos=%d ext=%d init=%d\n", t[i].lab, (unsigned long long)sd, k, e, init); hits++; fflush(stdout); } }
    }
  }
  fprintf(stderr, "done %llu..%llu e=%d init=%d hits=%ld\n", (unsigned long long)s0, (unsigned long long)s1, e, init, hits);
}
