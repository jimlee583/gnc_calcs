"""
Unit tests for Orbital Dynamics Service.

Tests cover:
- Keplerian orbital mechanics correctness
- Known orbit test cases (LEO, GEO, Molniya)
- Vis-viva equation verification
- Conservation of specific energy and angular momentum
- Apsis calculations
"""

import numpy as np
import pytest

from app.schemas.gnc import OrbitalInput
from app.services.gnc.orbital_dynamics import compute_orbital_dynamics

from .conftest import MU_EARTH, R_EARTH


class TestOrbitalPeriod:
    """Tests for orbital period calculations using Kepler's third law."""

    def test_circular_leo_period(self, circular_leo):
        """LEO at 400 km should have ~92.5 minute period."""
        result = compute_orbital_dynamics(circular_leo)

        # T = 2π * sqrt(a³/μ)
        a = R_EARTH + 400.0  # 6778.137 km
        expected_period = 2 * np.pi * np.sqrt(a**3 / MU_EARTH)

        assert abs(result.orbital_period - expected_period) < 0.01
        # Should be approximately 92.5 minutes = 5550 seconds
        assert 5500 < result.orbital_period < 5600

    def test_geostationary_period(self, geostationary_orbit):
        """GEO should have ~24 hour period (86164 seconds sidereal day)."""
        result = compute_orbital_dynamics(geostationary_orbit)

        # GEO period is one sidereal day
        sidereal_day = 86164.0905  # seconds
        assert abs(result.orbital_period - sidereal_day) < 10

    def test_period_increases_with_altitude(self, circular_leo, geostationary_orbit):
        """Higher orbits should have longer periods (Kepler's 3rd law)."""
        leo_result = compute_orbital_dynamics(circular_leo)
        geo_result = compute_orbital_dynamics(geostationary_orbit)

        assert geo_result.orbital_period > leo_result.orbital_period


class TestMeanMotion:
    """Tests for mean motion calculation."""

    def test_mean_motion_definition(self, circular_leo):
        """Mean motion n = sqrt(μ/a³) = 2π/T."""
        result = compute_orbital_dynamics(circular_leo)

        # n = 2π/T
        expected_n = 2 * np.pi / result.orbital_period

        assert abs(result.mean_motion - expected_n) < 1e-10

    def test_mean_motion_decreases_with_altitude(self, circular_leo, geostationary_orbit):
        """Higher orbits have lower mean motion."""
        leo_result = compute_orbital_dynamics(circular_leo)
        geo_result = compute_orbital_dynamics(geostationary_orbit)

        assert geo_result.mean_motion < leo_result.mean_motion


class TestVisVivaEquation:
    """Tests for vis-viva equation: v² = μ(2/r - 1/a)."""

    def test_circular_orbit_velocity(self, circular_leo):
        """Circular orbit: velocity is constant, v = sqrt(μ/a)."""
        result = compute_orbital_dynamics(circular_leo)

        a = R_EARTH + 400.0
        expected_velocity = np.sqrt(MU_EARTH / a)

        assert abs(result.velocity - expected_velocity) < 1e-6
        # LEO velocity should be ~7.67 km/s
        assert 7.6 < result.velocity < 7.8

    def test_elliptical_periapsis_velocity(self, elliptical_orbit):
        """Velocity at periapsis is maximum for elliptical orbit."""
        result = compute_orbital_dynamics(elliptical_orbit)

        # At periapsis (ν=0), r = a(1-e)
        assert result.velocity == result.periapsis_velocity

    def test_elliptical_apoapsis_velocity(self):
        """Velocity at apoapsis is minimum for elliptical orbit."""
        inputs = OrbitalInput(
            semi_major_axis=26600.0,
            eccentricity=0.74,
            gravitational_parameter=MU_EARTH,
            central_body_radius=R_EARTH,
            true_anomaly=180.0,  # At apoapsis
        )
        result = compute_orbital_dynamics(inputs)

        # At apoapsis (ν=180°), velocity equals apoapsis velocity
        assert abs(result.velocity - result.apoapsis_velocity) < 1e-6

    def test_periapsis_faster_than_apoapsis(self, elliptical_orbit):
        """Periapsis velocity should be higher than apoapsis velocity."""
        result = compute_orbital_dynamics(elliptical_orbit)

        assert result.periapsis_velocity > result.apoapsis_velocity


class TestApsisCalculations:
    """Tests for periapsis and apoapsis calculations."""

    def test_circular_orbit_apses_equal(self, circular_leo):
        """Circular orbit (e=0) has equal periapsis and apoapsis."""
        result = compute_orbital_dynamics(circular_leo)

        assert abs(result.periapsis_radius - result.apoapsis_radius) < 1e-6
        assert abs(result.periapsis_altitude - result.apoapsis_altitude) < 1e-6
        assert abs(result.periapsis_velocity - result.apoapsis_velocity) < 1e-6

    def test_periapsis_formula(self, elliptical_orbit):
        """r_p = a(1 - e)."""
        result = compute_orbital_dynamics(elliptical_orbit)

        expected_rp = 26600.0 * (1 - 0.74)  # 6916 km
        assert abs(result.periapsis_radius - expected_rp) < 1e-6

    def test_apoapsis_formula(self, elliptical_orbit):
        """r_a = a(1 + e)."""
        result = compute_orbital_dynamics(elliptical_orbit)

        expected_ra = 26600.0 * (1 + 0.74)  # 46284 km
        assert abs(result.apoapsis_radius - expected_ra) < 1e-6

    def test_altitude_calculation(self, circular_leo):
        """Altitude = radius - central body radius."""
        result = compute_orbital_dynamics(circular_leo)

        expected_altitude = (R_EARTH + 400.0) - R_EARTH
        assert abs(result.periapsis_altitude - expected_altitude) < 1e-6


