# omnivore-export

This is an export script for the
[Omnivore](https://github.com/omnivore-app/omnivore)
read-it-later solution written in Python.

Its main purpose is to create a backup of all links saved in Omnivore,
as long as the Omnivore app stil lacks an export function.

To run this script, you need to install
[gql](https://github.com/graphql-python/gql) with httpx support first:

```sh
pip install --pre -U gql[httpx]
```

Next, you must
[create an API key for Omnivore](https://omnivore.app/settings/api).

Then, in the script `omnivore-summary.py`,
change the global variable `api_key`,
or set the environment variable `OMNIVORE_API_KEY`.

If you're not using the free hosted Omnivore,
you must also change the global variable `api_url`
or set the environment variable `OMNIVORE_API_URL`.

You can change the path for the exported data
with the global variable `backup_path`
or the environment variable `OMNIVORE_BACKUP_PATH`.

Finally, just run the script via Python:

```sh
python omnivore-export.py 
```

This repository also contains a script `omnivore-summary.py`
that can be used to print a summary of the data store in Omnivore.

After configuring it in the same way as the export script, run:

```sh
python omnivore-summary.py 
```
