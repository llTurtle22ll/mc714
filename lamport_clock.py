from random import randrange
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = {'a': 7, 'b': 3.14}
    comm.send(data, dest=1, tag=11)
    print("entrei")
else:
    data = comm.recv(source=0, tag=11)
    print("entrei 2")
