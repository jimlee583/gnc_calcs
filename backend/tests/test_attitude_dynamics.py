"""
Unit tests for Attitude Dynamics Service.

Tests cover:
- Euler's equations correctness
- Physical conservation laws (energy, angular momentum)
- Tennis racket theorem (intermediate axis instability)
- Torque response
- Edge cases
"""

import numpy as np
import pytest

from app.schemas.gnc import AttitudeInput
from app.services.gnc.attitude_dynamics import compute_attitude_dynamics


class TestEulerEquations:
    """Tests for basic Euler equation calculations."""

    def test_pure_spin_major_axis_zero_acceleration(self, symmetric_spacecraft):
        """
        Pure spin about major axis (Z) with axisymmetric body.
        When Ix = Iy, spin about Z should have zero angular acceleration.
        """
        result = compute_attitude_dynamics(symmetric_spacecraft)

        # For axisymmetric body spinning about symmetry axis, no gyroscopic coupling
        assert abs(result.omega_dot_x) < 1e-10
        assert abs(result.omega_dot_y) < 1e-10
        assert abs(result.omega_dot_z) < 1e-10

    def test_torque_produces_acceleration(self, spacecraft_with_torque):
        """Applied torque should produce angular acceleration."""
        result = compute_attitude_dynamics(spacecraft_with_torque)

        # τ = I * α, so α = τ / I
        # torque_z = 1.0 N·m, inertia_z = 150 kg·m²
        expected_alpha_z = 1.0 / 150.0

        assert abs(result.omega_dot_x) < 1e-10
        assert abs(result.omega_dot_y) < 1e-10
        assert abs(result.omega_dot_z - expected_alpha_z) < 1e-10

    def test_gyroscopic_coupling(self):
        """
        Test gyroscopic coupling between axes.
        Spin about two axes should produce acceleration about the third.
        """
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.1,
            omega_y=0.1,
            omega_z=0.0,
            torque_x=0.0,
            torque_y=0.0,
            torque_z=0.0,
        )
        result = compute_attitude_dynamics(inputs)

        # ω̇_z = (I_x - I_y) * ω_x * ω_y / I_z
        # = (100 - 200) * 0.1 * 0.1 / 300 = -0.00333...
        expected_omega_dot_z = (100.0 - 200.0) * 0.1 * 0.1 / 300.0

        assert abs(result.omega_dot_z - expected_omega_dot_z) < 1e-10


