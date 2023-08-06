# logging_utils
logging consists of the following classes and functions to help with the burden of logging


### RelativePathRotatingFileHandler
Not sure if this is working properly

#### get_logger()
This function retrieves a logger for your file and function/method.  This should be called first.  For example:

#### start_function(logger, **kwargs)
This function tags the log file with the entry of a function/method.  You may turn it on or off in your logging configuration
note that the __msg=__ argument is reserved for single string messages

#### end_function(logger, **kwargs)
This function tags the log file with the exit of a function/method.  You may turn it on or off in your logging configuration
note that the __msg=__ argument is reserved for single string messages

Here is an example of everything
```python
    val1 = 5
    val2 = 6
    logger = get_logger()
    start_function(logger, msg="testing")

    # or you can call it this way:
    start_function(logger, val1=val1, val2=val2)
    val1 = 10
    val2 = {"first": 1, "second": 2}
    end_function(logger, val1=val1, val2=val2)

```
# os_utils
os consists of the following classes and functions

#### UnhandledOs
This is raised when the library does not recognize the operating system

#### list_timezones()
This function returns all known timezones

#### get_timezone()
This function returns the timezone selected by the operating system

#### kill_process(name)
This function kills the specified process name

#### is_running(name)
This function returns whether the specified process name is currently running

#### os_type()
This function returns the operating system type

#### get_ip_addresses()
This function returns all IP addresses on this hardware

#config
This contains the object __ConfigUtils__
It is used to read and write .ini files.  You should put all information into the different
methods to fully define the configuration file.

The constructor takes the configuration file name, a title to add to the top of the file, and a flag indicating
the file is being constructed.
```python
class ConfigManager:
    def __init__(self, file_name, title=None, create=False):
```

The read_entry function reads a section/entry from the file.  It takes a default value in case the value
does not exist in the file and also to create a new file.  The notes parameter describe the entry in the file
```python
    def read_entry(self, section, entry, default_value, notes=None):
```

The read_section function reads the entire section from the configuration file and returns 
a dictionary of the entries.  Note that the notes are only applied to the setion (not to the individual entries)
```python
    def read_section(self, section, default_entries, notes=None):
```

The write function writes a new configuration file.  If this is called, the package will check if the file exists.
If it does, it will abort with a warning.  If the file does not exist, it will write it and abort.
```python
    def write(self, out_file):
```

Here is an example of ConfigManager and its functions:
```python
    write = False # set this to True to create the configuration file
    cfg_mgr = ConfigManager("test.ini", "This is the title of the ini file\n"
                                        "You can have multiple lines if you use line breaks", write)
    first = cfg_mgr.read_entry("User 1", "first name", "Joe", "This is the first name")
    last = cfg_mgr.read_entry("User 1", "last name", "Brown", "This is the last name")
    age = cfg_mgr.read_entry("User 1", "age", 12)
    is_male = cfg_mgr.read_entry("User 1", "male", True)
    weight = cfg_mgr.read_entry("User 1", "weight", 23.5)
    section = cfg_mgr.read_section("user 2", {"first name": "Sally",
                                              "last name": "Jones",
                                              "age": 15,
                                              "is_male": False,
                                              "weight": 41.3},
                                   "You only get to add notes at the top of the section using this method")

```