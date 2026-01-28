"""
Unit tests for Quaternion Attitude Module.

Tests cover:
- Quaternion normalization
- Quaternion multiplication
- Quaternion conjugate/inverse
- Conversions (quaternion <-> Euler, quaternion <-> DCM)
- Quaternion kinematics (derivative calculation)
- Attitude propagation with RK4
- Conservation laws
- API endpoints
"""

import numpy as np
import pytest

from app.schemas.gnc import (
    AttitudePropagationInput,
    QuaternionInput,
)
from app.services.gnc.quaternion import (
    dcm_to_quaternion,
    euler_to_quaternion,
    normalize_quaternion,
    propagate_attitude_rk4,
    quaternion_conjugate,
    quaternion_derivative,
    quaternion_inverse,
    quaternion_multiply,
    quaternion_to_dcm,
    quaternion_to_euler,
    rotate_vector_by_quaternion,
    compute_quaternion_operations,
    compute_attitude_propagation,
)


class TestQuaternionNormalization:
    """Tests for quaternion normalization."""

    def test_already_normalized(self):
        """Normalized quaternion should stay unchanged."""
        q = np.array([1.0, 0.0, 0.0, 0.0])
        q_norm = normalize_quaternion(q)

        np.testing.assert_array_almost_equal(q_norm, q)

    def test_unnormalized_quaternion(self):
        """Unnormalized quaternion should be normalized to unit magnitude."""
        q = np.array([2.0, 0.0, 0.0, 0.0])
        q_norm = normalize_quaternion(q)

        assert abs(np.linalg.norm(q_norm) - 1.0) < 1e-10
        np.testing.assert_array_almost_equal(q_norm, [1.0, 0.0, 0.0, 0.0])

    def test_general_quaternion(self):
        """General quaternion should normalize correctly."""
        q = np.array([1.0, 1.0, 1.0, 1.0])
        q_norm = normalize_quaternion(q)

        assert abs(np.linalg.norm(q_norm) - 1.0) < 1e-10
        expected = np.array([0.5, 0.5, 0.5, 0.5])
        np.testing.assert_array_almost_equal(q_norm, expected)

    def test_near_zero_quaternion(self):
        """Near-zero quaternion should return identity."""
        q = np.array([1e-12, 0.0, 0.0, 0.0])
        q_norm = normalize_quaternion(q)

        np.testing.assert_array_almost_equal(q_norm, [1.0, 0.0, 0.0, 0.0])


class TestQuaternionMultiplication:
    """Tests for quaternion multiplication."""

    def test_identity_multiplication(self):
        """Multiplying by identity should not change quaternion."""
        identity = np.array([1.0, 0.0, 0.0, 0.0])
        q = np.array([0.5, 0.5, 0.5, 0.5])

        result = quaternion_multiply(identity, q)
        np.testing.assert_array_almost_equal(result, q)

        result = quaternion_multiply(q, identity)
        np.testing.assert_array_almost_equal(result, q)

    def test_quaternion_inverse_product(self):
        """q ⊗ q* should equal identity for unit quaternion."""
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        q_conj = quaternion_conjugate(q)

        result = quaternion_multiply(q, q_conj)
        expected = np.array([1.0, 0.0, 0.0, 0.0])

        np.testing.assert_array_almost_equal(result, expected)

    def test_non_commutative(self):
        """Quaternion multiplication should be non-commutative."""
        q1 = normalize_quaternion(np.array([1.0, 1.0, 0.0, 0.0]))
        q2 = normalize_quaternion(np.array([1.0, 0.0, 1.0, 0.0]))

        result1 = quaternion_multiply(q1, q2)
        result2 = quaternion_multiply(q2, q1)

        # Results should be different
        assert not np.allclose(result1, result2)

    def test_90_degree_rotations(self):
        """Test composition of 90° rotations about different axes."""
        # 90° about X
        qx = euler_to_quaternion(np.pi/2, 0, 0)
        # 90° about Y
        qy = euler_to_quaternion(0, np.pi/2, 0)

        # Compose rotations
        result = quaternion_multiply(qy, qx)

        # Should still be unit quaternion
        assert abs(np.linalg.norm(result) - 1.0) < 1e-10


