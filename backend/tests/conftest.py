"""
Pytest configuration and shared fixtures for GNC tests.

This module provides common test fixtures including:
- Standard spacecraft configurations
- Orbital parameters for Earth
- FastAPI test client
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.gnc import (
    AttitudeInput,
    OrbitalInput,
    OrbitalTrajectoryInput,
    RelativeMotionInput,
    RelativeTrajectoryInput,
)


# =============================================================================
# Physical Constants
# =============================================================================

# Earth gravitational parameter [km³/s²]
MU_EARTH = 398600.4418

# Earth equatorial radius [km]
R_EARTH = 6378.137


# =============================================================================
# API Test Client
# =============================================================================


@pytest.fixture
def client():
    """FastAPI test client for API integration tests."""
    return TestClient(app)


# =============================================================================
# Attitude Dynamics Fixtures
# =============================================================================


@pytest.fixture
def symmetric_spacecraft() -> AttitudeInput:
    """
    Axisymmetric spacecraft (cylinder/disk shape).
    Ix = Iy, stable spin about Z-axis.
    """
    return AttitudeInput(
        inertia_x=100.0,
        inertia_y=100.0,
        inertia_z=150.0,
        omega_x=0.0,
        omega_y=0.0,
        omega_z=0.1,  # 0.1 rad/s spin about major axis
        torque_x=0.0,
        torque_y=0.0,
        torque_z=0.0,
    )


@pytest.fixture
def asymmetric_spacecraft() -> AttitudeInput:
    """
    Asymmetric spacecraft (rectangular box shape).
    All moments of inertia different - demonstrates tennis racket theorem.
    """
    return AttitudeInput(
        inertia_x=100.0,  # Smallest (minor axis)
        inertia_y=200.0,  # Middle (intermediate axis) - unstable
        inertia_z=300.0,  # Largest (major axis)
        omega_x=0.0,
        omega_y=0.1,  # Spin about intermediate axis
        omega_z=0.0,
        torque_x=0.0,
        torque_y=0.0,
        torque_z=0.0,
    )


@pytest.fixture
def spacecraft_with_torque() -> AttitudeInput:
    """Spacecraft with constant applied torque."""
    return AttitudeInput(
        inertia_x=100.0,
        inertia_y=100.0,
        inertia_z=150.0,
        omega_x=0.0,
        omega_y=0.0,
        omega_z=0.0,  # Starting from rest
        torque_x=0.0,
        torque_y=0.0,
        torque_z=1.0,  # 1 N·m about Z
    )


# =============================================================================
# Orbital Dynamics Fixtures
# =============================================================================


@pytest.fixture
def circular_leo() -> OrbitalInput:
    """Circular Low Earth Orbit at 400 km altitude (ISS-like)."""
    return OrbitalInput(
        semi_major_axis=R_EARTH + 400.0,  # ~6778 km
        eccentricity=0.0,
        gravitational_parameter=MU_EARTH,
        central_body_radius=R_EARTH,
        true_anomaly=0.0,
    )


@pytest.fixture
def elliptical_orbit() -> OrbitalInput:
    """Molniya-type highly elliptical orbit."""
    return OrbitalInput(
        semi_major_axis=26600.0,  # km
        eccentricity=0.74,
        gravitational_parameter=MU_EARTH,
        central_body_radius=R_EARTH,
        true_anomaly=0.0,  # At periapsis
    )


@pytest.fixture
def geostationary_orbit() -> OrbitalInput:
    """Geostationary orbit (GEO)."""
    return OrbitalInput(
        semi_major_axis=42164.0,  # km (GEO radius)
        eccentricity=0.0,
        gravitational_parameter=MU_EARTH,
        central_body_radius=R_EARTH,
        true_anomaly=0.0,
    )


# =============================================================================
# Relative Motion Fixtures
# =============================================================================


@pytest.fixture
def bounded_relative_motion() -> RelativeMotionInput:
    """
    Bounded relative motion.

    The code uses drift formula: drift = 6π*x0 + 4*ẏ0/n
    For bounded motion, this must be near zero.
    Setting x0=0 (V-bar hold) ensures bounded motion.
    """
    a = R_EARTH + 400.0  # Chief at 400 km

    return RelativeMotionInput(
        chief_semi_major_axis=a,
        gravitational_parameter=MU_EARTH,
        x0=0.0,  # No radial offset (V-bar position)
        y0=1.0,  # 1 km in-track offset
        z0=0.0,
        x_dot0=0.0,
        y_dot0=0.0,
        z_dot0=0.0,
        propagation_time=5400.0,  # ~1 orbit (90 min)
    )


@pytest.fixture
def drifting_relative_motion() -> RelativeMotionInput:
    """Unbounded relative motion with secular drift."""
    a = R_EARTH + 400.0

    return RelativeMotionInput(
        chief_semi_major_axis=a,
        gravitational_parameter=MU_EARTH,
        x0=1.0,  # 1 km radial offset
        y0=0.0,
        z0=0.0,
        x_dot0=0.0,
        y_dot0=0.0,  # NOT energy-matched, will drift
        z_dot0=0.0,
        propagation_time=5400.0,
    )


@pytest.fixture
def cross_track_motion() -> RelativeMotionInput:
    """Pure cross-track (out-of-plane) motion."""
    a = R_EARTH + 400.0

    return RelativeMotionInput(
        chief_semi_major_axis=a,
        gravitational_parameter=MU_EARTH,
        x0=0.0,
        y0=0.0,
        z0=1.0,  # 1 km cross-track offset
        x_dot0=0.0,
        y_dot0=0.0,
        z_dot0=0.0,
        propagation_time=5400.0,
    )


# =============================================================================
# Trajectory Fixtures
# =============================================================================


@pytest.fixture
def orbital_trajectory_input() -> OrbitalTrajectoryInput:
    """Standard orbital trajectory generation input."""
    return OrbitalTrajectoryInput(
        semi_major_axis=R_EARTH + 400.0,
        eccentricity=0.1,
        central_body_radius=R_EARTH,
        num_points=100,
    )


@pytest.fixture
def relative_trajectory_input() -> RelativeTrajectoryInput:
    """
    Standard relative trajectory generation input.

    Uses V-bar position (x0=0) for bounded motion.
    """
    a = R_EARTH + 400.0

    return RelativeTrajectoryInput(
        chief_semi_major_axis=a,
        gravitational_parameter=MU_EARTH,
        x0=0.0,  # V-bar position for bounded motion
        y0=0.5,  # 500m in-track
        z0=0.2,  # 200m cross-track
        x_dot0=0.0,
        y_dot0=0.0,
        z_dot0=0.0,
        num_orbits=2.0,
        num_points=200,
    )


# =============================================================================
# Test Utilities
# =============================================================================


def assert_close(actual: float, expected: float, rel_tol: float = 1e-6, abs_tol: float = 1e-10):
    """Assert that two values are close within tolerance."""
    assert abs(actual - expected) <= max(rel_tol * abs(expected), abs_tol), (
        f"Values not close: actual={actual}, expected={expected}, "
        f"diff={abs(actual - expected)}"
    )
