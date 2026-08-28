# PRODX POS Design System

## Direction

PRODX POS uses a **Premium Matte Orange** visual language: bright warm orange as the primary brand signal, white and warm gray for Light Mode, and charcoal/near-black for Dark Mode. Components use soft premium rounding, restrained shadows, and high-contrast states so the interface remains practical for long retail shifts.

## Brand tokens

| Token | Value | Usage |
|---|---|---|
| `--brand` | `#F66A00` | Primary actions, active states, highlights |
| `--brand-2` | `#FF7D18` | Secondary orange / emphasis |
| `--brand-3` | `#FF9A3D` | Gradient start / warm accent |
| `--ink` | `#171310` | Primary text |
| `--muted` | `#7D726A` | Secondary text |
| `--line` | `#EADFD5` | Borders and dividers |
| `--soft` | `#FFF4E9` | Soft orange surfaces |
| `--radius-xl` | `30px` | Hero/login surfaces |
| `--radius-lg` | `24px` | Major cards |
| `--radius-md` | `18px` | Controls and metric cards |

## Light / Dark

- **Light:** `#FFFAF5` page background, white surfaces, warm gray borders, orange primary actions.
- **Dark:** `#0F0D0C` to `#30241E` background, charcoal surfaces, orange accents, soft warm borders.
- Orange is an emphasis color, not a blanket background color; reserve it for actions, active navigation, key metrics, and brand moments.

## Component rules

- Cards: 18–30px radius, subtle 1px warm border, restrained shadow.
- Primary buttons: warm orange gradient, white text, 16px radius, strong focus/disabled states.
- Inputs: 52px minimum height, 16px radius, visible focus ring, accessible labels and placeholders.
- Navigation: quiet neutral state; orange-tinted active state with clear text contrast.
- Metrics: concise label, prominent value, optional trend indicator.
- POS cart: persistent total and full-width checkout action.
- Responsive behavior: collapse the sidebar and stack POS panels on smaller screens; keep touch targets comfortable.

## Accessibility and production constraints

- Keep keyboard focus visible.
- Do not rely on color alone for success, warning, or error meaning.
- Preserve readable contrast in both themes.
- Keep money values as display strings from server-authoritative data; the visual layer must not perform financial calculations beyond presentation.
- UI changes must continue to pass the frontend quality gate and must not weaken backend architecture/security gates.

## Reference implementation

The initial production implementation lives in `frontend/src/main.tsx` and `frontend/src/styles.css`. This document is the visual contract for subsequent Login, Dashboard, POS, Products, Inventory, Reports, and responsive variants.
