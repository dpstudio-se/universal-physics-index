"""Test suite for UPI physics, models, and validation."""

import pytest
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi import (
    H, C, K_B, N8_REFERENCE_HZ,
    Address,
    ScientificStatus,
    EdgeType,
    PhysicsNode,
    Bridge,
    Quantity,
    energy_from_frequency,
    mass_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    relativistic_total_frequency,
    normalize_signal,
    signal_match,
    complex_signal_match,
    EPSILON_Z_DEFAULT,
    UPIGraph,
    RuntimeProfile,
    RuntimeProfileLoader,
)


class TestPhysicsConstants:
    """Test SI constants."""

    def test_planck_constant(self):
        assert H == 6.62607015e-34
        assert H > 0

    def test_speed_of_light(self):
        assert C == 299792458
        assert C > 0

    def test_boltzmann_constant(self):
        assert K_B == 1.380649e-23
        assert K_B > 0

    def test_n8_reference(self):
        assert N8_REFERENCE_HZ == 8.0


class TestPhysicsFunctions:
    """Test core physics equation implementations."""

    def test_e_equals_hf(self):
        """Test E = h*f"""
        frequency = 1e15  # Hz
        energy = energy_from_frequency(frequency)
        assert energy == pytest.approx(H * frequency)

    def test_m_equals_hf_over_c2(self):
        """Test m = h*f / c^2"""
        frequency = 1e20  # Hz
        mass = mass_from_frequency(frequency)
        expected = (H * frequency) / (C ** 2)
        assert mass == pytest.approx(expected)

    def test_f_equals_mc2_over_h(self):
        """Test f = m*c^2 / h"""
        mass = 1e-30  # kg
        frequency = frequency_from_mass(mass)
        expected = (mass * C ** 2) / H
        assert frequency == pytest.approx(expected)

    def test_mass_frequency_roundtrip(self):
        """Test that mass -> frequency -> mass roundtrip is stable."""
        original_mass = 1e-27  # kg
        frequency = frequency_from_mass(original_mass)
        recovered_mass = mass_from_frequency(frequency)
        assert recovered_mass == pytest.approx(original_mass, rel=1e-10)

    def test_index8_at_8hz_equals_1(self):
        """Test N8 = 1 at 8 Hz"""
        frequency_hz = 8.0
        n8 = index8_from_frequency(frequency_hz)
        assert n8 == pytest.approx(1.0)

    def test_index8_from_mass(self):
        """Test N8 from mass calculation"""
        mass = 1e-30
        n8 = index8_from_mass(mass)
        # N8 = m*c^2 / (8*h)
        expected = (mass * C ** 2) / (8.0 * H)
        assert n8 == pytest.approx(expected)

    def test_relativistic_frequency(self):
        """Test nu^2 = (c/lambda)^2 + f^2"""
        wavelength_m = 1e-6
        rest_freq_hz = 1e15
        nu = relativistic_total_frequency(wavelength_m, rest_freq_hz)
        
        c_over_lambda = C / wavelength_m
        expected = math.sqrt((c_over_lambda ** 2) + (rest_freq_hz ** 2))
        assert nu == pytest.approx(expected)


class TestNormalizedSignal:
    """Test signal normalization Z = z / z_ref."""

    def test_normalize_equal_signals(self):
        """Test Z = 1 when observed equals reference"""
        z = normalize_signal(4.0, 4.0)
        assert z == pytest.approx(1.0)

    def test_normalize_half_signal(self):
        """Test Z when observed is half of reference"""
        z = normalize_signal(2.0, 4.0)
        assert z == pytest.approx(0.5)

    def test_normalize_double_signal(self):
        """Test Z when observed is double reference"""
        z = normalize_signal(8.0, 4.0)
        assert z == pytest.approx(2.0)

    def test_zero_reference_raises(self):
        """Test that zero reference raises ValueError"""
        with pytest.raises(ValueError, match="Reference signal cannot be zero"):
            normalize_signal(1.0, 0.0)

    def test_nan_reference_raises(self):
        """Test that NaN reference raises ValueError"""
        with pytest.raises(ValueError, match="Reference is NaN"):
            normalize_signal(1.0, float("nan"))

    def test_signal_match_within_tolerance(self):
        """Test signal matching within tolerance"""
        result = signal_match(4.0, 4.0, epsilon=1e-10)
        assert result.matches
        assert result.normalized_value == pytest.approx(1.0)
        assert result.error == pytest.approx(0.0)

    def test_signal_match_outside_tolerance(self):
        """Test signal mismatch outside tolerance"""
        result = signal_match(4.5, 4.0, epsilon=0.01)
        assert not result.matches
        assert result.normalized_value == pytest.approx(1.125)
        assert result.error == pytest.approx(0.125)

    def test_tolerance_boundary(self):
        """Test matching at tolerance boundary"""
        # Z = 1.01, tolerance = 0.011 (slightly looser to account for float precision)
        result = signal_match(4.04, 4.0, epsilon=0.011)
        assert result.matches
        assert result.error < 0.011