class TestConservationLaws:
    """Tests for physical conservation laws."""

    def test_rotational_kinetic_energy_calculation(self):
        """Verify rotational KE formula: T = 0.5 * (Ix*ωx² + Iy*ωy² + Iz*ωz²)."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.1,
            omega_y=0.2,
            omega_z=0.3,
        )
        result = compute_attitude_dynamics(inputs)

        expected_ke = 0.5 * (100.0 * 0.1**2 + 200.0 * 0.2**2 + 300.0 * 0.3**2)
        # = 0.5 * (1 + 8 + 27) = 0.5 * 36 = 18

        assert abs(result.rotational_kinetic_energy - expected_ke) < 1e-10

    def test_angular_momentum_magnitude(self):
        """Verify angular momentum: |H| = sqrt((Ix*ωx)² + (Iy*ωy)² + (Iz*ωz)²)."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.1,
            omega_y=0.2,
            omega_z=0.3,
        )
        result = compute_attitude_dynamics(inputs)

        Hx = 100.0 * 0.1  # 10
        Hy = 200.0 * 0.2  # 40
        Hz = 300.0 * 0.3  # 90
        expected_H = np.sqrt(Hx**2 + Hy**2 + Hz**2)
        # = sqrt(100 + 1600 + 8100) = sqrt(9800) ≈ 98.99

        assert abs(result.angular_momentum_magnitude - expected_H) < 1e-10

    def test_zero_rates_zero_momentum(self):
        """Zero angular rates should give zero momentum and KE."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.0,
            omega_y=0.0,
            omega_z=0.0,
        )
        result = compute_attitude_dynamics(inputs)

        assert result.rotational_kinetic_energy == 0.0
        assert result.angular_momentum_magnitude == 0.0


class TestTennisRacketTheorem:
    """
    Tests related to the intermediate axis theorem.

    The tennis racket theorem states that rotation about the intermediate
    moment of inertia axis is unstable. A small perturbation will grow.
    """

    def test_major_axis_spin_stable(self):
        """Spin about major axis (largest I) should be stable (zero acceleration)."""
        inputs = AttitudeInput(
            inertia_x=100.0,  # Minor
            inertia_y=200.0,  # Intermediate
            inertia_z=300.0,  # Major
            omega_x=0.0,
            omega_y=0.0,
            omega_z=1.0,  # Spin about major axis
        )
        result = compute_attitude_dynamics(inputs)

        # Pure spin about principal axis: no gyroscopic torques
        assert abs(result.omega_dot_x) < 1e-10
        assert abs(result.omega_dot_y) < 1e-10
        assert abs(result.omega_dot_z) < 1e-10

    def test_minor_axis_spin_stable(self):
        """Spin about minor axis (smallest I) should be stable."""
        inputs = AttitudeInput(
            inertia_x=100.0,  # Minor
            inertia_y=200.0,  # Intermediate
            inertia_z=300.0,  # Major
            omega_x=1.0,  # Spin about minor axis
            omega_y=0.0,
            omega_z=0.0,
        )
        result = compute_attitude_dynamics(inputs)

        assert abs(result.omega_dot_x) < 1e-10
        assert abs(result.omega_dot_y) < 1e-10
        assert abs(result.omega_dot_z) < 1e-10

    def test_intermediate_axis_perturbation_grows(self, asymmetric_spacecraft):
        """
        Small perturbation from intermediate axis spin should produce
        non-zero angular acceleration (indicating instability).
        """
        # Add small perturbation to intermediate axis spin
        perturbed = AttitudeInput(
            inertia_x=asymmetric_spacecraft.inertia_x,
            inertia_y=asymmetric_spacecraft.inertia_y,
            inertia_z=asymmetric_spacecraft.inertia_z,
            omega_x=0.001,  # Small perturbation
            omega_y=0.1,  # Primary spin about intermediate axis
            omega_z=0.001,  # Small perturbation
        )
        result = compute_attitude_dynamics(perturbed)

        # The perturbations should cause angular accelerations
        # (instability characteristic of intermediate axis)
        assert result.omega_dot_x != 0.0 or result.omega_dot_z != 0.0


class TestTorqueResponse:
    """Tests for applied torque responses."""

    def test_single_axis_torque(self):
        """Single-axis torque on stationary body."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=100.0,
            inertia_z=100.0,
            omega_x=0.0,
            omega_y=0.0,
            omega_z=0.0,
            torque_x=10.0,  # 10 N·m about X
            torque_y=0.0,
            torque_z=0.0,
        )
        result = compute_attitude_dynamics(inputs)

        # α = τ / I = 10 / 100 = 0.1 rad/s²
        assert abs(result.omega_dot_x - 0.1) < 1e-10
        assert abs(result.omega_dot_y) < 1e-10
        assert abs(result.omega_dot_z) < 1e-10

    def test_multi_axis_torque(self):
        """Multiple simultaneous torques."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.0,
            omega_y=0.0,
            omega_z=0.0,
            torque_x=10.0,
            torque_y=20.0,
            torque_z=30.0,
        )
        result = compute_attitude_dynamics(inputs)

        assert abs(result.omega_dot_x - 0.1) < 1e-10  # 10/100
        assert abs(result.omega_dot_y - 0.1) < 1e-10  # 20/200
        assert abs(result.omega_dot_z - 0.1) < 1e-10  # 30/300

    def test_torque_counters_gyroscopic(self):
        """Torque can counter gyroscopic effects."""
        # First, find the gyroscopic acceleration without torque
        base_inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.1,
            omega_y=0.2,
            omega_z=0.0,
        )
        base_result = compute_attitude_dynamics(base_inputs)
        gyro_accel_z = base_result.omega_dot_z

        # Now apply torque to counter it
        counter_torque = -gyro_accel_z * 300.0  # τ = I * α
        inputs_with_counter = AttitudeInput(
            inertia_x=100.0,
            inertia_y=200.0,
            inertia_z=300.0,
            omega_x=0.1,
            omega_y=0.2,
            omega_z=0.0,
            torque_z=counter_torque,
        )
        result = compute_attitude_dynamics(inputs_with_counter)

        # Z acceleration should be nearly zero
        assert abs(result.omega_dot_z) < 1e-10


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_inertias(self):
        """Very small (but valid) inertias should still work."""
        inputs = AttitudeInput(
            inertia_x=0.001,
            inertia_y=0.002,
            inertia_z=0.003,
            omega_x=0.1,
            omega_y=0.1,
            omega_z=0.1,
        )
        result = compute_attitude_dynamics(inputs)

        # Should compute without error
        assert result.rotational_kinetic_energy > 0

    def test_very_large_inertias(self):
        """Very large inertias (e.g., space station)."""
        inputs = AttitudeInput(
            inertia_x=1e8,
            inertia_y=2e8,
            inertia_z=3e8,
            omega_x=0.001,
            omega_y=0.001,
            omega_z=0.001,
        )
        result = compute_attitude_dynamics(inputs)

        # Angular momentum should be very large
        assert result.angular_momentum_magnitude > 1e5

    def test_negative_angular_velocities(self):
        """Negative angular velocities should work correctly."""
        inputs = AttitudeInput(
            inertia_x=100.0,
            inertia_y=100.0,
            inertia_z=150.0,
            omega_x=-0.1,
            omega_y=-0.2,
            omega_z=-0.3,
        )
        result = compute_attitude_dynamics(inputs)

        # KE should still be positive
        assert result.rotational_kinetic_energy > 0
        # Angular momentum magnitude should be positive
        assert result.angular_momentum_magnitude > 0

    def test_assumptions_returned(self, symmetric_spacecraft):
        """Output should include list of assumptions."""
        result = compute_attitude_dynamics(symmetric_spacecraft)

        assert isinstance(result.assumptions, list)
        assert len(result.assumptions) > 0
        assert any("rigid body" in a.lower() for a in result.assumptions)
