# procurement handling project

This project uses [uv](https://docs.astral.sh/uv/).

## Quick start

```shell
# Install dependencies
uv sync

# run main processing pipeline
uv run main_processor.py
```

# Notes

This includes:
   * procurement parser
   * an example duplicate checker
   * example multi-threaded pipeline

Other parts included in the schematic are not included, I will explain this in detail later.

I use python's built in multi-threading as an example, but the concurrency executioner
can easily be replaced by another implemtation of choice, (multiprocess, gevent, eventlet, etc.)

Concurrency is implemented safely, IO is guarded by a semaphore.

The results are set to an output file as an example, but they could be sent to a database if
in a production scenario.
Note that the output files are json lines not a large json object. Although not part of the design,
this allow for writting very large amounts of data and read it in a streaming fashion safely, line by line.
