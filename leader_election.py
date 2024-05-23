# Fontes utilizadas:
# https://en.wikipedia.org/wiki/Leader_election

# Esse código funciona para uma topolgia em anel de tamanho exatamente 3
from random import randint
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD

if __name__ == '__main__':
    # Obter informações da rede
    rank = comm.Get_rank()

    prioridade = randint(0, 10000)

    # Criação da topologia em anel
    if rank == 0:
        vizinho_esquerdo = 2
        vizinho_direito = 1
    elif rank == 1:
        vizinho_esquerdo = 0
        vizinho_direito = 2
    else:
        vizinho_esquerdo = 1
        vizinho_direito = 0
       
    # Inicializar líder desconhecido
    lider_rank = -1
    lider_prioridade = -1 
    
    # Sincroniza as instâncias
    print(f"Instância {str(rank)} inicializada com prioridade {str(prioridade)}.")
    comm.Barrier()
    
    if rank == 0:
        print(f"Instância {str(rank)} é o melhor candidato, pois tem prioridade {str(prioridade)}")
        sleep(0.2)
        # Se envia como melhor candidato para seu vizinho direito
        comm.send((rank, prioridade), dest=vizinho_direito, tag=42)
        # Espera receber o resultado do vizinho esquerdo
        (lider_rank, lider_prioridade) = comm.recv(source=vizinho_esquerdo, tag=42)
        # Envia o resultado da eleição para o vizinho direito
        comm.send((lider_rank, lider_prioridade), dest=vizinho_direito, tag=42)
        
    else:
        # Espera receber do vizinho da esquerdo o melhor candidato até então
        (melhor_rank, melhor_prioridade) = comm.recv(source=vizinho_esquerdo, tag=42)
        # Verificar se a instância atual é o melhor candidato
        if melhor_prioridade < prioridade:
            melhor_rank = rank
            melhor_prioridade = prioridade
            print(f"O melhor candidado é na verdade a instância {str(rank)}, pois tem prioridade {str(prioridade)}")
        else:
            print(f"A instância {str(melhor_rank)} ainda é o melhor candidato, pois sua prioridade é maior que a prioridade da instância {str(rank)}.")
            # Envia candidato ao vizinho da direita
            sleep(0.2)
            comm.send((melhor_rank, melhor_prioridade), dest=vizinho_direito, tag=42)
            # Espera resultado do vizinho da esquerda
            (leader_rank, leader_priority) = comm.recv(source=vizinho_esquerdo, tag=42)
        # Envia líder
        if rank != 2:
            comm.send((leader_rank, melhor_prioridade), dest=vizinho_direito, tag=42)

    # Exibir resultado da eleição de líder
    print(f"A instância {str(rank)} escolheu como líder a instância {str(leader_rank)}")

