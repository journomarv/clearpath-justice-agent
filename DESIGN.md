# ClearPath Justice Design Contract

## Product identity

ClearPath Justice is a South African digital-justice platform for navigating criminal-record relief and related legal pathways.

The product must feel trustworthy, calm, human and practical — not like a government portal, generic chatbot, or charity donation site.

**Core principle:** AI assists; it does not adjudicate.

**ClearPath** is the organisation/platform brand. **Path** is the citizen-facing assistant within ClearPath and should feel like the same product family, not a separate company.

## Visual direction

Use a restrained civic-professional aesthetic:
- deep navy for trust and structure
- green for action and progress
- restrained warm gold as an accent
- bright surfaces
- strong text contrast
- rounded but not playful controls
- subtle borders
- calm motion

Avoid:
- AI neon gradients
- excessive glassmorphism
- loud startup aesthetics
- decorative legal clichés
- excessive cards
- animation that competes with the conversation

## Brand hierarchy

1. ClearPath Justice — primary organisation/product identity.
2. Path — conversational assistant identity.
3. Assess, Prepare, Manage, Refer and Verify — feature areas.

ClearPath branding should remain visible in the application shell.

Path may have its own geometric/path mark, but typography and visual language must remain consistent with ClearPath.

## Color system

Use semantic tokens from `design/clearpath/tokens.css`.

Core palette:

- Navy: #0B2239
- Navy light: #16324F
- Green: #2E6B44
- Green light: #E8F0EB
- Gold: #D4A537
- Background: #F7F9F9
- Surface: #FFFFFF
- Text: #1A1A1A
- Muted text: #5C6875
- Border: #E2E8F0

Gold is an accent, not a primary interaction color.

## Typography

Use Inter where available, with a system sans-serif fallback.

Keep headings compact and strong.

Body text must remain highly readable.

Labels should use letter spacing sparingly.

## Layout

The product is conversation-first.

On desktop:
- keep navigation visually subordinate to the conversation
- give the central Path experience the most visual weight
- avoid excessive application chrome

On mobile:
- prioritize the conversation and composer
- use comfortable touch targets
- never rely on hover states

## Path conversation

Path should feel like a calm guide, not an oracle.

Preferred language:

- "I can help you understand the process."
- "Let's work through this step by step."
- "Based on the information you've shared..."
- "This may need to be checked by a human reviewer."

Avoid language implying legal adjudication:

- "You are definitely eligible."
- "Your case qualifies."
- "The law says you will succeed."
- "I have decided."

The UI should visually distinguish:

- user messages
- Path explanations
- verified source information
- next actions
- human-review/referral states

## Components

Primary buttons use green.

Secondary buttons use light surfaces with borders.

Destructive actions must be explicit.

Use cards for meaningful grouping, not every piece of content.

Keep borders subtle and shadows restrained.

Inputs need:
- clear labels
- visible focus states
- helpful validation

Navigation active states may use green text with a light green surface.

Official sources should be easy to identify.

Never make an LLM-generated statement look like an official government decision.

## Accessibility

Target:

- at least 4.5:1 contrast for normal text
- at least 3:1 for large text

Every interactive control needs visible `:focus-visible` styling.

Preserve:
- semantic HTML
- keyboard interaction
- accessible form labels
- reduced-motion preferences

## Motion

Use restrained, purposeful motion.

Recommended:
- entry: approximately 200ms
- exit: approximately 140ms
- ease-out transitions

Avoid decorative continuous motion in the main conversation.

## Responsive behavior

The design must work at phone, tablet and desktop widths without requiring a framework migration.

Do not introduce React, Next.js, TypeScript, Tailwind or another component framework merely to implement visual changes.

The current ClearPath frontend is intentionally HTML/CSS/JavaScript.

## Protected application contract

A visual redesign must not change these backend contracts unless backend work is explicitly requested:

- `/chat`
- `/assess`
- `/health`
- `/relief-types`

Do not alter:

- `app/rules/`
- `app/knowledge/`
- `app/privacy.py`
- `app/agent.py`
- `app/deepseek.py`
- Pydantic request/response schemas
- environment variable names
- legal eligibility logic
- source-of-truth URLs

Never invent legal rules, fees, thresholds, deadlines or eligibility criteria.

## PWA requirements

Preserve:

- existing PWA behavior
- manifest metadata
- service-worker behavior
- offline shell behavior
- existing application routes
- existing API integration

## Implementation rule

When a design change can be achieved by editing:

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`
- frontend assets

prefer that over architectural changes.

The goal is a polished ClearPath Justice product — not a technology migration.