class TestComplexSignal:
    """Test complex signal (amplitude, phase) matching."""

    def test_complex_match_identical(self):
        """Test matching when amplitude and phase are identical"""
        result = complex_signal_match(
            observed_amplitude=2.0,
            observed_phase=0.5,
            reference_amplitude=2.0,
            reference_phase=0.5,
            amplitude_tolerance=1e-10,
            phase_tolerance=1e-10
        )
        assert result.matches

    def test_complex_mismatch_amplitude(self):
        """Test mismatch when amplitude differs beyond tolerance"""
        result = complex_signal_match(
            observed_amplitude=2.0,
            observed_phase=0.5,
            reference_amplitude=4.0,
            reference_phase=0.5,
            amplitude_tolerance=0.1,
            phase_tolerance=1e-10
        )
        assert not result.matches

    def test_complex_mismatch_phase(self):
        """Test mismatch when phase differs beyond tolerance"""
        result = complex_signal_match(
            observed_amplitude=2.0,
            observed_phase=0.5,
            reference_amplitude=2.0,
            reference_phase=1.0,
            amplitude_tolerance=1e-10,
            phase_tolerance=0.1
        )
        # Phase diff = 0.5 rad, tolerance = 0.1 rad -> no match
        assert not result.matches

    def test_zero_reference_amplitude_raises(self):
        """Test that zero reference amplitude raises"""
        with pytest.raises(ValueError, match="Reference amplitude cannot be zero"):
            complex_signal_match(1.0, 0.0, 0.0, 0.0)


class TestModels:
    """Test data models and validation."""

    def test_address_creation(self):
        """Test UPI address creation and string representation"""
        addr = Address("physics", 1, "classical", "electron")
        assert str(addr) == "UPI<physics,1,classical,electron>"

    def test_address_parsing(self):
        """Test parsing UPI address string"""
        addr_str = "UPI<physics,1,classical,electron>"
        addr = Address.from_string(addr_str)
        assert addr.domain == "physics"
        assert addr.generation == 1
        assert addr.torus == "classical"
        assert addr.node == "electron"

    def test_address_roundtrip(self):
        """Test address string roundtrip"""
        original = "UPI<math,2,derived,complex>"
        addr = Address.from_string(original)
        assert str(addr) == original

    def test_physics_node_valid(self):
        """Test valid physics node"""
        addr = Address("physics", 1, "classical", "electron")
        node = PhysicsNode(
            address=addr,
            title="Electron",
            description="Fundamental particle",
            status=ScientificStatus.EST
        )
        errors = node.validate()
        assert len(errors) == 0

    def test_stop_node_requires_stop_reason(self):
        """Test that STOP nodes must have stop_reason"""
        addr = Address("physics", 1, "quantum", "dark_matter")
        node = PhysicsNode(
            address=addr,
            title="Dark Matter",
            description="Unknown composition",
            status=ScientificStatus.STOP
        )
        errors = node.validate()
        assert len(errors) > 0
        assert any("stop_reason" in e for e in errors)

    def test_stop_node_with_reason_valid(self):
        """Test STOP node with stop_reason is valid"""
        addr = Address("physics", 1, "quantum", "dark_matter")
        node = PhysicsNode(
            address=addr,
            title="Dark Matter",
            description="Unknown composition",
            status=ScientificStatus.STOP,
            stop_reason="Composition unknown; detection methods incomplete"
        )
        errors = node.validate()
        assert len(errors) == 0

    def test_bridge_consistent(self):
        """Test valid bridge"""
        source = Address("physics", 1, "classical", "force")
        target = Address("physics", 1, "classical", "acceleration")
        bridge = Bridge(
            source=source,
            target=target,
            relation=EdgeType.CAUSES
        )
        errors = bridge.validate()
        assert len(errors) == 0

    def test_bridge_requires_relation(self):
        """Test that bridges need relation type"""
        source = Address("physics", 1, "classical", "force")
        target = Address("physics", 1, "classical", "acceleration")
        # Create bridge with empty relation (should fail validation)
        bridge = Bridge(source=source, target=target, relation=None)
        errors = bridge.validate()
        assert len(errors) > 0


