# PRODX POS — Design System Foundation

Status: **ACTIVE / v1.0**

This is the UI foundation for PRODX POS. The Final Logo is locked and must be treated as a reusable brand asset across the product.

## 1. Brand direction

**Premium · Modern · Professional · Clean · Confident**

The interface should feel trustworthy and operationally focused rather than decorative. Visual richness comes from hierarchy, spacing, typography, restrained gradients, and precise components.

## 2. Brand colors

### Primary accent

- Premium Orange: `#FF6A00`
- Bright Orange: `#FF7A18`
- Soft Peach: `#FFB07A`
- Deep Orange: `#E94B00`

Use orange primarily for primary actions, active states, important highlights, and the P monogram. Avoid flooding entire screens with orange.

### Neutral foundation

- Ink: `#111827`
- Slate: `#475569`
- Muted: `#64748B`
- Border: `#E2E8F0`
- Surface: `#FFFFFF`
- Canvas: `#F8FAFC`

Dark mode uses deep neutral surfaces and the same brand orange accent; the logo geometry does not change.

## 3. Typography

Use a clean modern sans-serif with strong numeric legibility.

Hierarchy:

- Display: bold, reserved for key totals or primary page titles.
- H1/H2: semibold/bold.
- Body: regular/medium.
- Labels: medium/semibold.
- POS numeric values: semibold/bold with tabular numerals where supported.

Avoid excessive font weights and all-caps text except compact status labels.

## 4. Shape language

- Corner radius: soft and consistent.
- Inputs/buttons: medium radius.
- Cards: medium-to-large radius.
- Avoid excessive pill shapes unless the component is a status/filter control.
- Borders should be subtle and never compete with content.

## 5. Elevation

Use soft, low-contrast shadows. The product should look premium without heavy glassmorphism or exaggerated 3D effects.

Preferred elevation levels:

- Level 0: flat surface.
- Level 1: subtle card separation.
- Level 2: modal/popover emphasis.
- Level 3: focused overlay only.

## 6. Buttons and actions

Primary action:

- Orange brand fill.
- High-contrast text.
- Clear hover/focus/disabled states.
- Reserved for the principal action in a context.

Secondary action:

- Neutral surface with clear border.

Destructive action:

- Use semantic danger styling; never substitute brand orange for destructive meaning.

## 7. Form controls

Inputs must provide:

- Visible label or accessible name.
- Clear focus state.
- Error state with useful message.
- Disabled/read-only state.
- Password visibility control where applicable.

Login UI should follow the approved PRODX POS login reference and remain responsive across mobile, tablet, and desktop.

## 8. POS operational UX

Priority order:

1. Transaction correctness.
2. Fast scanning/input.
3. Clear totals and payment state.
4. Error prevention.
5. Accessibility.
6. Visual polish.

Do not sacrifice financial or inventory clarity for visual effects.

## 9. Responsive behavior

Design for:

- Mobile: compact single-column layouts.
- Tablet: optimized POS working area with touch-friendly targets.
- Desktop: multi-column workspace with persistent navigation/context where useful.

Interactive targets should remain comfortable for touch operation.

## 10. Accessibility

- Maintain strong text/background contrast.
- Never communicate meaning by color alone.
- Preserve visible keyboard focus.
- Provide semantic labels and accessible names.
- Respect reduced-motion preferences.
- Ensure error and success states are understandable without relying solely on animation.

## 11. Logo rules

Reference: `docs/design/PRODX_POS_FINAL_LOGO.md`

The final logo must not be independently redrawn, distorted, stretched, recolored outside the approved palette, or given heavy effects. Use one reusable logo component/asset wherever possible.

## 12. Component architecture

Recommended shared component layers:

- Brand: Logo, Wordmark, BrandMark.
- Foundation: Button, Input, Select, Checkbox, Badge, IconButton.
- Layout: AppShell, PageHeader, Card, Stack, Grid, Divider.
- Feedback: Alert, Toast, EmptyState, LoadingState, ErrorState.
- POS: ProductTile, CartLine, CartSummary, PaymentPanel, ShiftStatus.
- Data: DataTable, Pagination, FilterBar, SearchField.
- Overlay: Dialog, Drawer, Popover, ConfirmDialog.

Components should consume design tokens rather than hard-code visual values per screen.

## 13. Implementation rule

UI work may evolve, but it must remain compatible with this foundation. A screen-specific visual decision should become a shared token/component when it repeats across the product.

The Final Logo is locked; the rest of the Design System can be iterated through versioned changes without breaking the brand identity.
