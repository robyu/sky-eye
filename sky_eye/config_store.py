import json
from pathlib import Path

class ConfigStore:
    def __init__(self, config_fname):
        assert isinstance(config_fname, Path), f"config_fname must be a Path object, not {type(config_fname)}"
        assert config_fname.exists(), f"{config_fname} does not exist"
        self.config_fname = Path(config_fname).resolve()
        with open(config_fname) as f:
            self.dict = json.load(f)
    
    def __getattr__(self, name):
        if name not in self.dict:
            raise AssertionError(f"({name}) is not a key in the dictionary from {self.config_fname}")
        return self.dict[name]
