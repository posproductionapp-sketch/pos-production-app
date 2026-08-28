# PRODX POS — Login UI Production Specification

Status: **APPROVED / READY FOR IMPLEMENTATION**

## Purpose

Define the production implementation contract for the approved PRODX POS login experience using the locked Final Logo and Design System v1.0.

## Visual direction

Premium, modern, professional, clean and confident. Use restrained depth, smooth surfaces, precise spacing, and the approved orange/peach brand accent. Avoid excessive 3D, reflection, glow, or decorative imagery.

## Brand

- Use the locked PRODX POS Final Logo.
- Do not redraw, distort, stretch, recolor, or independently modify the logo.
- Preserve the approved dark wordmark and premium orange/gold P treatment.
- Supporting text: `DEVERLOPED BY THODSAWAT`.

## Responsive layouts

### Mobile
- Single-column composition.
- Brand centered and visually dominant without excessive height.
- Login form uses comfortable touch targets.
- Primary action remains immediately accessible.
- Keyboard and small viewport must not obscure the submit action.

### Tablet
- Balanced centered login workspace.
- Increased breathing room while preserving fast POS access.
- Touch targets remain comfortable.

### Desktop
- Centered login card/workspace with restrained supporting brand area.
- Maintain clear visual hierarchy and generous whitespace.
- Avoid unnecessary full-screen decoration.

## Required controls

- Username / email field as required by authentication contract.
- Password field.
- Password visibility control.
- Primary Sign In action.
- Validation/error feedback.
- Loading state.
- Disabled state.
- Accessible labels and keyboard focus.

Optional recovery/help actions may be included only when supported by the authentication contract; do not invent unsupported flows.

## Interaction states

Every control must support default, hover, focus, pressed, disabled and error states where applicable. Loading must prevent duplicate submission and communicate progress without relying only on animation.

## Security UX

- Never expose secrets or sensitive authentication details in client-visible errors.
- Do not persist passwords.
- Respect authentication/rate-limit responses from the server.
- Avoid revealing whether a specific account exists unless the backend contract explicitly permits it.

## Accessibility

- Strong contrast in both themes.
- Visible keyboard focus.
- Semantic labels and accessible names.
- Error messages associated with their fields.
- Touch targets sized for reliable interaction.
- Respect reduced motion.
- Do not use color alone to communicate validation.

## Theme

### Light
White/near-white surface, dark typography, subtle borders/shadows, premium orange accent.

### Dark
Deep neutral surface, light typography, same logo geometry and orange accent. Do not create a separate logo shape.

## Component reuse

Build with the shared component foundation. Do not introduce screen-specific copies of Button, Input, Card, Logo, or feedback components.

## Acceptance criteria

1. Matches the approved PRODX POS visual direction.
2. Uses Final Logo without alteration.
3. Responsive at mobile/tablet/desktop breakpoints.
4. Supports Light/Dark Mode.
5. Complete interaction and validation states.
6. Accessible keyboard/focus/labels/error handling.
7. No unsupported authentication behavior is invented.
8. Uses shared design tokens/components.
9. Production build and relevant tests remain green.

This document is an implementation contract; visual polish can iterate while the brand and functional constraints remain intact.
