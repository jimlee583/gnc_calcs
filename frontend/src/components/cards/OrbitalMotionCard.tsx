import { useState } from 'react';
import { calculateOrbit, getOrbitalTrajectory } from '../../api/gnc';
import type { OrbitalInput, OrbitalOutput, OrbitalTrajectoryOutput } from '../../api/types';
import {
  GncCard,
  CardSection,
  CardInput,
  CardOutput,
  CardButton,
} from './GncCard';
import { TrajectoryPlot } from '../TrajectoryPlot';
import styles from './CalculationCard.module.css';

/**
 * OrbitalMotionCard - Two-Body Keplerian Orbital Mechanics
 * 
 * This card computes orbital parameters from classical orbital elements
 * using two-body dynamics. Central body defaults to Earth.
 * 
 * Key Equations:
 *   Vis-viva:        v² = μ(2/r - 1/a)
 *   Orbit equation:  r = a(1-e²) / (1 + e·cos(ν))
 *   Period:          T = 2π√(a³/μ)
 *   Specific energy: ε = -μ/(2a)
 * 
 * TODO: Add support for hyperbolic orbits (e ≥ 1)
 * TODO: Add J2 secular perturbation corrections
 * TODO: Add ground track visualization
 */
export function OrbitalMotionCard() {
  // Input state - LEO satellite defaults
  const [inputs, setInputs] = useState<OrbitalInput>({
    semi_major_axis: 6778,           // km (400 km altitude circular)
    eccentricity: 0.001,             // Nearly circular
    gravitational_parameter: 398600.4418,  // km³/s² (Earth)
    central_body_radius: 6378.137,   // km (Earth equatorial)
    true_anomaly: 0,                 // deg
  });

  const [result, setResult] = useState<OrbitalOutput | null>(null);
  const [trajectory, setTrajectory] = useState<OrbitalTrajectoryOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateInput = <K extends keyof OrbitalInput>(
    key: K,
    value: OrbitalInput[K]
  ) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
  };

  const handleCalculate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Calculate orbital parameters and generate trajectory in parallel
      const [output, traj] = await Promise.all([
        calculateOrbit(inputs),
        getOrbitalTrajectory({
          semi_major_axis: inputs.semi_major_axis,
          eccentricity: inputs.eccentricity,
          central_body_radius: inputs.central_body_radius,
          num_points: 120,
        }),
      ]);
      setResult(output);
      setTrajectory(traj);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to format period as HH:MM:SS
  const formatPeriod = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hrs}h ${mins}m ${secs}s`;
  };

  return (
    <GncCard
      title="Orbital Motion"
      subtitle="Two-body Keplerian orbital mechanics"
      category="Orbital"
      isLoading={isLoading}
      error={error}
    >
      <div className={styles.layout}>
        <div className={styles.inputPanel}>
          <CardSection title="Orbital Elements">
            <CardInput
              label="Semi-major axis (a)"
              unit="km"
              value={inputs.semi_major_axis}
              onChange={(v) => updateInput('semi_major_axis', v)}
              min={100}
            />
            <CardInput
              label="Eccentricity (e)"
              unit=""
              value={inputs.eccentricity}
              onChange={(v) => updateInput('eccentricity', v)}
              min={0}
              max={0.999}
              step={0.001}
            />
            <CardInput
              label="True anomaly (ν)"
              unit="deg"
              value={inputs.true_anomaly ?? 0}
              onChange={(v) => updateInput('true_anomaly', v)}
              min={0}
              max={360}
            />
          </CardSection>

          <CardSection title="Central Body (Earth default)">
            <CardInput
              label="Grav. parameter (μ)"
              unit="km³/s²"
              value={inputs.gravitational_parameter ?? 398600.4418}
              onChange={(v) => updateInput('gravitational_parameter', v)}
              min={0.001}
            />
            <CardInput
              label="Body radius"
              unit="km"
              value={inputs.central_body_radius ?? 6378.137}
              onChange={(v) => updateInput('central_body_radius', v)}
              min={1}
            />
          </CardSection>

          <div className={styles.buttonRow}>
            <CardButton onClick={handleCalculate} disabled={isLoading}>
              Calculate
            </CardButton>
          </div>
        </div>

        {result && (
          <div className={styles.outputPanel}>
            {/* Orbit Visualization */}
            {trajectory && (
              <div className={styles.trajectorySection}>
                <TrajectoryPlot
                  points={trajectory.points}
                  width={380}
                  height={280}
                  title="Orbit Shape (Orbital Plane)"
                  xLabel="X [km]"
                  yLabel="Y [km]"
                  showOrigin={true}
                  originRadius={trajectory.central_body_radius}
                  lineColor="var(--color-primary)"
                  showEndpoints={false}
                />
              </div>
            )}

            <CardSection title="Orbital Period">
              <CardOutput
                label="Period"
                value={result.orbital_period.toFixed(2)}
                unit="s"
              />
              <CardOutput
                label="Period (formatted)"
                value={formatPeriod(result.orbital_period)}
                unit=""
              />
              <CardOutput
                label="Mean motion"
                value={result.mean_motion}
                unit="rad/s"
              />
            </CardSection>

            <CardSection title="State at True Anomaly">
              <CardOutput
                label="Radius"
                value={result.radius.toFixed(3)}
                unit="km"
              />
              <CardOutput
                label="Velocity"
                value={result.velocity.toFixed(4)}
                unit="km/s"
              />
            </CardSection>

            <CardSection title="Apses">
              <CardOutput
                label="Periapsis radius"
                value={result.periapsis_radius.toFixed(3)}
                unit="km"
              />
              <CardOutput
                label="Periapsis altitude"
                value={result.periapsis_altitude.toFixed(3)}
                unit="km"
              />
              <CardOutput
                label="Apoapsis radius"
                value={result.apoapsis_radius.toFixed(3)}
                unit="km"
              />
              <CardOutput
                label="Apoapsis altitude"
                value={result.apoapsis_altitude.toFixed(3)}
                unit="km"
              />
            </CardSection>

            <CardSection title="Velocities at Apses">
              <CardOutput
                label="V at periapsis"
                value={result.periapsis_velocity.toFixed(4)}
                unit="km/s"
              />
              <CardOutput
                label="V at apoapsis"
                value={result.apoapsis_velocity.toFixed(4)}
                unit="km/s"
              />
            </CardSection>

            <CardSection title="Mechanical Properties">
              <CardOutput
                label="Specific energy"
                value={result.specific_orbital_energy}
                unit="km²/s²"
              />
              <CardOutput
                label="Specific ang. mom."
                value={result.specific_angular_momentum.toFixed(3)}
                unit="km²/s"
              />
            </CardSection>

            <div className={styles.assumptions}>
              <h5 className={styles.assumptionsTitle}>Assumptions</h5>
              <ul className={styles.assumptionsList}>
                {result.assumptions.map((assumption, i) => (
                  <li key={i}>{assumption}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </GncCard>
  );
}
