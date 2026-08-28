# PRODX POS — Shared UI Component Foundation

Status: **ACTIVE / v1.0**

This contract defines the reusable component layer that all future PRODX POS screens must consume. It extends `PRODX_POS_DESIGN_SYSTEM.md` and the locked `PRODX_POS_FINAL_LOGO.md`.

## 1. Component principles

- Prefer reusable components over screen-specific duplicates.
- Components consume design tokens; screens do not hard-code brand values.
- Preserve semantic HTML and accessible names.
- Every interactive component requires visible focus, disabled, and error behavior where applicable.
- Visual polish must never reduce POS speed, readability, or financial clarity.
- Light and dark modes use the same component API and geometry.

## 2. Foundation components

### Button
Variants: `primary`, `secondary`, `ghost`, `danger`.
States: default, hover, focus-visible, pressed, disabled, loading.
Rules: one primary action per context where practical; danger is reserved for destructive operations.

### Input
Supports label, hint, error, prefix/suffix, password visibility, disabled and read-only states.
Rules: never rely on placeholder text as the only accessible label.

### Select
Supports label, hint, error, disabled, keyboard navigation, and touch-friendly target sizing.

### Checkbox
Supports checked, unchecked, indeterminate, disabled, focus-visible, and validation states.

### Badge
Semantic variants: neutral, success, warning, danger, info, brand.
Do not communicate state by color alone.

### IconButton
Requires an accessible label or tooltip-equivalent accessible name. Use for compact actions only.

## 3. Layout components

- `AppShell` — global application frame and responsive navigation context.
- `PageHeader` — title, description, actions, and contextual status.
- `Card` — grouped content with controlled elevation.
- `Stack` — consistent vertical/horizontal spacing.
- `Grid` — responsive content arrangement.
- `Divider` — structural separation without excessive visual weight.

## 4. Feedback components

- `Alert` — persistent contextual message.
- `Toast` — transient confirmation/error feedback; never the only place for critical transaction information.
- `EmptyState` — clear explanation plus next action where appropriate.
- `LoadingState` — predictable loading treatment; avoid unnecessary layout shifts.
- `ErrorState` — actionable error with safe recovery guidance.

## 5. Overlay components

- `Dialog`
- `ConfirmDialog`
- `Drawer`
- `Popover`

Overlays must manage focus correctly, support keyboard dismissal where appropriate, and remain usable on small screens.

## 6. POS components

- `ProductTile` — product identity, price, stock/status and fast add action.
- `CartLine` — item, quantity, price, discount and removal/edit actions.
- `CartSummary` — subtotal, discount, VAT/tax, total and payment state.
- `PaymentPanel` — payment method, amount tendered, balance/change and completion state.
- `ShiftStatus` — current shift, cashier, opening/closing state and relevant cash status.

Financial values must be rendered from exact server-authoritative values. UI formatting must never introduce floating-point calculations or alter transaction semantics.

## 7. Data components

- `SearchField`
- `FilterBar`
- `DataTable`
- `Pagination`

Data components must support loading, empty, error and responsive states. Tables should collapse or transform appropriately on mobile rather than becoming horizontally unusable.

## 8. Brand components

- `Logo` — locked Final Logo asset/component.
- `BrandMark` — P monogram only.
- `Wordmark` — PRODX POS wordmark.

Brand components must not recreate the logo with arbitrary text, CSS shapes, filters, or screen-specific gradients. They reference the approved brand asset and rules.

## 9. Token contract

Shared components must consume tokens for:

- color
- typography
- spacing
- radius
- border
- elevation/shadow
- motion
- focus ring
- responsive breakpoints

Component implementations should expose semantic variants instead of allowing arbitrary per-screen visual values.

## 10. Responsive contract

- Mobile: single-column first, touch-friendly controls, compact navigation.
- Tablet: efficient touch POS workspace and larger working surfaces.
- Desktop: multi-column operational workspace where useful.

No component should assume a fixed viewport width.

## 11. Accessibility contract

- Keyboard reachable interactive controls.
- Visible focus-visible state.
- Accessible names for icon-only controls.
- Semantic error/success messaging.
- Strong contrast in both themes.
- Reduced-motion support.
- Do not rely on color alone.

## 12. Implementation order

1. Tokens
2. Brand components
3. Button / Input / Select / Checkbox / Badge / IconButton
4. Card / Stack / Grid / PageHeader / AppShell
5. Alert / Toast / Empty / Loading / Error
6. Dialog / Drawer / Popover / ConfirmDialog
7. POS components
8. Data components
9. Login screen composition
10. Main POS screen composition

## 13. Acceptance gate

A new screen is not considered Design-System compliant if it introduces a repeated control or visual pattern that should have been a shared component, hard-codes brand tokens, breaks light/dark parity, or creates an inaccessible interaction.
