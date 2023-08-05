obis - file organization


## `obis/scripts`

* `obis/scripts/cli.py` all **command-line commands**, implemented with the click library


* `obis/scripts/click_util.py` a few utilities, e.g. **echo**

* `obis/scripts/data_mgmt_runner.py` a few os routines to **initialize data and metadata paths** as well to **validate** obis' metadata
folder.


## `obis/dm` 

**Various Utilities**

* `checksum.py` generates SHA256, CRC32, MD5 and WORM **checksums**
* `utils.py` contains **OS-related helper scripts**, such as `complete_openbis_config`, `complete_git_config`, `run_shell`, `locate_command`, `cd`
* `repository_utils.py` contains **repository commands** like `copy_repository`, `delete_repository`, `get_repository_location`, `is_local`
* `command_log.py` **write log-output** to `~/.obis/log`. If a command is success, remove it from the log. If command fails, a log entry creates an error. A user must then manually remove the log entry in order to continue
* `command_result.py` Encapsulate result from a subprocess call

**setting utilities**

* `config.py` handle configuration settings, read and write config files from global and user_config
* `config_test.py` test for the above
* `git-annex-attributes` settings for **git-annex**. Files **>100kb** are considered to be **large files**, as well as all **.zip .tar .gz** files 

**main programs**

* `git.py` A wrapper on commands to git and git annex. Uses `checksum.py` for checksums.
* `data_mgmt.py` **Main program**. 
* `data_mgmt_test.py` test for the above

## `obis/dm/commands`

* `addref.py` add the current folder, which is supposed to be an obis repository, as a **new content copy** to openBIS
* `removeref.py` the opposite of `addref.py`: remove content copy from dataset and repository
* `clone.py` implements the **git clone** command and validates checksums
* `download.py` download files of a data set, using **big data link server**
* `move.py` implements the move command. Uses **clone**, then **deletes the old content** copy in openBIS and **deletes the repository** from the old location.
