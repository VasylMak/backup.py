# BACKUP.PY
After the [disaster happened at Kyoto University](https://gizmodo.com/university-loses-valuable-supercomputer-research-after-1848286983), it's evident that there is no way to exclude human errors from backup algorithms, but we can surely minimize them. Python permits writing code very close to standard English sentences, which reduces the likelihood of bugs. The script presented in this repository should be self-explanatory and, in most cases, can be used without changes, as explained in the [quickstart](#quickstart) section. However, it's always good to review the code with caution, mostly if it interacts with crucial data, so I invite you to check this [tutorial](#tutorial) with the deep explanation.

## Table of Contents
- [Quickstart](#quickstart)
- [Scheduling](#scheduling)
   - [Task Scheduler (for Windows users)](#task-scheduler)
   - [Crontab (for Mac/Linux users)](#crontab)
- [Warning](#warning)
- [Tutorial](#tutorial)
   - [Imports](#imports)
   - [Logging](#logging)
   - [Constants](#constants)
   - [Backup](#backup)
   - [Cleaner](#cleaner)

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

The message formatting caths the runtime, level of gravity, and event explanation. All levels starting with `INFO` will be written to <b>backup.log</b>:

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
def backup(source_path,backup_path,excepted_paths=tuple(),clean_backup=False):
    '''Backup files from "source_path" to "backup_path"

    Parameters:
        source_path (str) - the source directory to be backuped;
        backup_path (str) - the output directory of the backup;
        excepted_paths (tuple) - unnecessary "source_path" directories;
        clean_backup (boolean) - removes extra files in "backup_path".
    '''
```

With the help of `os.name`, python will decide if the `TRASH` or `RECYCLE_BIN` directory is relevant in an operating system and join them with the added `excepted_paths`:

``` python
    # Except trash/recycle bin
    if name == 'posix':
        system_exception = TRASH
    elif name == 'nt':
        system_exception = RECYCLE_BIN
    
    # Add user exceptions if they exist
    excepted_paths += system_exception
    warning(f'Excepted paths -> {"; ".join(path for path in excepted_paths)}')
```

Directories found in the `source_path` can be convenient in the log and are needed if `clean_backup=True`:

``` python
    # Source found directories
    expected_folders = set()
    expected_files = set()
    backuped_paths = 0
```

This loop will iterate over the `source_path` and ignore `excepted_paths`:

``` python
    for dir_path, folders, filenames in walk(source_path):
        # Except all exceptions
        if not any(excepted in dir_path for excepted in excepted_paths):
```

Maybe, is not too important, but empty folders will count:

``` python
            # Copy empty folders too
            if folders == [] and filenames == []:
                backup_folder_path = dir_path.replace(source_path, backup_path)
                expected_folders.add(backup_folder_path)
                if not exists(backup_folder_path):
                    makedirs(backup_folder_path)
                    info(f'Folder "{backup_folder_path}" is created')
                    backuped_paths += 1
```

Modified and new files will have the incomplete extension until a successful copy:

``` python
            for file in filenames:
                file_path = join_path(dir_path, file)
                backup_file_path = file_path.replace(source_path, backup_path)
                expected_files.add(backup_file_path)
                incomplete_file_path = backup_file_path+INCOMPLETE_EXTENSION

                try:
                    # Copy matched but modificated files
                    if exists(backup_file_path):
                        file_mod_time = getmtime(file_path)
                        backup_file_mod_time = getmtime(backup_file_path)
                        if backup_file_mod_time < file_mod_time:
                            copy(file_path, incomplete_file_path)
                            remove(backup_file_path)
                            rename(incomplete_file_path, backup_file_path)
                            info(f'File "{backup_file_path}" is updated')
                            backuped_paths += 1
                    # Copy new files
                    else:
                        backup_file_dir = backup_file_path[:-len(file)]
                        makedirs(backup_file_dir, exist_ok=True)
                        copy(file_path, incomplete_file_path)
                        rename(incomplete_file_path, backup_file_path)
                        info(f'Copied "{file_path}" to "{backup_file_path}"')
                        backuped_paths += 1
```

The except statement handle corrupted files, but any unexpected error should crash the execution:

``` python
                except OSError as os_error:
                    error_code = os_error.errno
                    if error_code == CORRUPTION_ERROR:
                        critical(f'File "{file_path}" is corrupted')
                    else:
                        error(f'{os_error} in the "backup()" function')
                        raise os_error
```

In addition to significant log statistics, `paths` can give the necessary data to `backup_cleaner`:

``` python
    paths = expected_folders.union(expected_files)
    info(f'{len(paths)} paths are processed')
    info(f'{backuped_paths} paths are backuped')
    
    # Warning: This function removes all unmatched data in backup paths
    if clean_backup:
        warning('Backup cleaner deletes all inconsistent paths in the backup')
        backup_cleaner(source_path, backup_path, paths, system_exception)
    else:
        info(f'"clear_backup" argument is set to "False"\nBackup completed\n')
```

### Cleaner
Sometimes some data are deleted from the source path consciously, and removing these accumulated directories can be tedious, so solving this task automatically it's convenient. The `backup_cleaner` function has four necessary arguments, which are provided by `backup`:

``` python
def backup_cleaner(source_path, backup_path, paths, system_exception):
    '''Should be called only by the "backup()" function

    source_path (str) - the source directory that are backuped;
    backup_path (str) - the output directory of this backup;
    dirs (set) - all files and folders in "source_path";
    system_exception (tuple) - trash/recycle bin path.
    '''
```

Directories found in the `backup_path` will permit determinate unnecessary files and folders:

``` python
    backup_folders = set()
    backup_files = set()
```

This loop iterates over the `backup_path` and ignores only the `system_exception`:

``` python
    for dir_path, folders, filenames in walk(backup_path):
        # Except default trash/recycle bin paths
        if not any(excepted in dir_path for excepted in system_exception):
```

The logic here reminds the previous `backup` loop, but in this one, our algorithm updates any file with unmatched size:

``` python
            # Count empty folders too
            if folders == [] and filenames == []:
                backup_folders.add(dir_path)
            
            for file in filenames:
                file_path = join_path(dir_path, file)
                backup_files.add(file_path)
                try:
                    source_dir_path = dir_path.replace(backup_path,source_path)
                    source_file_path = join_path(source_dir_path, file)
                    source_file_size = getsize(source_file_path)
                    backup_file_size = getsize(file_path)
                    incomplete_file_path = file_path+INCOMPLETE_EXTENSION

                    # Reload files with same names but different sizes
                    if source_file_size != backup_file_size:
                        copy(source_file_path, incomplete_file_path)
                        remove(file_path)
                        rename(incomplete_file_path, file_path)
                        info(f'Replaced "{file_path}" by "{source_file_path}"')

                except OSError as os_error:
                    error_code = os_error.errno
                    if error_code in (INEXISTENT_FILE, CORRUPTION_ERROR):
                        continue
                    else:
                        error(f'{os_error} in the "backup_cleaner()" function')
                        raise os_error
```

Finally, python compares all `backup_paths` with `paths` provided by the `backup` function and removes unnecessary paths:

``` python
    # Remove unnecessary folders and files
    backup_paths = backup_folders.union(backup_files)
    unnecessary_paths = backup_paths-paths
    unnecessary_paths_quantity = len(unnecessary_paths)
    unnecessary_tree = tuple()
    for unnecessary_path in unnecessary_paths:
        info(f'"{unnecessary_path}" path will be removed from backup')
        if not unnecessary_path.startswith(unnecessary_tree):
            if isfile(unnecessary_path):
                unnecessary_dir = dirname(unnecessary_path)
                source_dir = unnecessary_dir.replace(backup_path, source_path)
                if exists(source_dir):
                    remove(unnecessary_path)
                else:
                    rmtree(unnecessary_dir)
                    unnecessary_paths_quantity += 1
                    unnecessary_tree += (unnecessary_dir,)
                    info(f'"{unnecessary_dir}" path are removed from backup')
            else:
                rmtree(unnecessary_path)
    
    info(f'{unnecessary_paths_quantity} paths are removed\nBackup completed\n')
```
