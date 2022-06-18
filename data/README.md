# streaming-cosmic-rays/**data**

- **mapd-minidt-stream** data downloaded from cloud veneto, for local analysis

To use the *local-download* script, configure the .hidden file with your **credentials**. Then execute

```bash
cd mapd-minidt-stream & ../local-download.py
```

An example of credentials file is
```bash
$ cat credentials.hidden
{"key_id":"aaaabbbbccccddddeeeeffff","key":"gggghhhhiiiijjjjkkkk"}
```