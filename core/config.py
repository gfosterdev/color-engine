"""
Configuration management system for OSRS bot profiles.

Loads and validates JSON configuration files from the config/ directory.
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class MouseConfig:
    """Mouse movement configuration."""
    speed_min: float = 0.5
    speed_max: float = 1.2
    click_delay_min: float = 0.05
    click_delay_max: float = 0.15
    hold_time_min: float = 0.05
    hold_time_max: float = 0.12
    randomize_trajectory: bool = True
    
    def validate(self):
        """Validate mouse configuration values."""
        if self.speed_min <= 0 or self.speed_max <= 0:
            raise ValueError("Mouse speeds must be positive")
        if self.speed_min > self.speed_max:
            raise ValueError("speed_min cannot be greater than speed_max")
        if self.click_delay_min > self.click_delay_max:
            raise ValueError("click_delay_min cannot be greater than click_delay_max")


@dataclass
class BreakConfig:
    """Break scheduling configuration."""
    enabled: bool = True
    frequency_min: int = 30  # minutes
    frequency_max: int = 90
    duration_min: int = 5
    duration_max: int = 20
    randomize: bool = True
    
    def validate(self):
        """Validate break configuration values."""
        if self.frequency_min <= 0 or self.duration_min <= 0:
            raise ValueError("Break times must be positive")
        if self.frequency_min > self.frequency_max:
            raise ValueError("frequency_min cannot be greater than frequency_max")
        if self.duration_min > self.duration_max:
            raise ValueError("duration_min cannot be greater than duration_max")


@dataclass
class AntiBanConfig:
    """Anti-ban behavior configuration."""
    enabled: bool = True
    idle_actions: bool = True
    camera_movements: bool = True
    tab_switching: bool = True
    random_misclicks: bool = False
    fatigue_simulation: bool = True
    attention_shifts: bool = True
    
    # Idle action frequency (seconds between actions)
    idle_frequency_min: float = 10.0
    idle_frequency_max: float = 45.0


@dataclass
class WindowConfig:
    """Game window configuration."""
    title: str = "RuneLite - xJawj"
    exact_match: bool = True
    client_mode: str = "fixed"  # Must be 'fixed' for consistent positioning
    
    def validate(self):
        """Validate window configuration."""
        if self.client_mode != "fixed":
            raise ValueError("Only 'fixed' client mode is supported")


@dataclass
class BotConfig:
    """Complete bot configuration."""
    profile_name: str
    window: WindowConfig = field(default_factory=WindowConfig)
    mouse: MouseConfig = field(default_factory=MouseConfig)
    breaks: BreakConfig = field(default_factory=BreakConfig)
    anti_ban: AntiBanConfig = field(default_factory=AntiBanConfig)
    skill_settings: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self):
        """Validate all configuration sections."""
        self.window.validate()
        self.mouse.validate()
        self.breaks.validate()
        
        if not self.profile_name:
            raise ValueError("profile_name is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


class ConfigLoader:
    """Manages loading and saving bot configuration profiles."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the config loader.
        
        Args:
            config_dir: Base directory for configuration files
        """
        self.config_dir = Path(config_dir)
        self.profiles_dir = self.config_dir / "profiles"
        
        # Ensure directories exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def load_profile(self, profile_name: str) -> BotConfig:
        """
        Load a bot configuration profile from JSON.
        
        Args:
            profile_name: Name of the profile (without .json extension)
            
        Returns:
            BotConfig object
            
        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If configuration is invalid
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")
        
        with open(profile_path, 'r') as f:
            data = json.load(f)
        
        # Parse nested configurations
        config = BotConfig(
            profile_name=profile_name,
            window=WindowConfig(**data.get('window', {})),
            mouse=MouseConfig(**data.get('mouse', {})),
            breaks=BreakConfig(**data.get('breaks', {})),
            anti_ban=AntiBanConfig(**data.get('anti_ban', {})),
            skill_settings=data.get('skill_settings', {})
        )
        
        # Validate configuration
        config.validate()
        
        return config
    
    def save_profile(self, config: BotConfig) -> None:
        """
        Save a bot configuration profile to JSON.
        
        Args:
            config: BotConfig object to save
        """
        config.validate()
        
        profile_path = self.profiles_dir / f"{config.profile_name}.json"
        
        with open(profile_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
    
    def list_profiles(self) -> List[str]:
        """
        List all available profile names.
        
        Returns:
            List of profile names (without .json extension)
        """
        return [
            f.stem for f in self.profiles_dir.glob("*.json")
        ]
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a configuration profile.
        
        Args:
            profile_name: Name of the profile to delete
            
        Returns:
            True if deleted, False if not found
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        if profile_path.exists():
            profile_path.unlink()
            return True
        return False
    
    def create_default_profile(self, profile_name: str, skill: str = "mining") -> BotConfig:
        """
        Create a default configuration profile for a skill.
        
        Args:
            profile_name: Name for the new profile
            skill: Skill to create defaults for
            
        Returns:
            BotConfig with default settings
        """
        config = BotConfig(profile_name=profile_name)
        
        # Add skill-specific defaults
        if skill == "mining":
            config.skill_settings = {
                "skill": "mining",
                "ore_type": "iron_ore",
                "banking": True,
                "powermine": False,
                "location": "varrock_west"
            }
        elif skill == "woodcutting":
            config.skill_settings = {
                "skill": "woodcutting",
                "tree_type": "oak_tree",
                "banking": False,
                "drop_logs": True,
                "location": "varrock_west"
            }
        elif skill == "fishing":
            config.skill_settings = {
                "skill": "fishing",
                "spot_type": "fishing_spot_net",
                "banking": True,
                "drop_fish": False,
                "location": "lumbridge_swamp"
            }
        
        return config


# Global config loader instance
_loader = ConfigLoader()


def get_loader() -> ConfigLoader:
    """Get the global ConfigLoader instance."""
    return _loader


def load_profile(profile_name: str) -> BotConfig:
    """Load a profile using the global loader."""
    return _loader.load_profile(profile_name)


def save_profile(config: BotConfig) -> None:
    """Save a profile using the global loader."""
    _loader.save_profile(config)
