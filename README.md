# BACKUP.PY
Even the best professionals can make mistakes, and there is no way to exclude human errors from backup algorithms, but we can surely minimize them by making use of consistent algorithms.

## QUICKSTART
Call the `backup` function with your `"source_path"` and `"backup_path"`:

    backup('source/path/', 'backup/path/')

And schedule the execution of <b>backup.py</b> using <b>Task Scheduler</b> on Windows or <b>Crontab</b> on Mac/Linux. Also, you can use a tuple of `excepted_paths` as a third argument, and set `clean_backup` to `True`, but read the [warning](#warning) section before using this last argument.

## SCHEDULING

### Task Scheduler
Open <b>Task Scheduler</b> and press <b>Create Task...</b> In the <b>General</b> tab of the <b>Create Task</b> window, type your task <b>Name</b>, add some <b>Description</b> if you want, select <b>Run whether user is logged on or not</b> and <b>Run with highest privileges</b>:

![task_scheduler_general](https://github.com/VasylMak/backup.py/blob/main/Task%20Scheduler%20Screenshots/task_scheduler_general.png?raw=true)

Go to the <b>Triggers</b> tab and press <b>New...</b> In the <b>New Trigger</b> window, press <b>Repeat task every:</b>, choose how often you want to repeat this task, set <b>for a duration of:</b> to <b>Indefinitely</b> and press <b>OK</b>:

![task_scheduler_triggers](https://github.com/VasylMak/backup.py/blob/main/Task%20Scheduler%20Screenshots/task_scheduler_triggers.png?raw=true)

Moved to the <b>Actions</b> tab press <b>New...</b> too. In the <b>New Action</b> window, go to the <b>Program/script:</b> setting and <b>Browse...</b> your python interpreter (Here the best choice is the usage of <b>pyw.exe</b>/<b>pythonw.exe</b> if you want to run the script hiddenly in the background). Also, be sure to add the path to <b>backup.py</b> with quotes in the option <b>Add arguments (optional):</b> before pressing <b>OK</b>:

![task_scheduler_actions](https://github.com/VasylMak/backup.py/blob/main/Task%20Scheduler%20Screenshots/task_scheduler_actions.png?raw=true)

Finally, in the <b>Conditions</b> tab, disable the <b>Start the task only if the computer is on AC power</b> option and press <b>OK</b>:

![task_scheduler_conditions](https://github.com/VasylMak/backup.py/blob/main/Task%20Scheduler%20Screenshots/task_scheduler_conditions.png?raw=true)

Of course, for security reasons, Windows will ask your account password.

### Crontab

Open your terminal and type:

    $ crontab -e

In the opened file, firstly, type how often you want to execute the command. For example: `*/5 * * * *` means every 5 minutes (for better comprehension, you can test these expressions on [Crontab.guru](https://crontab.guru/)). Now type `python3` or the path to your python installation and finally add the path of the script:

    */5 * * * * python3 /your/path/backup.py

Don't forget to save your changes.

## WARNING
The `clean_backup=True` argument calls the `backup_cleaner` function, which removes all unnecessary paths from the `"backup_path"` and returns all files changed (maybe by accident) in the backup directory to their state in the source directory. Somebody can be confused why the backup function doesn't replace files changed in the `"backup_path"` by default, so let's clear this logic below:

- If the `"source_path"` file is modified, the `"backup_path"` file will be overwritten.
- If the `"source_path"` file is unmodified, but the `"backup_path"` file is modified, the last will be untouched until the subsequent modifications on the `"source_path"` file.
   - The idea is that if you confuse your `"backup_path"` directory with the `"source_path"` directory or on purpose you don't need to modify the original file, these changes wouldn't be erased automatically by the scheduled backup command.
- On the other hand, if `clean_backup` is activated, any inconsistency in the `"backup_path"` files will be considered unnecessary.
