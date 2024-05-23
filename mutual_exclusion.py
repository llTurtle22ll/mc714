# Fontes utilizadas:
# https://pt.wikipedia.org/wiki/Rel%C3%B3gios_de_Lamport

from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD

class LamportClockWithMutualExclusion:
    def __init__(self, rank):
        self.rank = rank
        self.clock = 0
        self.queue = []

    def receive(self):
        # Espera receber uma mensagem de alguma instância no formato (rank, clock)
        message_received = comm.recv(source=MPI.ANY_SOURCE, tag=42)
        # Enfileira a mensagem recebida
        self.queue.append(message_received)
        print(f"Instância {self.rank} recebeu mensagem da instância {message_received[0]} com clock {message_received[1]}")

    def send(self):
        # Envia uma mensagem para a instância 0
        self.clock += 1
        print(f"Instância {self.rank} enviou uma mensagem com o clock {self.clock}")
        sleep(0.2)
        comm.send((self.rank, self.clock), dest=0, tag=42)


if __name__ == '__main__':
    # Instancia a classe
    clock = LamportClockWithMutualExclusion(
        comm.Get_rank()
    )

    # Sincronizar os processos
    print(f"Instância {clock.rank} inicializada.")
    comm.Barrier()

    # Instância 0 recebe e processa mensagens
    if clock.rank == 0:
        while True:
            # Espera receber 5 requisições para ter disputa na região crítica
            while len(clock.queue) < 5:
                print(f"Intância {str(clock.rank)} está esperando 5 mensagens... Fila: {str(clock.queue)}")
                clock.receive()
            
            # FIFO
            message_to_send = clock.queue[0]
            # --------------- INÍCIO DA REGIÃO CRÍTICA --------------- #
            # Concede acesso à região crítica para a mensagem escolhida
            print(f"[!] Mensagem da instância {str(message_to_send[0])} está na região crítica.")
            delay = randrange(10, 50)
            contador = 0
            
            # Instância 0 continua recebendo mensagens mesmo quando uma mensagem já está na região crítica
            # Simula uma mensagem sendo executado na região crítica
            while True:
                while not comm.iprobe(source=MPI.ANY_SOURCE, tag=42):
                    sleep(0.2)
                    contador += 1
                    if contador % 5 == 0:
                        # Percentual de conclusão do Mensagem
                        print(f"Mensagem {str(round(contador/delay * 100))}% concluído")
                    if contador >= delay:
                        break
                if contador < delay:
                    # Recebeu uma mensagem enquanto está na região crítica
                    clock.receive()
                # Mensagem acabou de ser excecutado e a região crítica foi liberada
                else:
                    break
        
            clock.queue.remove(message_to_send)
            print(f"[!] Mensagem da instância {str(message_to_send[0])} saiu da região crítica.")
            # --------------- FIM DA REGIÃO CRÍTICA --------------- #
         
    # Demais instâncias enviam mensagens
    else:
        while True:
            delay = randrange(5, 15)
            # Esperam esse tempo
            sleep(delay)
            # Envia uma nova mensagem para a instância 0
            clock.send()