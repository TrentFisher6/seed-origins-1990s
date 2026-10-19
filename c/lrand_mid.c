// srand48(t) for t in [t0,t1): lrand48 outputs o_k (k<N); bytes (o>>sh)&0xff, sh in [shlo,shhi]. Targets: lines "label b0 b1 ..." (bytes).
// Report target runs found consecutively (>= all listed bytes). Usage: lrand_mid t0 t1 N shlo shhi targets
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXT 4096
typedef struct { char lab[64]; int L; uint8_t v[64]; } T;
T t[MAXT]; int nt; int head[1<<16], nxt[MAXT];
int main(int argc, char **argv) {
  uint64_t t0 = strtoull(argv[1],0,0), t1 = strtoull(argv[2],0,0); int N = atoi(argv[3]), shlo = atoi(argv[4]), shhi = atoi(argv[5]);
  FILE *f = fopen(argv[6], "r"); char line[4096];
  while (fgets(line, sizeof line, f)) { char *p = strtok(line, " \n"); if (!p) continue; strncpy(t[nt].lab, p, 63); t[nt].L = 0;
    while ((p = strtok(0, " \n")) && t[nt].L < 64) t[nt].v[t[nt].L++] = (uint8_t)atoi(p); nt++; }
  for (int i = 0; i < 65536; i++) head[i] = -1;
  for (int i = 0; i < nt; i++) { int key = (t[i].v[0] << 8) | t[i].v[1]; nxt[i] = head[key]; head[key] = i; }
  uint32_t o[256]; long hits = 0;
  for (uint64_t tt = t0; tt < t1; tt++) {
    uint64_t x = (tt << 16) | 0x330E;
    for (int k = 0; k < N; k++) { x = (0x5DEECE66DULL * x + 0xB) & 0xFFFFFFFFFFFFULL; o[k] = (uint32_t)(x >> 17); }
    for (int sh = shlo; sh <= shhi; sh++)
      for (int k = 0; k + 1 < N; k++) {
        int key = (((o[k] >> sh) & 0xff) << 8) | ((o[k+1] >> sh) & 0xff);
        for (int i = head[key]; i >= 0; i = nxt[i]) { int ok = 1;
          for (int j = 2; j < t[i].L; j++) if (k + j >= N || ((o[k+j] >> sh) & 0xff) != t[i].v[j]) { ok = 0; break; }
          if (ok) { printf("HIT %s t=%llu sh=%d pos=%d\n", t[i].lab, (unsigned long long)tt, sh, k); hits++; fflush(stdout); } }
      }
  }
  fprintf(stderr, "done %llu..%llu hits=%ld\n", (unsigned long long)t0, (unsigned long long)t1, hits);
}
