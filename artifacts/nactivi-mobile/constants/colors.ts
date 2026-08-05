/**
 * Semantic design tokens for the mobile app.
 *
 * These tokens mirror the naming conventions used in web artifacts (index.css)
 * so that multi-artifact projects share a cohesive visual identity.
 *
 * Replace the placeholder values below with values that match the project's
 * brand. If a sibling web artifact exists, read its index.css and convert the
 * HSL values to hex so both artifacts use the same palette.
 *
 * To add dark mode, add a `dark` key with the same token names.
 * The useColors() hook will automatically pick it up.
 */

const colors = {
  light: {
    // Legacy aliases (kept for backward compatibility)
    text: '#10261f',
    tint: '#1d875d',

    // Core surfaces
    background: '#f6f8f5',
    foreground: '#10261f',

    // Cards / elevated surfaces
    card: '#ffffff',
    cardForeground: '#10261f',

    // Primary action color (buttons, links, active states)
    primary: '#1d875d',
    primaryForeground: '#ffffff',

    // Secondary / less-emphasis interactive surfaces
    secondary: '#e9f0eb',
    secondaryForeground: '#1d3f31',

    // Muted / subdued elements (dividers, timestamps, placeholders)
    muted: '#e9efea',
    mutedForeground: '#718079',

    // Accent highlights (badges, selected items, focus rings)
    accent: '#dd8b33',
    accentForeground: '#ffffff',

    // Destructive actions (delete, error states)
    destructive: '#c94b4b',
    destructiveForeground: '#ffffff',

    // Borders and input outlines
    border: '#dfe7e0',
    input: '#dfe7e0',
    inputBackground: '#ffffff',
    heroStart: '#12382a',
    heroEnd: '#1d875d',
    heroMuted: '#b7d4c4',
    lime: '#b8dd63',
    blue: '#4f9bc1',
    amber: '#c77b2a',
    amberSoft: '#fbefdf',
    accentSoft: '#e7f2eb',
    error: '#bd4444',
    errorSoft: '#fbe9e9',
    success: '#1d875d',
    successSoft: '#e5f3e9',
    modalBackdrop: 'rgba(8, 25, 17, 0.52)',
  },

  // Border radius (in px). Sync from the sibling web artifact's --radius
  // CSS variable. This value applies to cards, buttons, inputs, and modals.
  radius: 8,
};

export default colors;
