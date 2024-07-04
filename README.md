# omnivore-export

This is an export script for the
[Omnivore](https://github.com/omnivore-app/omnivore)
read-it-later solution written in Python.

Its main purpose is to create a backup of all links saved in Omnivore,
as long as the Omnivore app still lacks an export function.

## Prerequisites

To run this script, you need to install
[gql](https://github.com/graphql-python/gql) with httpx support first:

```sh
pip install --pre -U gql[httpx]
```

Next, you must
[create an API key for Omnivore](https://omnivore.app/settings/api).

Then, change the global variable `API_KEY`
in the script `omnivore-summary.py`,
or set the environment variable `OMNIVORE_API_KEY`.

If you're not using the free hosted Omnivore,
you must also change the global variable `API_URL`
or set the environment variable `OMNIVORE_API_URL`.

## Other options

You can change the path for the exported data
with the global variable `BACKUP_PATH`
or the environment variable `OMNIVORE_BACKUP_PATH`.
The current date is automatically added to the backup filename,
unless you change the global variable `WITH_DATE` to False
or set the environment variable `OMNIVORE_WITH_DATE` to `no`.

There are some more global variables that you can change in the script:

- `SEARCH = "in:all"` - change if you don't want to export everything
- `LIMIT = 100` - the batch size when querying the API (max. 100)
- `TIMEOUT = 15` - the request timeout in seconds when querying the API
- `WITH_CONTENT = False` - change if you want to export the content as well

## Running the script

Finally, just run the script via Python:

```sh
python omnivore-export.py 
```

## Data Store summary

This repository also contains a script `omnivore-summary.py`
that can be used to print a summary of the data store in Omnivore.

After configuring it in the same way as the export script, run:

```sh
python omnivore-summary.py 
```

## Command line options

Instead of setting parameters in the script or via environment variables,
you can also pass them as options on the command line. You can show the
exact command line syntax by running the script with the  `--help` option.