class TestQuaternionConjugateInverse:
    """Tests for quaternion conjugate and inverse."""

    def test_conjugate(self):
        """Conjugate should negate vector part."""
        q = np.array([1.0, 2.0, 3.0, 4.0])
        q_conj = quaternion_conjugate(q)

        expected = np.array([1.0, -2.0, -3.0, -4.0])
        np.testing.assert_array_almost_equal(q_conj, expected)

    def test_inverse_unit_quaternion(self):
        """Inverse of unit quaternion equals conjugate."""
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        q_inv = quaternion_inverse(q)
        q_conj = quaternion_conjugate(q)

        np.testing.assert_array_almost_equal(q_inv, q_conj)

    def test_inverse_non_unit(self):
        """Inverse of non-unit quaternion should satisfy q ⊗ q⁻¹ = identity."""
        q = np.array([1.0, 2.0, 3.0, 4.0])  # Not normalized
        q_inv = quaternion_inverse(q)

        result = quaternion_multiply(q, q_inv)
        expected = np.array([1.0, 0.0, 0.0, 0.0])

        np.testing.assert_array_almost_equal(result, expected)


class TestQuaternionDCMConversion:
    """Tests for quaternion to/from DCM conversion."""

    def test_identity_quaternion_to_dcm(self):
        """Identity quaternion should give identity DCM."""
        q = np.array([1.0, 0.0, 0.0, 0.0])
        dcm = quaternion_to_dcm(q)

        expected = np.eye(3)
        np.testing.assert_array_almost_equal(dcm, expected)

    def test_dcm_orthogonality(self):
        """DCM should be orthogonal: C * C^T = I."""
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        dcm = quaternion_to_dcm(q)

        result = dcm @ dcm.T
        expected = np.eye(3)

        np.testing.assert_array_almost_equal(result, expected)

    def test_dcm_determinant(self):
        """DCM should have determinant +1 (proper rotation)."""
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        dcm = quaternion_to_dcm(q)

        assert abs(np.linalg.det(dcm) - 1.0) < 1e-10

    def test_dcm_to_quaternion_roundtrip(self):
        """Converting q -> DCM -> q should recover original quaternion."""
        q_original = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        dcm = quaternion_to_dcm(q_original)
        q_recovered = dcm_to_quaternion(dcm)

        # Quaternions q and -q represent same rotation
        if q_recovered[0] * q_original[0] < 0:
            q_recovered = -q_recovered

        np.testing.assert_array_almost_equal(q_recovered, q_original)

    def test_90_degree_rotation_dcm(self):
        """90° rotation about Z axis should give correct DCM."""
        q = euler_to_quaternion(0, 0, np.pi/2)  # 90° yaw
        dcm = quaternion_to_dcm(q)

        # Expected DCM for 90° about Z
        expected = np.array([
            [0, 1, 0],
            [-1, 0, 0],
            [0, 0, 1],
        ])

        np.testing.assert_array_almost_equal(dcm, expected, decimal=6)


