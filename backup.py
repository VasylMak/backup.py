# backup.py - Simple and flexible backup algorithm written for humans


__license__ = 'MIT'
__author__ = 'Vasyl Makoviichuk'
__email__ = 'vasyl@workmail.com'


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


# Logging configuration
chdir(dirname(__file__))
log_format = '%(asctime)s - %(levelname)s - %(message)s'
basic_config(filename='backup.log', level=INFO, format=log_format)

TRASH = ('/.Trash', '/Trash')
RECYCLE_BIN = (':\$RECYCLE.BIN',)
INCOMPLETE_EXTENSION = '.incomplete'

INEXISTENT_FILE = 2
CORRUPTION_ERROR = 22


def backup_cleaner(source_path, backup_path, paths, system_exception):
    '''Should be called only by the "backup()" function

    source_path (str) - the source directory that are backuped;
    backup_path (str) - the output directory of this backup;
    dirs (set) - all files and folders in "source_path";
    system_exception (tuple) - trash/recycle bin path.
    '''
    # Backup found directories
    backup_folders = set()
    backup_files = set()

    for dir_path, folders, filenames in walk(backup_path):
        # Except default trash/recycle bin paths
        if not any(excepted in dir_path for excepted in system_exception):
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
                

def backup(source_path, backup_path, excepted_paths=None, clean_backup=False):
    '''Backup files from "source_path" to "backup_path"

    Parameters:
        source_path (str) - the source directory to be backuped;
        backup_path (str) - the output directory of the backup;
        excepted_paths (tuple) - unnecessary "source_path" directories;
        clean_backup (boolean) - removes extra files in "backup_path".
    '''
    # Except trash/recycle bin
    if name == 'posix':
        system_exception = TRASH
    elif name == 'nt':
        system_exception = RECYCLE_BIN
    
    # Check user exceptions
    if excepted_paths is not None:
        excepted_paths = system_exception+excepted_paths
    else:
        excepted_paths = system_exception
    warning(f'Excepted paths -> {"; ".join(path for path in excepted_paths)}')
    
    # Source found directories
    expected_folders = set()
    expected_files = set()
    backuped_paths = 0
    
    for dir_path, folders, filenames in walk(source_path):
        # Except all exceptions
        if not any(excepted in dir_path for excepted in excepted_paths):
            # Copy empty folders too
            if folders == [] and filenames == []:
                backup_folder_path = dir_path.replace(source_path, backup_path)
                expected_folders.add(backup_folder_path)
                if not exists(backup_folder_path):
                    makedirs(backup_folder_path)
                    info(f'Folder "{backup_folder_path}" is created')
                    backuped_paths += 1

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
                
                except OSError as os_error:
                    error_code = os_error.errno
                    if error_code == CORRUPTION_ERROR:
                        critical(f'File "{file_path}" is corrupted')
                    else:
                        error(f'{os_error} in the "backup()" function')
                        raise os_error

    paths = expected_folders.union(expected_files)
    info(f'{len(paths)} paths are processed')
    info(f'{backuped_paths} paths are backuped')
    
    # Warning: This function removes all unmatched data in backup paths
    if clean_backup:
        warning('Backup cleaner deletes all inconsistent paths in the backup')
        backup_cleaner(source_path, backup_path, paths, system_exception)
    else:
        info(f'"clear_backup" argument is set to "False"\nBackup completed\n')


#backup('D:\\', 'E:\\')
