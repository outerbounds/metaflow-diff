#!/usr/bin/env python
import sys
import os
import shutil
from tempfile import TemporaryDirectory
from subprocess import call, run, PIPE
import os

from metaflow import namespace, Run
from metaflow.cli import echo_always
import click


EXCLUSIONS = [
    'metaflow/',
    'metaflow_extensions/',
    'INFO',
    'CONFIG_PARAMETERS',
    'conda.manifest'
]

def git_diff(tmpdir, output=False):
    for dirpath, dirnames, filenames in os.walk(tmpdir):
        for fname in filenames:
            rel = os.path.relpath(dirpath, tmpdir)
            cmd = ["git", "diff", "--no-index", os.path.join(rel, fname), os.path.join(dirpath, fname)]
            if output:
                yield run(cmd, text=True, stdout=PIPE).stdout
            else:
                run(cmd)

def echo(line):
    echo_always(line, err=True, fg='magenta')

def op_diff(tmpdir):
    for _ in git_diff(tmpdir):
        pass

def op_pull(tmpdir, dst=None):
    if os.path.exists(dst):
        echo(f"❌  Directory *{dst}* already exists")
    else:
        shutil.move(tmpdir, dst)
        echo(f"Code downloaded to *{dst}*")

def op_patch(tmpdir, dst=None):
    with open(dst, 'w') as f:
        for out in git_diff(tmpdir, output=True):
            out = out.replace(tmpdir, '/.')
            out = out.replace("+++ b/./", "+++ b/")
            out = out.replace("--- b/./", "--- b/")
            out = out.replace("--- a/./", "--- a/")
            out = out.replace("+++ a/./", "+++ a/")
            f.write(out)
    echo(f"Patch saved in *{dst}*")
    path = run(['git', 'rev-parse', '--show-prefix'], text=True, stdout=PIPE).stdout.strip()
    if path:
        diropt = f" --directory={path.rstrip('/')}"
    else:
        diropt = ""
    echo("Apply the patch by running:")
    echo_always(f"git apply --verbose{diropt} {dst}", highlight=True, bold=True, err=True)

def run_op(runspec, op, op_args):
    try:
        namespace(None)
        run = Run(runspec)
        echo(f"✅  Run *{runspec}* found, downloading code..")
    except:
        echo(f"❌  Run **{runspec}** not found")
        sys.exit(1)
    if run.code is None:
        echo(f"❌  Run **{runspec}** doesn't have a code package. Maybe it's a local run?")
        sys.exit(1)
    tar = run.code.tarball
    members = []
    for m in tar.getmembers():
        if not any(m.name.startswith(x) for x in EXCLUSIONS):
            members.append(m)
    tmp = None
    try:
        tmp = TemporaryDirectory()
        tar.extractall(tmp.name, members)
        op(tmp.name, **op_args)
    finally:
        if tmp:
            if os.path.exists(tmp.name):
                pass
                #shutil.rmtree(tmp.name)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('metaflow_run')
def diff(metaflow_run=None):
    """
    Show a 'git diff' between the current working directory and
    the given Metaflow run, e.g. HelloFlow/3
    """
    run_op(metaflow_run, op_diff, {})

@cli.command()
@click.argument('metaflow_run')
@click.option('--dir', help='Destination directory (default: {runspec}_code)', default=None)
def pull(metaflow_run=None, dir=None):
    """
    Pull the code of a Metaflow run, e.g. HelloFlow/3, to
    the given directory
    """
    if dir is None:
        dir = metaflow_run.lower().replace('/', '_') + "_code"
    run_op(metaflow_run, op_pull, {'dst': dir})

@cli.command()
@click.argument('metaflow_run')
@click.option('--file', help='Patch file name (default: {runspec}.patch', default=None)
def patch(metaflow_run, file=None):
    """
    Produce a patch file capturing the diff between the current
    working directory and the given Metaflow run, e.g. HelloFlow/3
    """
    if file is None:
        file = metaflow_run.lower().replace('/', '_') + ".patch"
    run_op(metaflow_run, op_patch, {'dst': file})

