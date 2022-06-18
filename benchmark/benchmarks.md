# benchmarks

We benchmark the Operation duration, given an input stream of values fixed at 1100 Hz.

### cloud veneto cluster

Each worker in the following table is to be intended with 4 cores & 2GB of memory, except for the *4 workers* column, for which we reduced to 2 the number of cores. Linger time is fixed to $1 s$.

| **partitions** | 2 workers (4c) | 1 worker (4c) | *4 workers* (2c) |
|    :---:   |  ---      | ---       | ---       |
|    *min*   |\[2\] 4500 |\[1\] 4000 |\[4\] 5600 |
|     12     | 6000      | 5050      | 6000      |
|     24     | 8000      | 6800      | 8000      |
|     64     | 12000     |  -        | -         |
|    128     | 21000     |  -        | -         |

### cayde cluster

| **partitions** | 1 worker, 4 cores | 
|    :---:   |  ---      | 
|     1      | 1960      |
|     12     | 1980      |
|     24     | 1990      |

| partitions | **linger** (ms) | 8 workers, 2 cores | 
|    :---:   |  ---   | ---      | 
|     8      |  1000  | 1950     |
|     8      |   500  | 1650     |


With linger time of 500 ms:

| **workers** | **cores per worker** | memory per worker | operation duration (ms) |
|  :---:  |  :---:      | ---       | ---       |
|    2    | 4 | 2 | 1450 |
|    2    | 8 | 3 | 1500 |
|    4    | 4 | 2 | 1450 |