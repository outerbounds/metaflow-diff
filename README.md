# `metaflow-diff` - run `git diff` between a repo and a Metaflow run

![Metaflow diff screenshot](metaflow-diff.png)

1. Create a Metaflow flow, say, `HelloFlow`, in a git repo as usual
2. Run it remotely: `python hello.py run --with kubernetes` or `python hello.py run --with batch`
3. Note the run ID in the console or in the UI, e.g. `HelloFlow/5`.
4. Continue editing code
5. Run `metaflow-diff diff HelloFlow/5` to see how the code has changed in the given execution 💡

> [!NOTE]
> `metaflow-diff` displays differences only for files associated with the specified run.
> Any new files added to the current working directory that are not part of the run will
> be excluded from the output.

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


