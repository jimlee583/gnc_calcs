"""
API Integration Tests for GNC Endpoints.

Tests the full HTTP request/response cycle including:
- Correct status codes
- Response schema validation
- Error handling
- Input validation
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

from .conftest import MU_EARTH, R_EARTH


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Health endpoint should return 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Root endpoint should return API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestAttitudeEndpoint:
    """Tests for /api/gnc/attitude endpoint."""

    def test_valid_attitude_request(self, client):
        """Valid attitude request should return 200."""
        payload = {
            "inertia_x": 100.0,
            "inertia_y": 200.0,
            "inertia_z": 300.0,
            "omega_x": 0.1,
            "omega_y": 0.1,
            "omega_z": 0.1,
            "torque_x": 0.0,
            "torque_y": 0.0,
            "torque_z": 0.0,
        }
        response = client.post("/api/gnc/attitude", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "omega_dot_x" in data
        assert "omega_dot_y" in data
        assert "omega_dot_z" in data
        assert "rotational_kinetic_energy" in data
        assert "angular_momentum_magnitude" in data
        assert "assumptions" in data

    def test_attitude_default_torques(self, client):
        """Torques should default to zero if not provided."""
        payload = {
            "inertia_x": 100.0,
            "inertia_y": 100.0,
            "inertia_z": 100.0,
            "omega_x": 0.0,
            "omega_y": 0.0,
            "omega_z": 0.1,
        }
        response = client.post("/api/gnc/attitude", json=payload)

        assert response.status_code == 200
        data = response.json()

        # For symmetric body with pure spin, accelerations should be zero
        assert abs(data["omega_dot_x"]) < 1e-10
        assert abs(data["omega_dot_y"]) < 1e-10
        assert abs(data["omega_dot_z"]) < 1e-10

    def test_attitude_invalid_inertia(self, client):
        """Zero or negative inertia should return 422."""
        payload = {
            "inertia_x": 0.0,  # Invalid: must be > 0
            "inertia_y": 100.0,
            "inertia_z": 100.0,
            "omega_x": 0.1,
            "omega_y": 0.1,
            "omega_z": 0.1,
        }
        response = client.post("/api/gnc/attitude", json=payload)

        assert response.status_code == 422

    def test_attitude_missing_required_field(self, client):
        """Missing required field should return 422."""
        payload = {
            "inertia_x": 100.0,
            # Missing inertia_y, inertia_z, omega_x, omega_y, omega_z
        }
        response = client.post("/api/gnc/attitude", json=payload)

        assert response.status_code == 422


class TestOrbitEndpoint:
    """Tests for /api/gnc/orbit endpoint."""

    def test_valid_orbit_request(self, client):
        """Valid orbit request should return 200."""
        payload = {
            "semi_major_axis": R_EARTH + 400.0,
            "eccentricity": 0.01,
            "gravitational_parameter": MU_EARTH,
            "central_body_radius": R_EARTH,
            "true_anomaly": 0.0,
        }
        response = client.post("/api/gnc/orbit", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "orbital_period" in data
        assert "mean_motion" in data
        assert "radius" in data
        assert "velocity" in data
        assert "periapsis_radius" in data
        assert "apoapsis_radius" in data
        assert "specific_orbital_energy" in data
        assert "specific_angular_momentum" in data

    def test_orbit_default_parameters(self, client):
        """Default Earth parameters should be used if not specified."""
        payload = {
            "semi_major_axis": 7000.0,
            "eccentricity": 0.0,
            # gravitational_parameter and central_body_radius should default to Earth
        }
        response = client.post("/api/gnc/orbit", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify reasonable LEO values
        assert 5000 < data["orbital_period"] < 6000  # ~90 min
        assert 7.0 < data["velocity"] < 8.0  # ~7.5 km/s

    def test_orbit_invalid_eccentricity(self, client):
        """Eccentricity >= 1 should return 422 (not elliptical)."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 1.0,  # Invalid: must be < 1
        }
        response = client.post("/api/gnc/orbit", json=payload)

        assert response.status_code == 422

    def test_orbit_negative_semi_major_axis(self, client):
        """Negative semi-major axis should return 422."""
        payload = {
            "semi_major_axis": -10000.0,  # Invalid
            "eccentricity": 0.1,
        }
        response = client.post("/api/gnc/orbit", json=payload)

        assert response.status_code == 422