class TestSpecificEnergy:
    """Tests for specific orbital energy: ε = -μ/(2a)."""

    def test_specific_energy_negative_for_ellipse(self, elliptical_orbit):
        """Bound (elliptical) orbits have negative specific energy."""
        result = compute_orbital_dynamics(elliptical_orbit)

        assert result.specific_orbital_energy < 0

    def test_specific_energy_formula(self, circular_leo):
        """ε = -μ/(2a)."""
        result = compute_orbital_dynamics(circular_leo)

        a = R_EARTH + 400.0
        expected_energy = -MU_EARTH / (2 * a)

        assert abs(result.specific_orbital_energy - expected_energy) < 1e-6

    def test_higher_orbit_less_negative_energy(self, circular_leo, geostationary_orbit):
        """Higher orbits have less negative (closer to zero) specific energy."""
        leo_result = compute_orbital_dynamics(circular_leo)
        geo_result = compute_orbital_dynamics(geostationary_orbit)

        # Both negative, but GEO should be closer to zero
        assert geo_result.specific_orbital_energy > leo_result.specific_orbital_energy


class TestSpecificAngularMomentum:
    """Tests for specific angular momentum: h = sqrt(μ * a * (1-e²))."""

    def test_specific_angular_momentum_formula(self, elliptical_orbit):
        """h = sqrt(μ * a * (1 - e²))."""
        result = compute_orbital_dynamics(elliptical_orbit)

        a = 26600.0
        e = 0.74
        expected_h = np.sqrt(MU_EARTH * a * (1 - e**2))

        assert abs(result.specific_angular_momentum - expected_h) < 1e-6

    def test_circular_angular_momentum(self, circular_leo):
        """For circular orbit (e=0): h = sqrt(μ * a)."""
        result = compute_orbital_dynamics(circular_leo)

        a = R_EARTH + 400.0
        expected_h = np.sqrt(MU_EARTH * a)

        assert abs(result.specific_angular_momentum - expected_h) < 1e-6


class TestTrueAnomalyVariation:
    """Tests for different true anomaly positions."""

    def test_radius_at_periapsis(self, elliptical_orbit):
        """At ν=0, radius should equal periapsis radius."""
        result = compute_orbital_dynamics(elliptical_orbit)

        assert abs(result.radius - result.periapsis_radius) < 1e-6

    def test_radius_at_apoapsis(self):
        """At ν=180°, radius should equal apoapsis radius."""
        inputs = OrbitalInput(
            semi_major_axis=10000.0,
            eccentricity=0.5,
            gravitational_parameter=MU_EARTH,
            central_body_radius=R_EARTH,
            true_anomaly=180.0,
        )
        result = compute_orbital_dynamics(inputs)

        assert abs(result.radius - result.apoapsis_radius) < 1e-6

    def test_radius_at_90_degrees(self):
        """At ν=90°, r = a(1-e²)/(1+0) = semi-latus rectum."""
        inputs = OrbitalInput(
            semi_major_axis=10000.0,
            eccentricity=0.5,
            gravitational_parameter=MU_EARTH,
            central_body_radius=R_EARTH,
            true_anomaly=90.0,
        )
        result = compute_orbital_dynamics(inputs)

        # At 90°, r = p = a(1-e²)
        expected_r = 10000.0 * (1 - 0.5**2)  # 7500 km
        assert abs(result.radius - expected_r) < 1e-6


class TestKnownOrbits:
    """Tests against known real-world orbit parameters."""

    def test_iss_orbit(self):
        """ISS-like orbit at ~420 km altitude."""
        inputs = OrbitalInput(
            semi_major_axis=6798.0,  # km (~420 km altitude)
            eccentricity=0.0002,
            gravitational_parameter=MU_EARTH,
            central_body_radius=R_EARTH,
        )
        result = compute_orbital_dynamics(inputs)

        # ISS period is about 92.68 minutes = 5561 seconds
        assert 5500 < result.orbital_period < 5650
        # ISS velocity is about 7.66 km/s
        assert 7.6 < result.velocity < 7.8

    def test_gps_orbit(self):
        """GPS satellite orbit (MEO at ~20,200 km altitude)."""
        inputs = OrbitalInput(
            semi_major_axis=26559.0,  # km
            eccentricity=0.01,
            gravitational_parameter=MU_EARTH,
            central_body_radius=R_EARTH,
        )
        result = compute_orbital_dynamics(inputs)

        # GPS period is ~12 hours = 43200 seconds
        assert 43000 < result.orbital_period < 44000


class TestAssumptions:
    """Tests for output metadata."""

    def test_assumptions_present(self, circular_leo):
        """Output should include calculation assumptions."""
        result = compute_orbital_dynamics(circular_leo)

        assert isinstance(result.assumptions, list)
        assert len(result.assumptions) > 0
        assert any("two-body" in a.lower() for a in result.assumptions)
