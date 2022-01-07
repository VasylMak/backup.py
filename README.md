# BACKUP.PY
Even the best professionals can make mistakes, and there is no way to exclude human errors from backup algorithms, but we can surely minimize them by making use of consistent algorithms.

## QUICKSTART
Call the `backup` function with your `"source_path"` and `"backup_path"`:

    backup('source/path/', 'backup/path/')

And schedule the execution of <b>backup.py</b> by <b>Crontab</b> on Mac/Linux or <b>Task Scheduler</b> on Windows. Also, you can use a tuple of `excepted_paths` as a third argument, and set `clean_backup` to `True`, but read the [warning](#warning) section before using this last argument.

## WARNING
The `clean_backup=True` argument calls the `backup_cleaner` function, which removes all unnecessary paths from the `"backup_path"` and returns all files changed (maybe by accident) in the backup directory to their state in the source directory. Somebody can be confused why the backup function doesn't replace files changed in the "backup_path" by default, so let's clear this logic below:

- If the `"source_path"` file is modified, the `"backup_path"` file will be overwritten.
- If the `"source_path"` file is unmodified, but the `"backup_path"` file is modified, the last will be untouched until the subsequent modifications on the `"source_path"` file.
   - The idea is that if you confuse your `"backup_path"` directory with the `"source_path"` directory or on purpose you don't need to modify the original file, these changes wouldn't be erased automatically by the scheduled backup command.
- On the other hand, if `clean_backup` is activated, any inconsistency in the `"backup_path"` files will be considered unnecessary.
