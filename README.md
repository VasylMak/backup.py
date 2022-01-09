# BACKUP.PY
After the [disaster happened at Kyoto University](https://gizmodo.com/university-loses-valuable-supercomputer-research-after-1848286983), it's evident that there is no way to exclude human errors from backup algorithms, but we can surely minimize them. Python permit writing code very close to standard English sentences, which reduces the likelihood of bugs. The script presented in this repository should be self-explanatory and, in most cases, can be used without changes, as explained in the [quickstart](#quickstart) section. However, it's always good to review the code with caution, principally if it interacts with crucial data, so I invite you to check the [tutorial](#) with an explanation about each line.

## QUICKSTART
Call the `backup` function with your `"source_path"` and `"backup_path"`:

``` python
backup('source/path/', 'backup/path/')
```

And schedule the execution of <b>backup.py</b> using [Task Scheduler](#task-scheduler) on Windows or [Crontab](#crontab) on Mac/Linux. Also, you can use a tuple of `excepted_paths` as a third argument, and set `clean_backup` to `True`, but read the [warning](#warning) section before using this last argument.

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

``` shell
$ crontab -e
```

In the opened file, firstly, type how often you want to execute the command. For example: `*/5 * * * *` means every 5 minutes (for better comprehension, you can test these expressions on [Crontab.guru](https://crontab.guru/)). Now type `python3` or the path to your python installation and finally add the path of the script:

    */5 * * * * python3 /your/path/backup.py

Don't forget to save your changes.

## WARNING
The `clean_backup=True` argument calls the `backup_cleaner` function, which removes all unnecessary paths from the `"backup_path"` and returns all files changed (maybe by accident) in the backup directory to their state in the source directory. Somebody can be confused why the backup function doesn't replace files changed in the `"backup_path"` by default, so let's clear this logic below:

- If the `"source_path"` file is modified, the `"backup_path"` file will be overwritten.
- If the `"source_path"` file is unmodified, but the `"backup_path"` file is modified, the last will be untouched until the subsequent modifications on the `"source_path"` file.
   - The idea is that if you confuse your `"backup_path"` directory with the `"source_path"` directory or on purpose you don't need to modify the original file, these changes wouldn't be erased automatically by the scheduled backup command.
- On the other hand, if `clean_backup` is activated, any inconsistency in the `"backup_path"` files will be considered unnecessary.

## TUTORIAL

### Imports
Let's ignore the header and get to the point. When it comes to importing libraries in Python, a good practice is to `import x` and then use the full path to any function in a module, but following the [PEP 8](https://www.python.org/dev/peps/pep-0008/) limitation of 80 characters per line, the DRY philosophy and my vision of beauty:

``` python
from os import chdir
from os import name
from os import walk
from os import rename
from os import makedirs
from os import remove
from os.path import join as join_path
from os.path import getmtime
from os.path import getsize
from os.path import exists
from os.path import isfile
from os.path import dirname

from shutil import rmtree
from shutil import copy2 as copy

from logging import info
from logging import INFO
from logging import warning
from logging import error
from logging import critical
from logging import basicConfig as basic_config
```

### Logging
Logging is an essential tool for debugging, and it can clarify all backup interactions. To generate the log beside <b>backup.py</b>:

``` python
chdir(dirname(__file__))
```

The message formatting caths the runtime, level of gravity, and event. This formatting caths the runtime, level of gravity, and event message. The message formatting caths the runtime, level of gravity, and event explanation. All levels starting with `INFO` will be written to <b>backup.log</b>:

``` python
log_format = '%(asctime)s - %(levelname)s - %(message)s'
basic_config(filename='backup.log', level=INFO, format=log_format)
```

### Constants
I think nobody wants to duplicate files in the Trash/Recycle Bin, so their paths are unnecessary in backup functions:

``` python
TRASH = ('/.Trash', '/Trash')
RECYCLE_BIN = (':\$RECYCLE.BIN',)
```

In case of a sudden interruption in the copying process, an incomplete file will have this extension:

``` python
INCOMPLETE_EXTENSION = '.incomplete'
```

These error codes will make sense later:

``` python
INEXISTENT_FILE = 2
CORRUPTION_ERROR = 22
```

### Backup
<i>Next is located the</i> `backup_cleaner` <i>function, but for a more comprehensive explanation, we will return to it at the end.</i>

The backup function has four parameters with a corresponding docstring:

``` python
def backup(source_path, backup_path, excepted_paths=None, clean_backup=False):
    '''Backup files from "source_path" to "backup_path"

    Parameters:
        source_path (str) - the source directory to be backuped;
        backup_path (str) - the output directory of the backup;
        excepted_paths (tuple) - unnecessary "source_path" directories;
        clean_backup (boolean) - removes extra files in "backup_path".
    '''
```