class TestRelativeMotionEndpoint:
    """Tests for /api/gnc/relative endpoint."""

    def test_valid_relative_request(self, client):
        """Valid relative motion request should return 200."""
        payload = {
            "chief_semi_major_axis": R_EARTH + 400.0,
            "gravitational_parameter": MU_EARTH,
            "x0": 1.0,
            "y0": 0.0,
            "z0": 0.0,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            "propagation_time": 1000.0,
        }
        response = client.post("/api/gnc/relative", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "x" in data
        assert "y" in data
        assert "z" in data
        assert "x_dot" in data
        assert "y_dot" in data
        assert "z_dot" in data
        assert "range_magnitude" in data
        assert "range_rate" in data
        assert "is_bounded" in data
        assert "drift_rate" in data

    def test_relative_default_mu(self, client):
        """Default gravitational parameter should be Earth."""
        payload = {
            "chief_semi_major_axis": 7000.0,
            "x0": 0.0,
            "y0": 0.0,
            "z0": 1.0,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            "propagation_time": 1000.0,
        }
        response = client.post("/api/gnc/relative", json=payload)

        assert response.status_code == 200

    def test_relative_negative_propagation_time(self, client):
        """Negative propagation time should return 422."""
        payload = {
            "chief_semi_major_axis": 7000.0,
            "x0": 1.0,
            "y0": 0.0,
            "z0": 0.0,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            "propagation_time": -100.0,  # Invalid
        }
        response = client.post("/api/gnc/relative", json=payload)

        assert response.status_code == 422


class TestOrbitalTrajectoryEndpoint:
    """Tests for /api/gnc/orbit/trajectory endpoint."""

    def test_valid_orbital_trajectory_request(self, client):
        """Valid orbital trajectory request should return 200."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 0.2,
            "central_body_radius": R_EARTH,
            "num_points": 50,
        }
        response = client.post("/api/gnc/orbit/trajectory", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "points" in data
        assert len(data["points"]) == 50
        assert "semi_major_axis" in data
        assert "semi_minor_axis" in data
        assert "periapsis_radius" in data
        assert "apoapsis_radius" in data

        # Verify point structure
        point = data["points"][0]
        assert "x" in point
        assert "y" in point
        assert "t" in point

    def test_orbital_trajectory_defaults(self, client):
        """Default values should be used if not specified."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 0.1,
            # num_points should default to 100
        }
        response = client.post("/api/gnc/orbit/trajectory", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert len(data["points"]) == 100

    def test_orbital_trajectory_invalid_num_points(self, client):
        """num_points outside valid range should return 422."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 0.1,
            "num_points": 5,  # Invalid: must be >= 10
        }
        response = client.post("/api/gnc/orbit/trajectory", json=payload)

        assert response.status_code == 422


class TestRelativeTrajectoryEndpoint:
    """Tests for /api/gnc/relative/trajectory endpoint."""

    def test_valid_relative_trajectory_request(self, client):
        """Valid relative trajectory request should return 200."""
        payload = {
            "chief_semi_major_axis": R_EARTH + 400.0,
            "gravitational_parameter": MU_EARTH,
            "x0": 0.5,
            "y0": 0.0,
            "z0": 0.1,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            "num_orbits": 1.0,
            "num_points": 100,
        }
        response = client.post("/api/gnc/relative/trajectory", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Verify response schema
        assert "points" in data
        assert len(data["points"]) == 100
        assert "orbital_period" in data
        assert "is_bounded" in data
        assert "max_range" in data

        # Verify point structure includes z
        point = data["points"][0]
        assert "x" in point
        assert "y" in point
        assert "z" in point
        assert "t" in point

    def test_relative_trajectory_defaults(self, client):
        """Default values should be used if not specified."""
        payload = {
            "chief_semi_major_axis": 7000.0,
            "x0": 1.0,
            "y0": 0.0,
            "z0": 0.0,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            # num_orbits and num_points should default
        }
        response = client.post("/api/gnc/relative/trajectory", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert len(data["points"]) == 100  # Default

    def test_relative_trajectory_invalid_num_orbits(self, client):
        """num_orbits outside valid range should return 422."""
        payload = {
            "chief_semi_major_axis": 7000.0,
            "x0": 1.0,
            "y0": 0.0,
            "z0": 0.0,
            "x_dot0": 0.0,
            "y_dot0": 0.0,
            "z_dot0": 0.0,
            "num_orbits": 15.0,  # Invalid: must be <= 10
        }
        response = client.post("/api/gnc/relative/trajectory", json=payload)

        assert response.status_code == 422


class TestCORSAndHeaders:
    """Tests for CORS and response headers."""

    def test_content_type_json(self, client):
        """Response should have JSON content type."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 0.1,
        }
        response = client.post("/api/gnc/orbit", json=payload)

        assert response.headers["content-type"] == "application/json"


class TestResponseConsistency:
    """Tests for response data consistency."""

    def test_orbit_calculation_consistency(self, client):
        """Same input should produce same output."""
        payload = {
            "semi_major_axis": 10000.0,
            "eccentricity": 0.3,
            "true_anomaly": 45.0,
        }

        response1 = client.post("/api/gnc/orbit", json=payload)
        response2 = client.post("/api/gnc/orbit", json=payload)

        assert response1.json() == response2.json()

    def test_attitude_calculation_consistency(self, client):
        """Same input should produce same output."""
        payload = {
            "inertia_x": 100.0,
            "inertia_y": 200.0,
            "inertia_z": 300.0,
            "omega_x": 0.1,
            "omega_y": 0.2,
            "omega_z": 0.3,
        }

        response1 = client.post("/api/gnc/attitude", json=payload)
        response2 = client.post("/api/gnc/attitude", json=payload)

        assert response1.json() == response2.json()
