import { useMemo } from 'react';
import type { TrajectoryPoint } from '../api/types';
import styles from './TrajectoryPlot.module.css';

interface TrajectoryPlotProps {
  /** Array of trajectory points to plot */
  points: TrajectoryPoint[];
  /** Width of the SVG in pixels */
  width?: number;
  /** Height of the SVG in pixels */
  height?: number;
  /** Plot title */
  title?: string;
  /** X-axis label */
  xLabel?: string;
  /** Y-axis label */
  yLabel?: string;
  /** Whether to show the origin marker */
  showOrigin?: boolean;
  /** Optional circle to draw at origin (e.g., central body) */
  originRadius?: number;
  /** Color of the trajectory line */
  lineColor?: string;
  /** Show start and end markers */
  showEndpoints?: boolean;
}

/**
 * TrajectoryPlot - SVG-based 2D trajectory visualization
 * 
 * Renders trajectory points as a path in an SVG with proper scaling,
 * axis labels, and grid lines. Designed for the engineering aesthetic.
 */
export function TrajectoryPlot({
  points,
  width = 400,
  height = 300,
  title,
  xLabel = 'X',
  yLabel = 'Y',
  showOrigin = true,
  originRadius,
  lineColor = 'var(--color-primary)',
  showEndpoints = true,
}: TrajectoryPlotProps) {
  // Calculate bounds and scaling
  const plotData = useMemo(() => {
    if (points.length === 0) {
      return null;
    }

    // Find data bounds
    const xValues = points.map((p) => p.x);
    const yValues = points.map((p) => p.y);
    
    let xMin = Math.min(...xValues, 0);
    let xMax = Math.max(...xValues, 0);
    let yMin = Math.min(...yValues, 0);
    let yMax = Math.max(...yValues, 0);

    // Include origin radius in bounds if specified
    if (originRadius) {
      xMin = Math.min(xMin, -originRadius);
      xMax = Math.max(xMax, originRadius);
      yMin = Math.min(yMin, -originRadius);
      yMax = Math.max(yMax, originRadius);
    }

    // Add padding (10%)
    const xRange = xMax - xMin || 1;
    const yRange = yMax - yMin || 1;
    const padding = 0.1;
    
    xMin -= xRange * padding;
    xMax += xRange * padding;
    yMin -= yRange * padding;
    yMax += yRange * padding;

    // Plotting area (leave room for labels)
    const margin = { top: 30, right: 20, bottom: 40, left: 50 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    // Scale functions
    const scaleX = (x: number) =>
      margin.left + ((x - xMin) / (xMax - xMin)) * plotWidth;
    const scaleY = (y: number) =>
      margin.top + plotHeight - ((y - yMin) / (yMax - yMin)) * plotHeight;

    // Generate path
    const pathD = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.y)}`)
      .join(' ');

    // Grid lines (5 lines each axis)
    const xTicks = Array.from({ length: 5 }, (_, i) => 
      xMin + (i / 4) * (xMax - xMin)
    );
    const yTicks = Array.from({ length: 5 }, (_, i) =>
      yMin + (i / 4) * (yMax - yMin)
    );

    return {
      pathD,
      margin,
      plotWidth,
      plotHeight,
      scaleX,
      scaleY,
      xTicks,
      yTicks,
      xMin,
      xMax,
      yMin,
      yMax,
      startPoint: points[0],
      endPoint: points[points.length - 1],
    };
  }, [points, width, height, originRadius]);

  if (!plotData) {
    return (
      <div className={styles.placeholder}>
        No trajectory data
      </div>
    );
  }

  const { pathD, margin, plotWidth, plotHeight, scaleX, scaleY, xTicks, yTicks, startPoint, endPoint } = plotData;

  // Format tick labels (use scientific notation for large/small numbers)
  const formatTick = (val: number): string => {
    if (Math.abs(val) < 0.01 || Math.abs(val) >= 10000) {
      return val.toExponential(1);
    }
    return val.toFixed(2);
  };

  return (
    <div className={styles.container}>
      {title && <h5 className={styles.title}>{title}</h5>}
      <svg
        width={width}
        height={height}
        className={styles.svg}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Grid lines */}
        <g className={styles.grid}>
          {xTicks.map((x, i) => (
            <line
              key={`x-${i}`}
              x1={scaleX(x)}
              y1={margin.top}
              x2={scaleX(x)}
              y2={margin.top + plotHeight}
            />
          ))}
          {yTicks.map((y, i) => (
            <line
              key={`y-${i}`}
              x1={margin.left}
              y1={scaleY(y)}
              x2={margin.left + plotWidth}
              y2={scaleY(y)}
            />
          ))}
        </g>

        {/* Axes */}
        <g className={styles.axes}>
          {/* X axis */}
          <line
            x1={margin.left}
            y1={margin.top + plotHeight}
            x2={margin.left + plotWidth}
            y2={margin.top + plotHeight}
          />
          {/* Y axis */}
          <line
            x1={margin.left}
            y1={margin.top}
            x2={margin.left}
            y2={margin.top + plotHeight}
          />
        </g>

        {/* Tick labels */}
        <g className={styles.tickLabels}>
          {xTicks.map((x, i) => (
            <text
              key={`xl-${i}`}
              x={scaleX(x)}
              y={margin.top + plotHeight + 15}
              textAnchor="middle"
            >
              {formatTick(x)}
            </text>
          ))}
          {yTicks.map((y, i) => (
            <text
              key={`yl-${i}`}
              x={margin.left - 8}
              y={scaleY(y) + 4}
              textAnchor="end"
            >
              {formatTick(y)}
            </text>
          ))}
        </g>

        {/* Axis labels */}
        <g className={styles.axisLabels}>
          <text
            x={margin.left + plotWidth / 2}
            y={height - 5}
            textAnchor="middle"
          >
            {xLabel}
          </text>
          <text
            x={12}
            y={margin.top + plotHeight / 2}
            textAnchor="middle"
            transform={`rotate(-90, 12, ${margin.top + plotHeight / 2})`}
          >
            {yLabel}
          </text>
        </g>

        {/* Origin marker */}
        {showOrigin && (
          <g className={styles.origin}>
            <circle
              cx={scaleX(0)}
              cy={scaleY(0)}
              r={4}
            />
            {/* Crosshairs at origin */}
            <line
              x1={scaleX(0) - 8}
              y1={scaleY(0)}
              x2={scaleX(0) + 8}
              y2={scaleY(0)}
            />
            <line
              x1={scaleX(0)}
              y1={scaleY(0) - 8}
              x2={scaleX(0)}
              y2={scaleY(0) + 8}
            />
          </g>
        )}

        {/* Central body circle (e.g., Earth) */}
        {originRadius && (
          <circle
            cx={scaleX(0)}
            cy={scaleY(0)}
            r={Math.abs(scaleX(originRadius) - scaleX(0))}
            className={styles.centralBody}
          />
        )}

        {/* Trajectory path */}
        <path
          d={pathD}
          fill="none"
          stroke={lineColor}
          strokeWidth={2}
          className={styles.trajectory}
        />

        {/* Start and end markers */}
        {showEndpoints && (
          <g>
            <circle
              cx={scaleX(startPoint.x)}
              cy={scaleY(startPoint.y)}
              r={5}
              className={styles.startMarker}
            />
            <circle
              cx={scaleX(endPoint.x)}
              cy={scaleY(endPoint.y)}
              r={5}
              className={styles.endMarker}
            />
          </g>
        )}
      </svg>
      {showEndpoints && (
        <div className={styles.legend}>
          <span className={styles.legendStart}>Start</span>
          <span className={styles.legendEnd}>End</span>
        </div>
      )}
    </div>
  );
}
