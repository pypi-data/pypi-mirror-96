# Copyright 2018 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Classes for reading and writing FASTQ files.

The FASTQ format is described at
https://en.wikipedia.org/wiki/FASTQ_format

API for reading:

```python
from nucleus.io import fastq

with fastq.FastqReader(input_path) as reader:
  for record in reader:
    print(record)
```

where `record` is a `nucleus.genomics.v1.FastqRecord` protocol buffer.

API for writing:

```python
from nucleus.io import fastq

# records is an iterable of nucleus.genomics.v1.FastqRecord protocol buffers.
records = ...

with fastq.FastqWriter(output_path) as writer:
  for record in records:
    writer.write(record)
```

For both reading and writing, if the path provided to the constructor contains
'.tfrecord' as an extension, a `TFRecord` file is assumed and attempted to be
read or written. Otherwise, the filename is treated as a true FASTQ file.

Files that end in a '.gz' suffix cause the file to be treated as compressed
(with BGZF if it is a true FASTQ file, and with gzip if it is a TFRecord file).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nucleus.io import genomics_reader
from nucleus.io import genomics_writer
from nucleus.io.python import fastq_reader
from nucleus.io.python import fastq_writer
from nucleus.protos import fastq_pb2


class NativeFastqReader(genomics_reader.GenomicsReader):
  """Class for reading from native FASTQ files.

  Most users will want to use FastqReader instead, because it dynamically
  dispatches between reading native FASTQ files and TFRecord files based on the
  filename's extension.
  """

  def __init__(self, input_path):
    """Initializes a NativeFastqReader.

    Args:
      input_path: str. A path to a resource containing FASTQ records.
    """
    super(NativeFastqReader, self).__init__()

    fastq_path = input_path.encode('utf8')
    options = fastq_pb2.FastqReaderOptions()
    self._reader = fastq_reader.FastqReader.from_file(fastq_path, options)
    self.header = None

  def query(self, region):
    """Returns an iterator for going through the records in the region.

    NOTE: This function is not implemented by NativeFastqReader as there is no
    concept of genome ordering in the FASTQ format.
    """
    raise NotImplementedError('Can not query a FASTQ file')

  def iterate(self):
    """Returns an iterable of FastqRecord protos in the file."""
    return self._reader.iterate()

  def __exit__(self, exit_type, exit_value, exit_traceback):
    self._reader.__exit__(exit_type, exit_value, exit_traceback)


class FastqReader(genomics_reader.DispatchingGenomicsReader):
  """Class for reading FastqRecord protos from FASTQ or TFRecord files."""

  def _native_reader(self, input_path, **kwargs):
    return NativeFastqReader(input_path, **kwargs)

  def _record_proto(self):
    return fastq_pb2.FastqRecord


class NativeFastqWriter(genomics_writer.GenomicsWriter):
  """Class for writing to native FASTQ files.

  Most users will want FastqWriter, which will write to either native FASTQ
  files or TFRecord files, based on the output filename's extension.
  """

  def __init__(self, output_path, **kwargs):
    """Initializer for NativeFastqWriter.

    Args:
      output_path: str. The path to which to write the FASTQ file.
      **kwargs: optional arguments; presently ignored.
    """
    super(NativeFastqWriter, self).__init__()

    writer_options = fastq_pb2.FastqWriterOptions()
    self._writer = fastq_writer.FastqWriter.to_file(output_path, writer_options)

  def write(self, proto):
    self._writer.write(proto)

  def __exit__(self, exit_type, exit_value, exit_traceback):
    self._writer.__exit__(exit_type, exit_value, exit_traceback)


class FastqWriter(genomics_writer.DispatchingGenomicsWriter):
  """Class for writing FastqRecord protos to FASTQ or TFRecord files."""

  def _native_writer(self, output_path, **kwargs):
    return NativeFastqWriter(output_path, **kwargs)
