# benchmarks

We benchmark the Operation duration, given an input stream of values fixed at 1100 Hz.

### cloud veneto cluster

Each worker in the following table is to be intended with 4 cores & 2GB of memory, except for the *4 workers* column, for which we reduced to 2 the number of cores. Linger time is fixed to $1 s$.

| **partitions** | 2 workers (4c) | 1 worker (4c) | *4 workers* (2c) |
|    :---:   |  :---:     | :---:       | :---:       |
|    *min*   |\[2\] 3600  |\[1\] 3700 |\[4\] 3900 |
|     12     |  4900      | 4900      | 4900      |
|     24     |  6000      | 5900      | 6300      |
|     64     |  8900      |  -        | -         |
|    128     | 13000      |  -        | -         |

### cayde cluster

On Cayde we use a default linger time of 500ms, unless otherwise specified.

| **workers** | **cores per worker** | operation duration (ms) |
|  :---:  |  :---:      | :---:       |
|    2    | 4 |  1450 |
|    2    | 8 |  1490 |
|    4    | 4 |  1500 |

| partitions | **linger** (ms) | 8 workers, 2 cores | 
|    :---:   |  :---:   | :---:      | 
|     8      |  1000  | 1950     |
|     8      |   500  | 1450     |

If we restrict to just a single worker:

| **partitions** | 1 worker, 4 cores | 
|    :---:   |  :---:      | 
|     1      | 1500      |
|     12     | 1800      |
|     24     | 1890      |

Vertical scaling?

| **partitions** | linger | 1 worker, 20 cores, 16gb ram | 
|    :---:   |  :---:      |:---:      |
|      1     |  200   | 1350      |
|     20     | 500    | 1500      | 
