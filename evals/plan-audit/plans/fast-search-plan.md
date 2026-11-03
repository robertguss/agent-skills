---
title: Fast task search
type: feat
date: 2026-10-30
status: ready
---

# Fast task search

## Goal

A user can find tasks by a word in the title or notes with one command, `tasks search WORD`. Matching ignores case. Results print in the same format as `tasks list`. A search returns in under 100 ms on a store of 10,000 tasks.

## Problem

Long-running task lists grow into the thousands. People report losing track of older tasks and re-adding duplicates because they can't find the original. They need a quick way to pull up every task that mentions a word.

## Constraints

- Standard library only, Python 3.9 or later.
- No change to the task file's format, so existing files keep working and stay readable.
- Search must stay fast as the store grows; 10,000 tasks is the size we design for.
- Non-goal: fuzzy matching, ranking, or search across several task files.

## Context

- `tasks/store.py` holds `Task` and `Store`. `Store.load()` reads the JSON file and returns a list of `Task`; `Store.save(tasks)` writes the whole list back through a temp file and `os.replace`.
- All writes go through `Store.add`, `Store.mark_done`, and `Store.save`.
- `tasks/cli.py` registers each subcommand in `build_parser()` with a `cmd_<name>(args, store)` handler. `format_task(task)` renders one line of `list` output.

## Approach

Scanning every task's title and notes on each search would get slow as stores grow, so search reads from an inverted index instead of the store.

The index maps each lowercased word to the set of task ids whose title or notes contain it. It lives in a sidecar file next to the store, `<store>.index.json`. `Store.save` rewrites the index whenever it writes the store, so the two files change together and the index never needs a separate rebuild. A search is then one dictionary lookup plus loading the matching tasks.

Tokenization splits on anything that isn't a letter or digit (`re.findall(r"\w+", text.casefold())`). A query word matches a task when it appears as a whole token in the title or notes.

## Steps

1. **Index module.** Add `tasks/index.py` with:
   - `tokenize(text) -> set[str]`
   - `build_index(tasks) -> dict[str, list[int]]`
   - `read_index(store_path)` and `write_index(store_path, index)`, which write `<store>.index.json` through a temp file and `os.replace`, same as `Store.save`.
2. **Keep the index current.** At the end of `Store.save`, call `write_index(self.path, build_index(tasks))`. Since every write path ends in `Store.save`, the index always matches the store.
3. **Search.** Add `Store.search(word)`. It reads the index, looks up `word.casefold()`, and returns the matching tasks from `Store.load()` in id order. When the index file doesn't exist yet (a store created before this change), build it once from `Store.load()` and write it.
4. **CLI.** Add a `search` subparser with one positional `word` argument and a `cmd_search` handler that prints each result with `format_task`.
5. **Docs.** Add `tasks search WORD` to the README usage block and note the `.index.json` sidecar file.

## Test plan

- `tests/test_index.py` (new): `tokenize` lowercases and splits on punctuation; `build_index` maps words from both title and notes; a missing index file is built on first search.
- `tests/test_cli.py`: `add` two tasks, `search` a word from one task's notes, and check that only that task prints.
- A timing test that builds a 10,000-task store in a temp directory and checks that `Store.search` returns in under 100 ms.
- Run `python3 -m unittest discover`.

## Risks

- The sidecar file doubles the number of files a user sees next to their store. The README note covers this.
- Tokenizing on `\w+` means a search for part of a word (`pass` for `passport`) finds nothing. We accept that for now; whole-word search is what people asked for.
