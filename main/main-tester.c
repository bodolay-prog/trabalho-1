#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <time.h>

// N = numero de filhos por execucao
#define N 8

#define ITER 20000000ULL

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

static void carga_trabalho(void) {
    volatile unsigned long long acc = 0;
    for (unsigned long long i = 0; i < ITER; i++) {
        acc += i * i;
    }
}

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    int run_id = argc > 1 ? atoi(argv[1]) : 0;

    pid_t criados[N];
    double t0 = now_ms();

    for (int i = 0; i < N; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            exit(1);
        } else if (pid == 0) {
            carga_trabalho();
            double t_fim = now_ms();
            // FILHO,run_id,indice_criacao,pid,tempo_desde_t0_ms
            printf("FILHO,%d,%d,%d,%.4f\n", run_id, i, getpid(), t_fim - t0);
            exit(0);
        } else {
            criados[i] = pid;
        }
    }

    for (int rank = 0; rank < N; rank++) {
        int status;
        pid_t p = wait(&status);
        double t_wait = now_ms();
        int idx_criacao = -1;
        for (int j = 0; j < N; j++) {
            if (criados[j] == p) { idx_criacao = j; break; }
        }
        // WAIT,run_id,rank_de_termino(0=primeiro a terminar),indice_de_criacao,pid,tempo_ms
        printf("WAIT,%d,%d,%d,%d,%.4f\n", run_id, rank, idx_criacao, p, t_wait - t0);
    }

    return 0;
}
