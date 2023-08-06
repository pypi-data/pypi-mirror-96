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
"""Fake setup.py module for installing Nucleus.

Usually, setup.py is invoked twice:  first, to build the pip package
and second to install it.

This setup.py is only used for installation; build_pip_package.sh is
used to create the package.  We do it this way because we need our
package to include symbolic links, which normal setup.py doesn't
support.

For the same reason, this setup.py is not implemented using setuptools.
Instead, we directly implement the four commands run by pip install
(https://pip.pypa.io/en/stable/reference/pip_install/#id46):
  * setup.py egg_info [--egg-base XXX]
  * setup.py install --record XXX [--single-version-externally-managed]
          [--root XXX] [--compile|--no-compile] [--install-headers XXX]
  * setup.py bdist_wheel -d XXX
  * setup.py clean
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from distutils import dist
import distutils.command.install as dist_install
import glob
import os
import shutil
import sys

# Basename of the .egg-info directory.
_EGG_DIR_BASENAME = 'google_nucleus.egg-info'


def _unsafe_filename(filename):
  return any(c in filename for c in ' \t\n\r;&<>*')


def touch(fname):
  open(fname, 'w+').close()


def find_destination(is_user):
  """Returns the directory we are supposed to install into."""
  install_cmd = dist_install.install(dist.Distribution())
  install_cmd.finalize_options()
  if is_user:
    return install_cmd.install_usersite
  else:
    return install_cmd.install_platlib


def copy_egg_info(dest_dir):
  """Copies the .egg-info directory to the specified location.

  Args:
    dest_dir: str. The destination directory.

  Returns:
    0 on success, 1 on failure.
  """
  # Remove any trailing slash on the destination directory.
  dest_dir = dest_dir.rstrip('/')
  egg_srcs = glob.glob('google_nucleus-*-py*.egg-info')
  if not egg_srcs:
    print('Could not find source .egg-info directory')
    return 1
  egg_src = egg_srcs[0]
  print('Copying egg-info from ', egg_src, ' to ', dest_dir)
  shutil.copytree(egg_src, dest_dir)
  return 0


def main():
  if len(sys.argv) < 2:
    print('Missing command')
    sys.exit(1)

  cmd = sys.argv[1]
  args = sys.argv[2:]

  if cmd == 'egg_info':
    egg_dir = _EGG_DIR_BASENAME
    if len(args) > 1 and args[0] == '--egg-base':
      egg_dir = os.path.join(args[1], egg_dir)
    sys.exit(copy_egg_info(egg_dir))

  elif cmd == 'install':
    destination = find_destination('--user' in args)

    record_file = 'install-record.txt'
    if '--record' in args:
      i = args.index('--record')
      record_file = args[i+1]
      if _unsafe_filename(record_file):
        print('Invalid record_file name', record_file)
        sys.exit(1)

    print('Removing old protobuf files')
    os.system('rm -fR ' + destination + '/google/protobuf')

    print('Installing Nucleus to ' + destination
          + ' with record file at ' + record_file)
    os.system('cp -R -v google nucleus ' + destination
              + " | awk '{print substr($3,2,length($3)-2)}' > " + record_file)
    # Append the .egg-info directory (must include trailing '/') to the record.
    dest_egg_dir = os.path.join(destination, _EGG_DIR_BASENAME) + '/'
    os.system('echo ' + dest_egg_dir + ' >> ' + record_file)
    # End by copying the .egg-info directory to the destination.
    sys.exit(copy_egg_info(dest_egg_dir))

  elif cmd == 'bdist_wheel':
    print('This package does not support wheel creation.')
    sys.exit(1)

  elif cmd == 'clean':
    # Nothing to do
    sys.exit(0)

  print('Unknown command: ', cmd)
  sys.exit(1)


if __name__ == '__main__':
  main()
