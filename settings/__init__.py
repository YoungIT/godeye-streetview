import hydra
from omegaconf import DictConfig, OmegaConf

from loguru import logger

def load_config (cfg: DictConfig) -> DictConfig:
    logger.info(f"\nConfigs: \n {OmegaConf.to_yaml(cfg)}")

    return cfg 

config_path = OmegaConf.load("settings/config.yaml")
config = load_config(config_path)