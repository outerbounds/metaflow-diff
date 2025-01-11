# `metaflow-diff` - run `git diff` between a repo and a Metaflow run

1. Create a Metaflow flow, say, `HelloFlow`, in a git repo as usual
2. Run it remotely: `python hello.py run --with kubernetes` or `python hello.py run --with batch`, which produces a run ID, e.g. `HelloFlow/5`.
3. Continue editing code
4. Run `metaflow-diff diff HelloFlow/5` to see how the code has changed in the given execution 💡

## Commands

```
metaflow-diff diff HelloFlow/5
```

Show diff between the current working directory and the given run.

```
metaflow-diff pull --dir code HelloFlow/5
```

Pull the code of the given run to a directory.

```
metaflow-diff patch --file my.patch HelloFlow/5
```

Produce a patch file that, if applied, changes the code in the current
working directory to match that of the run.


