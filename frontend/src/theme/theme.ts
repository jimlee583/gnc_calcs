/**
 * Theme Configuration for GNC Calculations App
 * 
 * This module provides TypeScript-accessible theme tokens that mirror
 * the CSS custom properties defined in index.css. Use these for
 * inline styles or styled-components when CSS variables aren't suitable.
 */

export const colors = {
  // Background colors
  bg: {
    base: '#FAFAF8',
    surface: '#FFFFFF',
    elevated: '#FFFFFF',
    muted: '#F1F5F9',
  },
  
  // Grid/engineering paper feel
  grid: {
    line: '#E2E8F0',
    accent: '#CBD5E1',
  },
  
  // Primary palette
  primary: {
    default: '#4A6FA5',
    hover: '#3D5D8A',
    light: '#EBF1F8',
  },
  
  // Text colors
  text: {
    primary: '#1E293B',
    secondary: '#475569',
    muted: '#94A3B8',
    inverse: '#FFFFFF',
  },
  
  // Semantic colors
  semantic: {
    success: '#059669',
    warning: '#D97706',
    error: '#DC2626',
    info: '#0284C7',
  },
  
  // Border colors
  border: {
    default: '#E2E8F0',
    strong: '#CBD5E1',
  },
} as const;

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.08)',
} as const;

export const spacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '3rem',
} as const;

export const radius = {
  sm: '0.25rem',
  md: '0.5rem',
  lg: '0.75rem',
} as const;

export const fonts = {
  sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  mono: "'IBM Plex Mono', 'SF Mono', 'Fira Code', monospace",
} as const;

export const fontSizes = {
  xs: '0.75rem',
  sm: '0.875rem',
  base: '1rem',
  lg: '1.125rem',
  xl: '1.25rem',
  '2xl': '1.5rem',
  '3xl': '1.875rem',
} as const;

export const theme = {
  colors,
  shadows,
  spacing,
  radius,
  fonts,
  fontSizes,
} as const;

export type Theme = typeof theme;
