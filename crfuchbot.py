#!/usr/bin/env python

# Copyright 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import subprocess
import sys
import uuid


def git(*args):
  return subprocess.check_output(('git',) + args)


def main():
  initial_dir = os.getcwd()
  repo_root = 'repos'
  separator = uuid.uuid4().hex
  for repo in os.listdir(repo_root):
    repo_root = os.path.join(initial_dir, repo_root, repo)
    if not os.path.isdir(repo_root):
      continue
    os.chdir(repo_root)
    update_filename = '../' + repo + '.lastupdate'
    with open(update_filename, 'r') as f:
      last_rev = f.read().strip()
    print git('fetch', 'origin'),
    print git('checkout', 'origin/master'),
    head_rev = git('rev-parse', 'HEAD').strip()
    with open(update_filename, 'w') as f:
      f.write(head_rev)
    output = git('log',
                '--format=%(sep)s%%H%(sep)s%%ae%(sep)s%%s%(sep)s%%B' % {
                    'sep': separator},
                '--raw',
                last_rev + '..' + head_rev)
    print 'checking', last_rev, 'to', head_rev
    if not output:
      continue
    if not output.startswith(separator):
      raise Exception('output should have started with separator')
    output = output[len(separator):].split(separator)
    if len(output) % 4 != 0:
      raise Exception('output should have been in quads')
    for i in range(0, len(output), 4):
      commit = output[i+0]
      author = output[i+1]
      subject = output[i+2]
      data = output[i+3]
      if 'fuchsia' in data.lower():
        popen = subprocess.Popen(['nc', '127.0.0.1', '12345'],
                                 stdin=subprocess.PIPE)
        # TODO: repo root url hardcoded.
        print 'sending to irc:', subject, author, commit
        popen.communicate(
            '%s %s https://chromium.googlesource.com/chromium/src/+/%s\n' % (
                subject, author, commit))
        popen.wait()
  return 0


if __name__ == '__main__':
  sys.exit(main())
