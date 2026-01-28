"""
Unit tests for Trajectory Generation Service.

Tests cover:
- Orbital trajectory point generation
- Relative motion trajectory generation
- Trajectory geometry validation
- Point count verification
"""

import numpy as np
import pytest

from app.schemas.gnc import OrbitalTrajectoryInput, RelativeTrajectoryInput
from app.services.gnc.trajectory import generate_orbital_trajectory, generate_relative_trajectory

from .conftest import MU_EARTH, R_EARTH


class TestOrbitalTrajectory:
    """Tests for orbital trajectory generation."""

    def test_correct_number_of_points(self, orbital_trajectory_input):
        """Should generate exactly the requested number of points."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        assert len(result.points) == orbital_trajectory_input.num_points

    def test_trajectory_is_closed(self, orbital_trajectory_input):
        """Orbital trajectory should start and end at same point (closed orbit)."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        first = result.points[0]
        last = result.points[-1]

        # Should be very close (same point at ν=0 and ν=2π)
        assert abs(first.x - last.x) < 1e-6
        assert abs(first.y - last.y) < 1e-6

    def test_periapsis_at_start(self):
        """First point should be at periapsis (ν=0)."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.5,
            central_body_radius=R_EARTH,
            num_points=100,
        )
        result = generate_orbital_trajectory(inputs)

        first_point = result.points[0]
        # At periapsis, y=0 and x = r_p = a(1-e)
        expected_x = 10000.0 * (1 - 0.5)  # 5000 km

        assert abs(first_point.x - expected_x) < 1e-6
        assert abs(first_point.y) < 1e-6

    def test_semi_axes_calculation(self, orbital_trajectory_input):
        """Semi-major and semi-minor axes should be correct."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        a = orbital_trajectory_input.semi_major_axis
        e = orbital_trajectory_input.eccentricity
        expected_b = a * np.sqrt(1 - e**2)

        assert abs(result.semi_major_axis - a) < 1e-6
        assert abs(result.semi_minor_axis - expected_b) < 1e-6

    def test_apses_calculation(self, orbital_trajectory_input):
        """Periapsis and apoapsis radii should be correct."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        a = orbital_trajectory_input.semi_major_axis
        e = orbital_trajectory_input.eccentricity

        expected_rp = a * (1 - e)
        expected_ra = a * (1 + e)

        assert abs(result.periapsis_radius - expected_rp) < 1e-6
        assert abs(result.apoapsis_radius - expected_ra) < 1e-6

    def test_circular_orbit_is_circle(self):
        """Circular orbit should have constant radius."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.0,  # Circular
            central_body_radius=R_EARTH,
            num_points=50,
        )
        result = generate_orbital_trajectory(inputs)

        # All points should be at same distance from origin
        radii = [np.sqrt(p.x**2 + p.y**2) for p in result.points]
        assert all(abs(r - 10000.0) < 1e-6 for r in radii)

    def test_time_parameter_spans_unit(self, orbital_trajectory_input):
        """Time parameter should go from 0 to 1."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        assert result.points[0].t == 0.0
        assert abs(result.points[-1].t - 1.0) < 1e-6

    def test_z_is_none_for_2d_orbit(self, orbital_trajectory_input):
        """Z coordinate should be None for orbital plane trajectory."""
        result = generate_orbital_trajectory(orbital_trajectory_input)

        assert all(p.z is None for p in result.points)

    def test_max_radius_at_apoapsis(self):
        """Maximum radius should occur at apoapsis."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.5,
            central_body_radius=R_EARTH,
            num_points=100,
        )
        result = generate_orbital_trajectory(inputs)

        radii = [np.sqrt(p.x**2 + p.y**2) for p in result.points]
        max_radius = max(radii)

        # Apoapsis radius
        expected_ra = 10000.0 * 1.5  # 15000 km

        assert abs(max_radius - expected_ra) < 10  # Within 10 km

    def test_min_radius_at_periapsis(self):
        """Minimum radius should occur at periapsis."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.5,
            central_body_radius=R_EARTH,
            num_points=100,
        )
        result = generate_orbital_trajectory(inputs)

        radii = [np.sqrt(p.x**2 + p.y**2) for p in result.points]
        min_radius = min(radii)

        # Periapsis radius
        expected_rp = 10000.0 * 0.5  # 5000 km

        assert abs(min_radius - expected_rp) < 10


class TestRelativeTrajectory:
    """Tests for relative motion trajectory generation."""

    def test_correct_number_of_points(self, relative_trajectory_input):
        """Should generate exactly the requested number of points."""
        result = generate_relative_trajectory(relative_trajectory_input)

        assert len(result.points) == relative_trajectory_input.num_points

    def test_starts_at_initial_state(self, relative_trajectory_input):
        """First point should be at initial state."""
        result = generate_relative_trajectory(relative_trajectory_input)

        first = result.points[0]

        assert abs(first.x - relative_trajectory_input.x0) < 1e-10
        assert abs(first.y - relative_trajectory_input.y0) < 1e-10
        assert abs(first.z - relative_trajectory_input.z0) < 1e-10
        assert first.t == 0.0

    def test_time_spans_requested_orbits(self, relative_trajectory_input):
        """Time should span the requested number of orbits."""
        result = generate_relative_trajectory(relative_trajectory_input)

        last = result.points[-1]

        # Total time should be num_orbits * orbital_period
        expected_total_time = relative_trajectory_input.num_orbits * result.orbital_period

        assert abs(last.t - expected_total_time) < 1

    def test_orbital_period_calculation(self, relative_trajectory_input):
        """Orbital period should be 2π/n."""
        result = generate_relative_trajectory(relative_trajectory_input)

        a = relative_trajectory_input.chief_semi_major_axis
        n = np.sqrt(MU_EARTH / a**3)
        expected_period = 2 * np.pi / n

        assert abs(result.orbital_period - expected_period) < 0.01

    def test_bounded_motion_detection(self, relative_trajectory_input):
        """Energy-matched trajectory should be bounded."""
        result = generate_relative_trajectory(relative_trajectory_input)

        assert result.is_bounded is True

    def test_unbounded_motion_detection(self):
        """Non-energy-matched trajectory should be unbounded."""
        a = R_EARTH + 400.0

        inputs = RelativeTrajectoryInput(
            chief_semi_major_axis=a,
            gravitational_parameter=MU_EARTH,
            x0=1.0,
            y0=0.0,
            z0=0.0,
            x_dot0=0.0,
            y_dot0=0.0,  # Not energy-matched
            z_dot0=0.0,
            num_orbits=1.0,
            num_points=50,
        )
        result = generate_relative_trajectory(inputs)

        assert result.is_bounded is False

    def test_max_range_tracked(self, relative_trajectory_input):
        """Maximum range should be tracked correctly."""
        result = generate_relative_trajectory(relative_trajectory_input)

        # Compute max range from points
        ranges = [np.sqrt(p.x**2 + p.y**2 + (p.z or 0) ** 2) for p in result.points]
        computed_max = max(ranges)

        assert abs(result.max_range - computed_max) < 1e-6

    def test_z_coordinate_present(self, relative_trajectory_input):
        """Z coordinate should be present for 3D relative motion."""
        result = generate_relative_trajectory(relative_trajectory_input)

        # All points should have z coordinate
        assert all(p.z is not None for p in result.points)

    def test_cross_track_oscillation(self):
        """Pure cross-track motion should oscillate sinusoidally."""
        a = R_EARTH + 400.0
        n = np.sqrt(MU_EARTH / a**3)

        inputs = RelativeTrajectoryInput(
            chief_semi_major_axis=a,
            gravitational_parameter=MU_EARTH,
            x0=0.0,
            y0=0.0,
            z0=1.0,  # 1 km cross-track
            x_dot0=0.0,
            y_dot0=0.0,
            z_dot0=0.0,
            num_orbits=1.0,
            num_points=100,
        )
        result = generate_relative_trajectory(inputs)

        # Z should oscillate between -1 and +1 km
        z_values = [p.z for p in result.points]
        assert max(z_values) > 0.99
        assert min(z_values) < -0.99


class TestTrajectoryEdgeCases:
    """Tests for edge cases in trajectory generation."""

    def test_minimum_points_orbital(self):
        """Should work with minimum number of points."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.1,
            central_body_radius=R_EARTH,
            num_points=10,  # Minimum
        )
        result = generate_orbital_trajectory(inputs)

        assert len(result.points) == 10

    def test_maximum_points_orbital(self):
        """Should work with maximum number of points."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.1,
            central_body_radius=R_EARTH,
            num_points=500,  # Maximum
        )
        result = generate_orbital_trajectory(inputs)

        assert len(result.points) == 500

    def test_highly_elliptical_orbit(self):
        """Should handle highly elliptical orbit."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=26600.0,
            eccentricity=0.9,  # Very elliptical
            central_body_radius=R_EARTH,
            num_points=100,
        )
        result = generate_orbital_trajectory(inputs)

        # Apoapsis should be ~50,540 km, periapsis ~2,660 km
        assert result.apoapsis_radius > 50000
        assert result.periapsis_radius < 3000

    def test_nearly_circular_orbit(self):
        """Should handle nearly circular orbit."""
        inputs = OrbitalTrajectoryInput(
            semi_major_axis=10000.0,
            eccentricity=0.001,  # Nearly circular
            central_body_radius=R_EARTH,
            num_points=50,
        )
        result = generate_orbital_trajectory(inputs)

        # Semi-major and semi-minor should be nearly equal
        assert abs(result.semi_major_axis - result.semi_minor_axis) < 10

    def test_small_relative_trajectory(self):
        """Should work with very small relative separations."""
        a = R_EARTH + 400.0
        n = np.sqrt(MU_EARTH / a**3)

        inputs = RelativeTrajectoryInput(
            chief_semi_major_axis=a,
            gravitational_parameter=MU_EARTH,
            x0=0.001,  # 1 meter
            y0=0.0,
            z0=0.0,
            x_dot0=0.0,
            y_dot0=-2 * n * 0.001,
            z_dot0=0.0,
            num_orbits=0.1,
            num_points=20,
        )
        result = generate_relative_trajectory(inputs)

        assert len(result.points) == 20
        assert result.max_range < 0.01  # Less than 10 meters

    def test_multiple_orbits_relative(self):
        """Should handle multiple orbits for relative trajectory."""
        a = R_EARTH + 400.0
        n = np.sqrt(MU_EARTH / a**3)

        inputs = RelativeTrajectoryInput(
            chief_semi_major_axis=a,
            gravitational_parameter=MU_EARTH,
            x0=0.5,
            y0=0.0,
            z0=0.0,
            x_dot0=0.0,
            y_dot0=-2 * n * 0.5,
            z_dot0=0.0,
            num_orbits=5.0,  # 5 orbits
            num_points=200,
        )
        result = generate_relative_trajectory(inputs)

        # Total time should be 5 orbits
        assert result.points[-1].t > 4.9 * result.orbital_period
