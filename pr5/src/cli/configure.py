import configparser
import os
from pathlib import Path
from typing import Union

from src.processor import ProcType
from src.hardware.memory.cache.cache import (
    CacheType,
    CacheConfig,
    ReplacementPolicy,
    WritePolicy,
)
from src.hardware.memory.ram32 import RAMConfig


class ConfigurationError(Exception):
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(msg)


class ConfigReader:
    """
    Configuration Reader
    """

    def __init__(self, config_file: Union[str, Path]):
        self.config = configparser.ConfigParser()

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found.")

        self.config.read(config_file)

    def get_stats_file(self) -> str:  # TODO Returns Path
        """
        Get output `.json` filepath for statistics
        """

        return self.config.get("General", "stats_file")

    def get_num_insts(self) -> int:
        """
        Get the number of instructions to simulate
        """

        return self.config.getint("General", "num_insts")

    def get_start(self) -> int:
        start_hex_str = self.config.get("General", "start")
        return int(start_hex_str, 16)

    def get_log_level(self) -> str:
        return self.config.get("Logging", "log_level")

    def get_processor_type(self) -> ProcType:
        """
        Get the processor type
        """

        proc = self.config.get("Processor", "type")

        match proc:
            case "SingleCycleProcessor":
                return ProcType.SINGLE_CYCLE
            case "PipelinedProcessor":
                return ProcType.STALL_PIPELINE
            case "FPipelinedProcessor":
                return ProcType.FWD_PIPELINE
            case _:
                raise ValueError(f"Invalid processor type: {proc}")

    def get_cache_config(self, cache: CacheType) -> CacheConfig:
        match cache:
            case CacheType.L1I:
                level = "I1_Cache"
            case CacheType.L1D:
                level = "L1_Cache"
            case CacheType.L2:
                level = "L2_Cache"

        valid = self.config.getboolean(level, "valid")
        latency = self.config.getint(level, "latency")
        size = self.config.getint(level, "size")
        block_size = self.config.getint(level, "block_size")
        assoc = self.config.getint(level, "assoc")
        policy = self.config.get(level, "replacement")
        write = self.config.get(level, "write_policy")

        match policy:
            case "FIFO":
                replacement = ReplacementPolicy.FIFO
            case "LRU":
                replacement = ReplacementPolicy.LRU
            case _:
                raise ConfigurationError(f"Invalid Replacement Policy: {policy}")

        match write:
            case "WB":  # writeback
                write_policy = WritePolicy.WRITE_BACK
            case "WT":
                write_policy = WritePolicy.WRITE_THROUGH
            case _:
                raise ConfigurationError(f"Invalid Write Policy: {write}")

        return CacheConfig(
            valid=valid,
            latency=latency,
            cache_size=size,
            block_size=block_size,
            ways=assoc,
            repl_policy=replacement,
            write_policy=write_policy,
        )

    def get_ram_config(self) -> RAMConfig:
        latency = self.config.getint("RAM", "latency")

        return RAMConfig(latency=latency)

    def display_config(self) -> None:
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")
