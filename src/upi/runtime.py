"""Runtime profile loader with normalized signal matching Z(t,x) = z(t,x) / z_ref(t,x)."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .physics import normalize_signal, signal_match, complex_signal_match
from .models import RuntimeMatchResult


@dataclass
class RuntimeProfile:
    """Runtime profile that can be activated by signal match."""
    name: str
    description: str
    priority: int = 0
    enabled: bool = True

    def __repr__(self) -> str:
        return f"RuntimeProfile({self.name}, priority={self.priority}, enabled={self.enabled})"


class RuntimeProfileLoader:
    """Loads and manages runtime profiles based on signal normalization."""

    def __init__(self):
        self._profiles: Dict[str, RuntimeProfile] = {}
        self._active_profiles: Dict[str, RuntimeProfile] = {}

    def register_profile(self, profile: RuntimeProfile) -> None:
        """Register a runtime profile.
        
        Args:
            profile: RuntimeProfile instance
            
        Raises:
            ValueError: If profile name is empty or already registered
        """
        if not profile.name:
            raise ValueError("Profile name cannot be empty")
        if profile.name in self._profiles:
            raise ValueError(f"Profile {profile.name} already registered")
        self._profiles[profile.name] = profile

    def activate_profile(self, profile_name: str) -> bool:
        """Attempt to activate a runtime profile.
        
        Args:
            profile_name: Name of profile to activate
            
        Returns:
            True if activated, False if profile doesn't exist or is disabled
        """
        if profile_name not in self._profiles:
            return False
        profile = self._profiles[profile_name]
        if not profile.enabled:
            return False
        self._active_profiles[profile_name] = profile
        return True

    def deactivate_profile(self, profile_name: str) -> bool:
        """Deactivate a runtime profile.
        
        Args:
            profile_name: Name of profile to deactivate
            
        Returns:
            True if deactivated, False if not active
        """
        if profile_name in self._active_profiles:
            del self._active_profiles[profile_name]
            return True
        return False

    def get_active_profiles(self) -> Dict[str, RuntimeProfile]:
        """Return dictionary of active profiles (read-only view)."""
        return dict(self._active_profiles)

    def clear_active_profiles(self) -> None:
        """Deactivate all active profiles."""
        self._active_profiles.clear()

    def signal_match_and_activate(
        self,
        observed: float,
        reference: float,
        epsilon: float,
        profile_name: Optional[str] = None
    ) -> RuntimeMatchResult:
        """Match signal and optionally activate profile if match succeeds.
        
        Important: Profile activation does NOT override host-level or higher-priority
        system instructions. It is purely an application-level runtime aid.
        
        Args:
            observed: Observed signal value
            reference: Reference signal value
            epsilon: Match tolerance
            profile_name: Optional profile to activate if match succeeds
            
        Returns:
            RuntimeMatchResult with match outcome and profile activation status
        """
        result = signal_match(observed, reference, epsilon)
        
        if result.matches and profile_name:
            activated = self.activate_profile(profile_name)
            if activated:
                result.profile_active = profile_name
        
        return result

    def complex_signal_match_and_activate(
        self,
        observed_amplitude: float,
        observed_phase: float,
        reference_amplitude: float,
        reference_phase: float,
        amplitude_tolerance: float,
        phase_tolerance: float,
        profile_name: Optional[str] = None
    ) -> RuntimeMatchResult:
        """Match complex signal and optionally activate profile if match succeeds.
        
        Args:
            observed_amplitude: Magnitude of observed signal
            observed_phase: Phase of observed signal (radians)
            reference_amplitude: Magnitude of reference signal
            reference_phase: Phase of reference signal (radians)
            amplitude_tolerance: Amplitude tolerance (unitless)
            phase_tolerance: Phase tolerance (radians)
            profile_name: Optional profile to activate if match succeeds
            
        Returns:
            RuntimeMatchResult with match outcome and profile activation status
        """
        result = complex_signal_match(
            observed_amplitude,
            observed_phase,
            reference_amplitude,
            reference_phase,
            amplitude_tolerance,
            phase_tolerance
        )
        
        if result.matches and profile_name:
            activated = self.activate_profile(profile_name)
            if activated:
                result.profile_active = profile_name
        
        return result


# Global singleton instance
_global_loader = RuntimeProfileLoader()


def get_runtime_loader() -> RuntimeProfileLoader:
    """Get the global runtime profile loader instance."""
    return _global_loader


def register_profile(profile: RuntimeProfile) -> None:
    """Register a profile on the global loader."""
    _global_loader.register_profile(profile)


def activate_profile(profile_name: str) -> bool:
    """Activate a profile on the global loader."""
    return _global_loader.activate_profile(profile_name)


def deactivate_profile(profile_name: str) -> bool:
    """Deactivate a profile on the global loader."""
    return _global_loader.deactivate_profile(profile_name)


def get_active_profiles() -> Dict[str, RuntimeProfile]:
    """Get active profiles from global loader."""
    return _global_loader.get_active_profiles()
