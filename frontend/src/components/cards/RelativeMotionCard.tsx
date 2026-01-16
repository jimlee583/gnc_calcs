import { useState } from 'react';
import { calculateRelativeMotion } from '../../api/gnc';
import type { RelativeMotionInput, RelativeMotionOutput } from '../../api/types';
import {
  GncCard,
  CardSection,
  CardInput,
  CardOutput,
  CardButton,
} from './GncCard';
import styles from './CalculationCard.module.css';

/**
 * RelativeMotionCard - Clohessy-Wiltshire (Hill) Equations
 * 
 * This card propagates relative motion between two spacecraft using the
 * linearized CW equations. The chief spacecraft is in a circular orbit
 * and the deputy's motion is described in the LVLH frame.
 * 
 * LVLH Frame (Local Vertical Local Horizontal):
 *   x: Radial (outward from central body)
 *   y: In-track (velocity direction)
 *   z: Cross-track (normal to orbital plane)
 * 
 * CW Equations:
 *   ẍ - 2nẏ - 3n²x = 0
 *   ÿ + 2nẋ = 0
 *   z̈ + n²z = 0
 * 
 * TODO: Add Yamanaka-Ankersen STM for eccentric chief orbits
 * TODO: Add impulsive maneuver planning
 * TODO: Add trajectory visualization
 */
export function RelativeMotionCard() {
  // Input state - typical rendezvous scenario
  const [inputs, setInputs] = useState<RelativeMotionInput>({
    chief_semi_major_axis: 6778,    // km (400 km altitude)
    gravitational_parameter: 398600.4418,
    x0: 0.1,          // km - small radial offset
    y0: -1.0,         // km - 1 km behind
    z0: 0,            // km - in-plane
    x_dot0: 0,        // km/s
    y_dot0: 0,        // km/s
    z_dot0: 0,        // km/s
    propagation_time: 5400,  // s (1.5 orbits)
  });

  const [result, setResult] = useState<RelativeMotionOutput | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateInput = <K extends keyof RelativeMotionInput>(
    key: K,
    value: RelativeMotionInput[K]
  ) => {
    setInputs((prev) => ({ ...prev, [key]: value }));
  };

  const handleCalculate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const output = await calculateRelativeMotion(inputs);
      setResult(output);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <GncCard
      title="Relative Motion"
      subtitle="Clohessy-Wiltshire equations for proximity operations"
      category="Relative"
      isLoading={isLoading}
      error={error}
    >
      <div className={styles.layout}>
        <div className={styles.inputPanel}>
          <CardSection title="Chief Orbit">
            <CardInput
              label="Semi-major axis"
              unit="km"
              value={inputs.chief_semi_major_axis}
              onChange={(v) => updateInput('chief_semi_major_axis', v)}
              min={100}
            />
            <CardInput
              label="Grav. parameter (μ)"
              unit="km³/s²"
              value={inputs.gravitational_parameter ?? 398600.4418}
              onChange={(v) => updateInput('gravitational_parameter', v)}
              min={0.001}
            />
          </CardSection>

          <CardSection title="Initial Position (LVLH)">
            <CardInput
              label="x₀ (radial)"
              unit="km"
              value={inputs.x0}
              onChange={(v) => updateInput('x0', v)}
            />
            <CardInput
              label="y₀ (in-track)"
              unit="km"
              value={inputs.y0}
              onChange={(v) => updateInput('y0', v)}
            />
            <CardInput
              label="z₀ (cross-track)"
              unit="km"
              value={inputs.z0}
              onChange={(v) => updateInput('z0', v)}
            />
          </CardSection>

          <CardSection title="Initial Velocity (LVLH)">
            <CardInput
              label="ẋ₀ (radial)"
              unit="km/s"
              value={inputs.x_dot0}
              onChange={(v) => updateInput('x_dot0', v)}
              step={0.0001}
            />
            <CardInput
              label="ẏ₀ (in-track)"
              unit="km/s"
              value={inputs.y_dot0}
              onChange={(v) => updateInput('y_dot0', v)}
              step={0.0001}
            />
            <CardInput
              label="ż₀ (cross-track)"
              unit="km/s"
              value={inputs.z_dot0}
              onChange={(v) => updateInput('z_dot0', v)}
              step={0.0001}
            />
          </CardSection>

          <CardSection title="Propagation">
            <CardInput
              label="Time"
              unit="s"
              value={inputs.propagation_time}
              onChange={(v) => updateInput('propagation_time', v)}
              min={0}
            />
          </CardSection>

          <div className={styles.buttonRow}>
            <CardButton onClick={handleCalculate} disabled={isLoading}>
              Propagate
            </CardButton>
          </div>
        </div>

        {result && (
          <div className={styles.outputPanel}>
            <CardSection title="Final Position (LVLH)">
              <CardOutput
                label="x (radial)"
                value={result.x}
                unit="km"
              />
              <CardOutput
                label="y (in-track)"
                value={result.y}
                unit="km"
              />
              <CardOutput
                label="z (cross-track)"
                value={result.z}
                unit="km"
              />
            </CardSection>

            <CardSection title="Final Velocity (LVLH)">
              <CardOutput
                label="ẋ (radial)"
                value={result.x_dot}
                unit="km/s"
              />
              <CardOutput
                label="ẏ (in-track)"
                value={result.y_dot}
                unit="km/s"
              />
              <CardOutput
                label="ż (cross-track)"
                value={result.z_dot}
                unit="km/s"
              />
            </CardSection>

            <CardSection title="Range Analysis">
              <CardOutput
                label="Range"
                value={result.range_magnitude}
                unit="km"
              />
              <CardOutput
                label="Range rate"
                value={result.range_rate}
                unit="km/s"
              />
              <CardOutput
                label="Mean motion"
                value={result.mean_motion}
                unit="rad/s"
              />
            </CardSection>

            <CardSection title="Trajectory Characterization">
              <div className={styles.statusIndicator}>
                <span className={styles.statusLabel}>Motion Type:</span>
                <span className={result.is_bounded ? styles.statusGood : styles.statusWarning}>
                  {result.is_bounded ? 'Bounded (No Drift)' : 'Unbounded (Drifting)'}
                </span>
              </div>
              <CardOutput
                label="Drift per orbit"
                value={result.drift_rate}
                unit="km"
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
