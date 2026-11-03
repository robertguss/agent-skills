# tasks

A small command-line task list. Python 3.9 or later, standard library only.

## Usage

```sh
python3 -m tasks.cli add "Renew passport" --notes "photo booth on Main St"
python3 -m tasks.cli list
python3 -m tasks.cli list --open
python3 -m tasks.cli list --search passport
python3 -m tasks.cli done 1
python3 -m tasks.cli export --output tasks.csv
```

`list --search TEXT` shows tasks whose title or notes contain TEXT, ignoring case.

## Where tasks are stored

Tasks live in one JSON file: `$TASKS_FILE` if set, otherwise
`~/.local/share/tasks/tasks.json`. Pass `--file PATH` to use another file.

The file is a plain JSON array, so you can edit it by hand, keep it in a
synced folder (Syncthing, Dropbox) to share one list between machines, or
point a script at it.

## Tests

```sh
python3 -m unittest discover
```
