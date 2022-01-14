import hashlib
import subprocess
import sys
import os.path


def filename(mode, suffix, body):
    md = hashlib.md5()
    for part in body:
        md.update(part.encode('utf-8'))

    return mode + '-' + md.hexdigest() + '.' + suffix


def command(cmd, filename, body):
    if os.path.exists(filename):
        return
    sub = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=sys.stderr)

    for part in body:
        sub.stdin.write(part.encode('utf-8'))
    sub.stdin.close()
    sub.wait()


def pipe(cmd, filename, body):
    if os.path.exists(filename):
        return
    with open(filename, 'wb') as fp:
        sub = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=fp,
                               stderr=sys.stderr)

    for part in body:
        sub.stdin.write(part.encode('utf-8'))
    sub.stdin.close()
    sub.wait()


def accept(fmts, *acc):
    for f in fmts:
        if f in acc:
            return f
    raise ValueError("Unacceptable: " + fmts + ' not in ' + acc)
