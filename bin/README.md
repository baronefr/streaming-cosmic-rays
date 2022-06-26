# streaming-cosmic-rays/**bin**

**description**

- **cosmo** the bash tool to manage the cluster execution
- **mydash** the bokeh dashboard to monitor the processed data

- *spark_analysis.py* is the actual Spark analysis code
    - to make this file more readable, we provide a Jupyter notebook: *spark_analysis_demo.ipynb*
![spark_warning](../share/warning_spark.png)
    
- *streamer_local_minidt.py* creates a stream of values from muon detectors

### requirements

If you don't have already a Kafka & Spark cluster, you must configure your own.

Download **Kafka 3.2.0** from [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.2.0/kafka_2.13-3.2.0.tgz).

Download **Spark 3.2.1** from [here](https://www.apache.org/dyn/closer.lua/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz).

Then link the resources as you wish.
