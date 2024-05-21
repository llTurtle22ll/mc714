# Fontes utilizadas:
# https://mpi4py.readthedocs.io/en/stable/tutorial.html
# https://github.com/arthurdouillard/algo_with_mpi/blob/master/lamport_clock.py
# https://pt.wikipedia.org/wiki/Rel%C3%B3gios_de_Lamport

from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD

class LamportClock:
  def __init__(self, rank):
    self.rank = rank
    self.clock = 0

  def receive(self):
    # Espera receber um clock de alguma fonte
    clock_received = comm.recv(source=MPI.ANY_SOURCE, tag=42)
    # Se o clock recebido for maior que o atual, atualiza o clock atual
    # se não, mantém o clock
    if clock_received + 1 > self.clock:
      self.clock = clock_received + 1
      print(f"Instância {self.rank} recebeu mensagem e atualizou seu clock para {self.clock}")
    else:
      print(f"Instância {self.rank} recebeu mensagem e manteve seu clock em {self.clock}")

  def send(self):
    # Envia seu clock para a instância 0
    self.clock += 1
    print(f"Instância {self.rank} enviou uma mensagem com o clock {self.clock}")
    sleep(0.2)
    comm.send(self.clock, dest=0, tag=42)


if __name__ == '__main__':
  # Instancia a classe
  clock = LamportClock(
    comm.Get_rank()
  )

  # Sincronizar os processos
  print(f"Instância {clock.rank} inicializada.")
  comm.Barrier()

  while True:
    # Instância 0 ouve e sincroniza os clocks
    if clock.rank == 0:
      clock.receive()
    else:
      # Demais instâncias enviam seu clock a cada período de tempo aleatório dentro de um range
      delay = randrange(0, 8)
      sleep(delay)
      clock.send()