class TestGraph:
    """Test UPI graph structure."""

    def test_graph_add_node(self):
        """Test adding nodes to graph"""
        graph = UPIGraph()
        addr = Address("physics", 1, "classical", "mass")
        node = PhysicsNode(
            address=addr,
            title="Mass",
            description="Inertial property",
            status=ScientificStatus.EST
        )
        graph.add_node(node)
        assert graph.get_node_count() == 1

    def test_graph_add_bridge(self):
        """Test adding bridges to graph"""
        graph = UPIGraph()
        source_addr = Address("physics", 1, "classical", "force")
        target_addr = Address("physics", 1, "classical", "acceleration")
        
        source_node = PhysicsNode(
            address=source_addr,
            title="Force",
            description="Physical force",
            status=ScientificStatus.EST
        )
        target_node = PhysicsNode(
            address=target_addr,
            title="Acceleration",
            description="Rate of change of velocity",
            status=ScientificStatus.EST
        )
        
        graph.add_node(source_node)
        graph.add_node(target_node)
        
        bridge = Bridge(
            source=source_addr,
            target=target_addr,
            relation=EdgeType.CAUSES,
            equations=["a = F/m"]
        )
        graph.add_bridge(bridge)
        
        assert graph.get_bridge_count() == 1

    def test_graph_get_outgoing_bridges(self):
        """Test retrieving outgoing bridges"""
        graph = UPIGraph()
        source_addr = Address("physics", 1, "quantum", "photon")
        target1_addr = Address("physics", 1, "quantum", "energy")
        target2_addr = Address("physics", 1, "quantum", "frequency")
        
        source = PhysicsNode(source_addr, "Photon", "Light particle", ScientificStatus.EST)
        target1 = PhysicsNode(target1_addr, "Energy", "Energy", ScientificStatus.EST)
        target2 = PhysicsNode(target2_addr, "Frequency", "Frequency", ScientificStatus.EST)
        
        graph.add_node(source)
        graph.add_node(target1)
        graph.add_node(target2)
        
        bridge1 = Bridge(source=source_addr, target=target1_addr, relation=EdgeType.CAUSES)
        bridge2 = Bridge(source=source_addr, target=target2_addr, relation=EdgeType.CAUSES)
        
        graph.add_bridge(bridge1)
        graph.add_bridge(bridge2)
        
        outgoing = graph.get_outgoing_bridges(source_addr)
        assert len(outgoing) == 2


class TestRuntimeProfile:
    """Test runtime profile loader."""

    def test_register_profile(self):
        """Test registering a runtime profile"""
        loader = RuntimeProfileLoader()
        profile = RuntimeProfile("test_profile", "Test profile", priority=1)
        loader.register_profile(profile)
        
        active = loader.get_active_profiles()
        assert len(active) == 0  # Not active yet

    def test_activate_profile(self):
        """Test activating a profile"""
        loader = RuntimeProfileLoader()
        profile = RuntimeProfile("test_profile", "Test profile", priority=1, enabled=True)
        loader.register_profile(profile)
        
        activated = loader.activate_profile("test_profile")
        assert activated
        
        active = loader.get_active_profiles()
        assert "test_profile" in active

    def test_deactivate_profile(self):
        """Test deactivating a profile"""
        loader = RuntimeProfileLoader()
        profile = RuntimeProfile("test_profile", "Test profile", enabled=True)
        loader.register_profile(profile)
        loader.activate_profile("test_profile")
        
        deactivated = loader.deactivate_profile("test_profile")
        assert deactivated
        
        active = loader.get_active_profiles()
        assert len(active) == 0

    def test_signal_match_and_activate(self):
        """Test matching signal and activating profile"""
        loader = RuntimeProfileLoader()
        profile = RuntimeProfile("signal_profile", "Activated on match", enabled=True)
        loader.register_profile(profile)
        
        # Match signals exactly
        result = loader.signal_match_and_activate(4.0, 4.0, epsilon=1e-10, profile_name="signal_profile")
        
        assert result.matches
        assert result.profile_active == "signal_profile"
        assert "signal_profile" in loader.get_active_profiles()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