class TestQuaternionEulerConversion:
    """Tests for quaternion to/from Euler angle conversion."""

    def test_identity_euler_angles(self):
        """Zero Euler angles should give identity quaternion."""
        q = euler_to_quaternion(0, 0, 0)

        expected = np.array([1.0, 0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(q, expected)

    def test_euler_roundtrip(self):
        """Converting Euler -> q -> Euler should recover angles."""
        roll, pitch, yaw = 0.1, 0.2, 0.3
        q = euler_to_quaternion(roll, pitch, yaw)
        euler_recovered = quaternion_to_euler(q)

        np.testing.assert_array_almost_equal(
            euler_recovered, [roll, pitch, yaw], decimal=10
        )

    def test_pure_roll(self):
        """Pure roll rotation."""
        roll = np.pi / 4  # 45°
        q = euler_to_quaternion(roll, 0, 0)
        euler = quaternion_to_euler(q)

        assert abs(euler[0] - roll) < 1e-10  # Roll
        assert abs(euler[1]) < 1e-10  # Pitch
        assert abs(euler[2]) < 1e-10  # Yaw

    def test_pure_pitch(self):
        """Pure pitch rotation."""
        pitch = np.pi / 6  # 30°
        q = euler_to_quaternion(0, pitch, 0)
        euler = quaternion_to_euler(q)

        assert abs(euler[0]) < 1e-10  # Roll
        assert abs(euler[1] - pitch) < 1e-10  # Pitch
        assert abs(euler[2]) < 1e-10  # Yaw

    def test_pure_yaw(self):
        """Pure yaw rotation."""
        yaw = np.pi / 3  # 60°
        q = euler_to_quaternion(0, 0, yaw)
        euler = quaternion_to_euler(q)

        assert abs(euler[0]) < 1e-10  # Roll
        assert abs(euler[1]) < 1e-10  # Pitch
        assert abs(euler[2] - yaw) < 1e-10  # Yaw

    def test_gimbal_lock_handling(self):
        """Near gimbal lock (pitch = ±90°) should not crash."""
        pitch = np.pi / 2 - 0.001  # Near 90°
        q = euler_to_quaternion(0.1, pitch, 0.2)
        euler = quaternion_to_euler(q)

        # Should not raise and pitch should be close to input
        assert abs(euler[1] - pitch) < 0.01


class TestQuaternionDerivative:
    """Tests for quaternion kinematics (derivative calculation)."""

    def test_zero_angular_velocity(self):
        """Zero angular velocity should give zero quaternion derivative."""
        q = np.array([1.0, 0.0, 0.0, 0.0])
        omega = np.array([0.0, 0.0, 0.0])

        q_dot = quaternion_derivative(q, omega)

        np.testing.assert_array_almost_equal(q_dot, [0.0, 0.0, 0.0, 0.0])

    def test_pure_x_rotation(self):
        """Pure rotation about X axis."""
        q = np.array([1.0, 0.0, 0.0, 0.0])
        omega = np.array([1.0, 0.0, 0.0])  # 1 rad/s about X

        q_dot = quaternion_derivative(q, omega)

        # q̇ = 0.5 * q ⊗ [0, ω]
        # For identity q and ω = [1,0,0]: q̇ = [0, 0.5, 0, 0]
        expected = np.array([0.0, 0.5, 0.0, 0.0])
        np.testing.assert_array_almost_equal(q_dot, expected)

    def test_derivative_magnitude_constraint(self):
        """
        For unit quaternion, q · q̇ = 0 (derivative is orthogonal to quaternion).
        This ensures the quaternion stays on the unit sphere.
        """
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        omega = np.array([0.1, 0.2, 0.3])

        q_dot = quaternion_derivative(q, omega)

        # q · q̇ should be zero
        dot_product = np.dot(q, q_dot)
        assert abs(dot_product) < 1e-10


class TestVectorRotation:
    """Tests for rotating vectors by quaternions."""

    def test_identity_rotation(self):
        """Identity quaternion should not change vector."""
        q = np.array([1.0, 0.0, 0.0, 0.0])
        v = np.array([1.0, 2.0, 3.0])

        v_rotated = rotate_vector_by_quaternion(q, v)

        np.testing.assert_array_almost_equal(v_rotated, v)

    def test_90_degree_rotation_about_z(self):
        """90° rotation about Z should rotate X to Y."""
        q = euler_to_quaternion(0, 0, np.pi/2)
        v = np.array([1.0, 0.0, 0.0])  # X axis

        v_rotated = rotate_vector_by_quaternion(q, v)

        expected = np.array([0.0, 1.0, 0.0])  # Y axis
        np.testing.assert_array_almost_equal(v_rotated, expected, decimal=6)

    def test_180_degree_rotation(self):
        """180° rotation about Z should flip X and Y."""
        q = euler_to_quaternion(0, 0, np.pi)
        v = np.array([1.0, 0.0, 0.0])

        v_rotated = rotate_vector_by_quaternion(q, v)

        expected = np.array([-1.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(v_rotated, expected, decimal=6)

    def test_rotation_preserves_magnitude(self):
        """Rotation should preserve vector magnitude."""
        q = normalize_quaternion(np.array([1.0, 2.0, 3.0, 4.0]))
        v = np.array([1.0, 2.0, 3.0])

        v_rotated = rotate_vector_by_quaternion(q, v)

        assert abs(np.linalg.norm(v_rotated) - np.linalg.norm(v)) < 1e-10


class TestAttitudePropagation:
    """Tests for attitude propagation with RK4 integration."""

    def test_torque_free_energy_conservation(self):
        """Torque-free motion should conserve rotational kinetic energy."""
        q0 = np.array([1.0, 0.0, 0.0, 0.0])
        omega0 = np.array([0.1, 0.0, 0.1])  # Spin about two axes
        inertia = np.array([100.0, 200.0, 300.0])
        torque = np.array([0.0, 0.0, 0.0])

        q_hist, omega_hist, t_hist = propagate_attitude_rk4(
            q0, omega0, inertia, torque, dt=0.1, num_steps=100
        )

        # Compute initial and final kinetic energy
        initial_ke = 0.5 * np.sum(inertia * omega0**2)
        final_omega = omega_hist[-1]
        final_ke = 0.5 * np.sum(inertia * final_omega**2)

        # Energy should be conserved within 0.1%
        assert abs(final_ke - initial_ke) / initial_ke < 0.001

    def test_torque_free_momentum_conservation(self):
        """Torque-free motion should conserve angular momentum magnitude."""
        q0 = np.array([1.0, 0.0, 0.0, 0.0])
        omega0 = np.array([0.1, 0.05, 0.1])
        inertia = np.array([100.0, 200.0, 300.0])
        torque = np.array([0.0, 0.0, 0.0])

        q_hist, omega_hist, t_hist = propagate_attitude_rk4(
            q0, omega0, inertia, torque, dt=0.1, num_steps=100
        )

        # Compute initial and final momentum magnitude
        initial_H = np.linalg.norm(inertia * omega0)
        final_omega = omega_hist[-1]
        final_H = np.linalg.norm(inertia * final_omega)

        # Momentum should be conserved within 0.1%
        assert abs(final_H - initial_H) / initial_H < 0.001

    def test_quaternion_normalization(self):
        """Quaternions should remain normalized throughout propagation."""
        q0 = np.array([1.0, 0.0, 0.0, 0.0])
        omega0 = np.array([0.5, 0.3, 0.2])
        inertia = np.array([100.0, 100.0, 100.0])
        torque = np.array([0.0, 0.0, 0.0])

        q_hist, omega_hist, t_hist = propagate_attitude_rk4(
            q0, omega0, inertia, torque, dt=0.01, num_steps=1000
        )

        # All quaternions should have unit magnitude
        for q in q_hist:
            assert abs(np.linalg.norm(q) - 1.0) < 1e-6

    def test_constant_torque_changes_momentum(self):
        """Constant torque should change angular momentum linearly."""
        q0 = np.array([1.0, 0.0, 0.0, 0.0])
        omega0 = np.array([0.0, 0.0, 0.0])  # Start at rest
        inertia = np.array([100.0, 100.0, 100.0])  # Symmetric body
        torque = np.array([0.0, 0.0, 1.0])  # 1 N·m about Z

        total_time = 10.0
        q_hist, omega_hist, t_hist = propagate_attitude_rk4(
            q0, omega0, inertia, torque, dt=0.1, num_steps=100
        )

        # For symmetric body: ω_z = M_z * t / I_z
        expected_omega_z = torque[2] * total_time / inertia[2]
        actual_omega_z = omega_hist[-1][2]

        assert abs(actual_omega_z - expected_omega_z) < 0.01

    def test_stable_major_axis_spin(self):
        """Spin about major axis should remain stable."""
        q0 = np.array([1.0, 0.0, 0.0, 0.0])
        omega0 = np.array([0.0, 0.0, 1.0])  # Spin about Z (major axis)
        inertia = np.array([100.0, 100.0, 150.0])  # Z is major axis
        torque = np.array([0.0, 0.0, 0.0])

        q_hist, omega_hist, t_hist = propagate_attitude_rk4(
            q0, omega0, inertia, torque, dt=0.1, num_steps=200
        )

        # Angular velocity should remain constant
        for omega in omega_hist:
            assert abs(omega[0]) < 1e-6  # No X component
            assert abs(omega[1]) < 1e-6  # No Y component
            assert abs(omega[2] - 1.0) < 1e-6  # Z stays at 1


class TestQuaternionServiceFunction:
    """Tests for the quaternion service function."""

    def test_basic_quaternion_operations(self):
        """Test basic quaternion operations output."""
        inputs = QuaternionInput(
            q0=1.0, q1=0.0, q2=0.0, q3=0.0,
            omega_x=0.1, omega_y=0.0, omega_z=0.0,
        )
        result = compute_quaternion_operations(inputs)

        # Should be normalized
        assert result.is_normalized is True
        assert abs(result.magnitude - 1.0) < 1e-6

        # Check derivative
        assert abs(result.q1_dot - 0.05) < 1e-6  # 0.5 * 0.1

        # Check Euler angles (should all be zero for identity quaternion)
        assert abs(result.euler_angles.roll_deg) < 1e-6
        assert abs(result.euler_angles.pitch_deg) < 1e-6
        assert abs(result.euler_angles.yaw_deg) < 1e-6

    def test_unnormalized_input(self):
        """Unnormalized input should be normalized."""
        inputs = QuaternionInput(
            q0=2.0, q1=0.0, q2=0.0, q3=0.0,  # Not normalized
        )
        result = compute_quaternion_operations(inputs)

        assert result.is_normalized is False  # Input was not normalized
        assert abs(result.q0 - 1.0) < 1e-6  # Output is normalized

    def test_dcm_in_output(self):
        """DCM should be properly formatted."""
        inputs = QuaternionInput(q0=1.0, q1=0.0, q2=0.0, q3=0.0)
        result = compute_quaternion_operations(inputs)

        # DCM should be 9 elements (3x3 flattened)
        assert len(result.dcm) == 9

        # For identity quaternion, DCM should be identity
        expected_dcm = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        for i, (actual, expected) in enumerate(zip(result.dcm, expected_dcm)):
            assert abs(actual - expected) < 1e-6


class TestAttitudePropagationServiceFunction:
    """Tests for the attitude propagation service function."""

    def test_propagation_output_structure(self):
        """Test that propagation output has correct structure."""
        inputs = AttitudePropagationInput(
            q0=1.0, q1=0.0, q2=0.0, q3=0.0,
            omega_x=0.1, omega_y=0.0, omega_z=0.0,
            inertia_x=100.0, inertia_y=100.0, inertia_z=100.0,
            torque_x=0.0, torque_y=0.0, torque_z=0.0,
            propagation_time=10.0,
            num_steps=100,
        )
        result = compute_attitude_propagation(inputs)

        # Should have correct number of states (num_steps + 1 for initial)
        assert len(result.states) == 101

        # First state should be initial conditions
        assert result.states[0].t == 0.0
        assert abs(result.states[0].q0 - 1.0) < 1e-6
        assert abs(result.states[0].omega_x - 0.1) < 1e-6

        # Time step should be correct
        assert abs(result.time_step - 0.1) < 1e-6

        # Integration method should be RK4
        assert result.integration_method == "RK4"

    def test_conservation_errors_reported(self):
        """Conservation errors should be reported for torque-free motion."""
        inputs = AttitudePropagationInput(
            q0=1.0, q1=0.0, q2=0.0, q3=0.0,
            omega_x=0.1, omega_y=0.05, omega_z=0.1,
            inertia_x=100.0, inertia_y=200.0, inertia_z=300.0,
            torque_x=0.0, torque_y=0.0, torque_z=0.0,  # Torque-free
            propagation_time=10.0,
            num_steps=100,
        )
        result = compute_attitude_propagation(inputs)

        # Conservation errors should be reported
        assert result.energy_conservation_error is not None
        assert result.momentum_conservation_error is not None

        # Errors should be small
        assert result.energy_conservation_error < 0.01
        assert result.momentum_conservation_error < 0.01

    def test_conservation_errors_not_reported_with_torque(self):
        """Conservation errors should not be reported when torque is applied."""
        inputs = AttitudePropagationInput(
            q0=1.0, q1=0.0, q2=0.0, q3=0.0,
            omega_x=0.0, omega_y=0.0, omega_z=0.0,
            inertia_x=100.0, inertia_y=100.0, inertia_z=100.0,
            torque_x=0.0, torque_y=0.0, torque_z=1.0,  # With torque
            propagation_time=10.0,
            num_steps=100,
        )
        result = compute_attitude_propagation(inputs)

        # Conservation errors should be None when torque is applied
        assert result.energy_conservation_error is None
        assert result.momentum_conservation_error is None


class TestQuaternionAPIEndpoints:
    """Integration tests for quaternion API endpoints."""

    def test_quaternion_endpoint(self, client):
        """Test /attitude/quaternion endpoint."""
        payload = {
            "q0": 0.707,
            "q1": 0.707,
            "q2": 0.0,
            "q3": 0.0,
            "omega_x": 0.1,
            "omega_y": 0.0,
            "omega_z": 0.0,
        }
        response = client.post("/api/gnc/attitude/quaternion", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "q0" in data
        assert "euler_angles" in data
        assert "dcm" in data
        assert "is_normalized" in data

    def test_propagate_endpoint(self, client):
        """Test /attitude/propagate endpoint."""
        payload = {
            "q0": 1.0,
            "q1": 0.0,
            "q2": 0.0,
            "q3": 0.0,
            "omega_x": 0.1,
            "omega_y": 0.0,
            "omega_z": 0.0,
            "inertia_x": 100.0,
            "inertia_y": 100.0,
            "inertia_z": 100.0,
            "propagation_time": 10.0,
            "num_steps": 50,
        }
        response = client.post("/api/gnc/attitude/propagate", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "states" in data
        assert len(data["states"]) == 51  # num_steps + 1
        assert "time_step" in data
        assert "integration_method" in data

    def test_propagate_invalid_inertia(self, client):
        """Invalid inertia should return 422."""
        payload = {
            "omega_x": 0.1,
            "omega_y": 0.0,
            "omega_z": 0.0,
            "inertia_x": 0.0,  # Invalid
            "inertia_y": 100.0,
            "inertia_z": 100.0,
            "propagation_time": 10.0,
        }
        response = client.post("/api/gnc/attitude/propagate", json=payload)

        assert response.status_code == 422


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
