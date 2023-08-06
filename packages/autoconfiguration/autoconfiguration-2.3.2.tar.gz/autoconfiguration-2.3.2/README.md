# python-autoconfiguration

Load configuration files (.ini) automatically.


## Usage

The `init` function of the `autoconfiguration` package has to be called first to initialize the configuration. Pass an arbitrary amount of configuration files to this function. All passed files will be loaded. Additionally the global configuration file (`config.ini`) will always be loaded by default. The name of the global configuration file has to be `config.ini`. All other files must start with `config-` and end with `.ini`. You don't have to use the full file names for the `init` function. You can just use the name between `config-` and `.ini`.

The `init` function expects a second parameter `config_class`. This should be a dataclass containing all sections of the configuration files. The types of the fields should be dataclasses too. These dataclasses should contain the keys of the respective sections.

Supported data types for keys in the dataclasses:
- str
- int
- float
- complex
- bool
- List
- Tuple
- Dict
- Optional (value will be set to `None` if the key could not be found in the configuration)

Default values are supported too which will be set if the respective key could not be found in the configuration.

The third parameter of the `init` function is the optional `config_dir` parameter. This should be a path to the directory containing the configuration files. Absolute paths are supported. The default is `config`. This works if the name of the directory is `config` and it exists in the directory where the application was executed from.

### Example

config files:

`config.ini`:
```
[section]
key=test
```

`config-dev.ini`:
```
[test]
# % needs to be escaped with another %, so a str containing %% will contain only %
test-complex-str=test %%d 1
    # Lines after the first line have to be indented deeper than the first line
    2 \n\ta
test-int=123
test-bool=False
test-float=0.987
test-complex=1j
test-list=["abc", 123]
test-tuple=(123, "abc")
test-dict={"test": 123, 2: "abc"}
```
---

dataclasses:
```python
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class Section:
    key: str


@dataclass
class Test:
    test_complex_str: str
    test_int: int
    test_bool: bool
    test_float: float
    test_complex: complex
    test_list: List[Any]
    test_tuple: Tuple[int, str]
    test_dict: Dict
    optional: Optional[str]
    default_int: int = 987
    default_list: List[str] = field(default_factory=lambda: [1, 2, 3])


@dataclass
class Config:
    section: Section
    test: Test
```
---

Initialize autoconfiguration:
```python
from autoconfiguration import autoconfiguration

config: Config = autoconfiguration.init("dev", config_class=Config)
```

You can enable auto completion in IDEs by specifying the type of the variable (`config: Config`).

After the autoconfiguration was initialized you can get the configuration from anywhere in your code by calling the `get` function:
```python
from autoconfiguration import autoconfiguration

config: Config = autoconfiguration.get()
```

The instance created by `init` is cached. That means that both the `init` and the `get` function always returns the same instance for a specific config class.

The instance of the config class above looks like:
```python
Config(
    section=Section(key="test"),
    types=Types(
        test_complex_str="test %d 1\n2 \\n\\ta",
        test_int=123,
        test_bool=False,
        test_float=0.987,
        test_complex=1j,
        test_list=["abc", 123],
        test_tuple=(123, "abc"),
        test_dict={"test": 123, 2: "abc"},
        optional=None,
        default_int=987,
        default_list=[1, 2, 3],
    ),
)
```

### Multiple instances

If `init` is called with another config class, autoconfiguration creates and returns a new instance and caches this instance too.

If `get` is called without the config class parameter, it always returns the first cached instance. Pass the config class to `get` to get another instance:
```python
from autoconfiguration import autoconfiguration

config: SecondConfig = autoconfiguration.get(SecondConfig)
```

See `example/main.py` for a complete example.
