"""
Skill tracking system for monitoring XP gains and levels across game sessions.
Provides real-time tracking and summary statistics for any skill.
"""

from typing import Optional, Dict
import time


class SkillTracker:
    """
    Tracks XP and level progress for a specific skill.
    
    Features:
    - Starting and current XP/level tracking
    - Session duration monitoring
    - XP gain calculations
    - XP per hour metrics
    """
    
    def __init__(self, skill_name: str, api):
        """
        Initialize skill tracker.
        
        Args:
            skill_name: Name of the skill to track (e.g., "Mining", "Woodcutting")
            api: RuneLiteAPI instance for fetching stats
        """
        self.skill_name = skill_name
        self.api = api
        
        # Session tracking
        self.session_start_time = time.time()
        self.starting_xp: Optional[int] = None
        self.starting_level: Optional[int] = None
        self.current_xp: Optional[int] = None
        self.current_level: Optional[int] = None
        
        # Gain tracking
        self.last_xp_check_time = time.time()
        self.xp_gains: list[tuple[float, int]] = []  # (timestamp, xp_gained)
    
    def start_tracking(self) -> bool:
        """
        Begin tracking by recording initial stats.
        
        Returns:
            True if successfully started tracking, False otherwise
        """
        stats = self._get_skill_stats()
        if not stats:
            print(f"✗ Failed to get starting {self.skill_name} stats")
            return False
        
        self.starting_xp = stats['xp']
        self.starting_level = stats['level']
        self.current_xp = stats['xp']
        self.current_level = stats['level']
        self.session_start_time = time.time()
        self.last_xp_check_time = time.time()
        
        print(f"✓ Started tracking {self.skill_name} - Level {self.starting_level} ({self.starting_xp:,} XP)")
        return True
    
    def update(self) -> Optional[Dict]:
        """
        Update current stats and calculate gains.
        
        Returns:
            Dictionary with gain info if XP changed, None otherwise
        """
        stats = self._get_skill_stats()
        if not stats:
            return None
        
        new_xp = stats['xp']
        new_level = stats['level']
        
        # Check if XP changed
        if new_xp != self.current_xp:
            xp_gained = new_xp - self.current_xp
            level_gained = new_level - self.current_level
            
            # Record gain
            current_time = time.time()
            self.xp_gains.append((current_time, xp_gained))
            self.last_xp_check_time = current_time
            
            # Update current stats
            old_xp = self.current_xp
            old_level = self.current_level
            self.current_xp = new_xp
            self.current_level = new_level
            
            return {
                'xp_gained': xp_gained,
                'level_gained': level_gained,
                'old_xp': old_xp,
                'old_level': old_level,
                'new_xp': new_xp,
                'new_level': new_level
            }
        
        return None
    
    def get_session_stats(self) -> Dict:
        """
        Get comprehensive session statistics.
        
        Returns:
            Dictionary with session metrics
        """
        if self.starting_xp is None or self.current_xp is None:
            return {}
        
        if self.starting_level is None or self.current_level is None:
            return {}
        
        session_duration = time.time() - self.session_start_time
        total_xp_gained = self.current_xp - self.starting_xp
        levels_gained = self.current_level - self.starting_level
        
        # Calculate XP per hour
        hours = session_duration / 3600
        xp_per_hour = int(total_xp_gained / hours) if hours > 0 else 0
        
        return {
            'skill': self.skill_name,
            'starting_level': self.starting_level,
            'current_level': self.current_level,
            'levels_gained': levels_gained,
            'starting_xp': self.starting_xp,
            'current_xp': self.current_xp,
            'total_xp_gained': total_xp_gained,
            'session_duration': session_duration,
            'xp_per_hour': xp_per_hour,
            'session_duration_formatted': self._format_duration(session_duration)
        }
    
    def print_session_summary(self):
        """Print formatted session summary."""
        stats = self.get_session_stats()
        if not stats:
            print("No session data available")
            return
        
        print("\n" + "="*50)
        print(f"{stats['skill'].upper()} SESSION SUMMARY")
        print("="*50)
        print(f"Duration:       {stats['session_duration_formatted']}")
        print(f"Starting Level: {stats['starting_level']} ({stats['starting_xp']:,} XP)")
        print(f"Current Level:  {stats['current_level']} ({stats['current_xp']:,} XP)")
        print(f"Levels Gained:  {stats['levels_gained']}")
        print(f"XP Gained:      {stats['total_xp_gained']:,}")
        print(f"XP/Hour:        {stats['xp_per_hour']:,}")
        print("="*50 + "\n")
    
    def _get_skill_stats(self) -> Optional[Dict]:
        """
        Fetch current skill stats from API.
        
        Returns:
            Dictionary with 'level' and 'xp', or None on error
        """
        try:
            stats = self.api.get_stats()
            if not stats or 'skills' not in stats:
                return None
            
            skill_key = self.skill_name.lower()
            skill_data = stats['skills'].get(skill_key)
            
            if skill_data:
                return {
                    'level': skill_data.get('level'),
                    'xp': skill_data.get('xp')
                }
        except Exception as e:
            print(f"Error fetching {self.skill_name} stats: {e}")
        
        return None
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to readable string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
