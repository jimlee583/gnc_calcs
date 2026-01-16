"""
GNC API Router - Guidance, Navigation, and Control Endpoints

This router provides HTTP endpoints for GNC calculations. Each endpoint
delegates to the corresponding service module for computation.

All calculations are stateless and deterministic - given the same inputs,
the outputs will always be identical. This design supports:
    - Easy testing and validation
    - Caching of results
    - Future agent/tool integration
"""

from fastapi import APIRouter, HTTPException

from app.schemas.gnc import (
    AttitudeInput,
    AttitudeOutput,
    OrbitalInput,
    OrbitalOutput,
    RelativeMotionInput,
    RelativeMotionOutput,
)
from app.services.gnc.attitude_dynamics import compute_attitude_dynamics
from app.services.gnc.orbital_dynamics import compute_orbital_dynamics
from app.services.gnc.relative_motion import compute_relative_motion

router = APIRouter()


@router.post("/attitude", response_model=AttitudeOutput)
async def calculate_attitude_dynamics(inputs: AttitudeInput) -> AttitudeOutput:
    """
    Calculate rigid-body attitude dynamics using Euler's equations.
    
    Computes instantaneous angular accelerations given the spacecraft's
    inertia properties, current angular velocity, and applied torques.
    
    Returns angular accelerations and derived quantities including
    rotational kinetic energy and angular momentum magnitude.
    """
    try:
        return compute_attitude_dynamics(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/orbit", response_model=OrbitalOutput)
async def calculate_orbital_dynamics(inputs: OrbitalInput) -> OrbitalOutput:
    """
    Calculate two-body orbital dynamics from classical orbital elements.
    
    Computes orbital parameters including period, velocities at apses,
    and specific mechanical quantities (energy, angular momentum).
    
    Position and velocity at a specific true anomaly can be computed
    by providing that angle in the input.
    """
    try:
        return compute_orbital_dynamics(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/relative", response_model=RelativeMotionOutput)
async def calculate_relative_motion(inputs: RelativeMotionInput) -> RelativeMotionOutput:
    """
    Calculate relative motion using Clohessy-Wiltshire equations.
    
    Propagates the relative state of a deputy spacecraft with respect to
    a chief spacecraft in a circular orbit. Uses the closed-form solution
    to the linearized equations of relative motion.
    
    Returns the propagated state, range/range-rate, and drift analysis.
    """
    try:
        return compute_relative_motion(inputs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
