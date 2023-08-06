# Copyright 2018 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A universal converter program for nucleus-supported genomics file formats.

Invoked with a single argument, this program will open a genomics data file and
iterate over its contents, doing no writing.  This is a good benchmark for I/O
and reader processing speed.

Invoked with two arguments, the program will open the first file, read its
records, and write them, one at a time, to the second file.  The filetypes for
the first and second filename must be compatible ways of encoding the same
nucleus genomics record type (for example, `infile.gff` and
`outfile.gff.tfrecord.gz` are compatible, but `infile.gff` and `outfile.bam` are
not.

Note: at present we have no convention for encoding a file *header* in
tfrecords, so conversion is not possible from tfrecord to any native file format
for which a header is compulsory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import re
import sys
import time

from absl import app
from absl import logging

from nucleus.io import bed
from nucleus.io import fastq
from nucleus.io import gff
from nucleus.io import sam
from nucleus.io import vcf


def _is_native_file(filename):
  """Returns true if filename is a native (non-tfrecord) genomics data file."""
  return not re.match(r".*\.tfrecord(\.gz)?", filename)


def _filename_pattern(ext):
  """Returns an re matching native or tfrecord files of format `ext`."""
  return r".*\.{}(\.tfrecord)?(\.gz)?".format(ext)


_FileType = collections.namedtuple(
    "_FileType", ("reader_class", "writer_class", "has_header"))

_FILETYPE_LOOKUP = {
    _filename_pattern("bed"):
        _FileType(bed.BedReader, bed.BedWriter, False),
    _filename_pattern("(fastq|fq)"):
        _FileType(fastq.FastqReader, fastq.FastqWriter, False),
    _filename_pattern("gff"):
        _FileType(gff.GffReader, gff.GffWriter, True),
    _filename_pattern("(bam|sam)"):
        _FileType(sam.SamReader, sam.SamWriter, True),
    _filename_pattern("vcf"):
        _FileType(vcf.VcfReader, vcf.VcfWriter, True),
}


def _lookup_filetype(filename):
  for pattern in _FILETYPE_LOOKUP:
    if re.match(pattern, filename):
      return _FILETYPE_LOOKUP[pattern]
  raise ConversionError("Unrecognized extension!")

LOG_EVERY = 100000


class ConversionError(Exception):
  """An exception used to signal file conversion error."""
  pass


class NullWriter(object):
  """A writer class whose .write() method is a no-op.

  This allows us to create and use a writer object where one is required by
  context but we do not wish to write to any file.
  """

  def __init__(self, unused_filename, header=None):
    pass

  def write(self, unused_record):
    pass

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    pass


def _reader_writer_classes(in_filename, out_filename):
  """Returns reader, writer classes for filenames, if conversion is possible.

  Args:
    in_filename: filename of a genomics data file to use as input.
    out_filename: filename of a genomics data file to use as output, or None,
      if no output should be written.

  Raises:
    ConversionError: if in_filename is not convertible to out_filename.
  """
  in_filetype = _lookup_filetype(in_filename)
  out_filetype = _lookup_filetype(out_filename) if out_filename else None

  if out_filetype:
    if in_filetype != out_filetype:
      raise ConversionError(
          "Input and output filetypes specified are incompatible.")
    input_has_header = in_filetype.has_header and _is_native_file(in_filename)
    output_requires_header = (
        out_filetype.has_header and _is_native_file(out_filename))
    if output_requires_header and not input_has_header:
      raise ConversionError(
          "Input file does not have a header, which is needed to construct "
          "output file")
    writer_class = out_filetype.writer_class

  else:
    writer_class = NullWriter

  return in_filetype.reader_class, writer_class


def convert(in_filename, out_filename):
  """Converts a recognized genomics file `in_filename` to `out_filename`.

  Args:
    in_filename: str; filename of a genomics data file to use as input.
    out_filename: str; filename of a genomics data file to use as output, or
      None, if no output should be written.

  Raises:
    ConversionError, if the conversion could not be executed.
  """
  reader_class, writer_class = _reader_writer_classes(in_filename, out_filename)
  reader = reader_class(in_filename)

  with reader_class(in_filename) as reader:
    with writer_class(out_filename, header=reader.header) as writer:
      start = time.time()
      i = 0
      for record in reader:
        i += 1
        writer.write(record)
        logging.log_every_n(logging.INFO, "Progress: %d records", LOG_EVERY, i)
      elapsed = time.time() - start
      logging.info("Done, processed %d records in %0.2f seconds.", i, elapsed)


def main(argv):
  if len(argv) not in (2, 3):
    print("Usage: %s <input_filename> [<output_filename>]" % argv[0])
    sys.exit(1)

  input_filename = argv[1]
  output_filename = None if len(argv) == 2 else argv[2]

  try:
    convert(input_filename, output_filename)
  except ConversionError as e:
    print("Could not execute conversion:", e)
    sys.exit(1)


if __name__ == "__main__":
  app.run(main)
