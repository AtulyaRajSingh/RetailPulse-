# RetailPulse Design System

This document describes the design tokens, color palette, typography, and component guidelines for the RetailPulse UI redesign.

## Palette
- Primary: #2563EB
- Secondary: #3B82F6
- Accent: #06B6D4
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Background (Dark): #0F172A
- Surface (Dark): #1E293B
- Text (Dark): #F8FAFC

## Typography
- Primary fonts: Inter, Manrope, Poppins
- Hierarchy:
  - H1: 32px, 800
  - H2: 24px, 700
  - H3: 18px, 600
  - Body: 14-16px, 400

## Components (Guidelines)
- Navbar: sticky, glassmorphism backdrop, logo left, nav links, theme toggle, profile on right.
- Footer: sticky bottom, centered, text: "Made by Atulya Raj Singh".
- Sidebar: collapsible, icons for items, active state highlight, mobile drawer.
- Buttons: gradient backgrounds, hover glow, disabled/loading states.
- Cards: rounded corners, soft elevation, hover lift.
- Forms: floating labels, clear validation colors.
- Tables: sticky headers, zebra rows, search and pagination controls.

## Animations
- Prefer CSS transforms and opacity transitions for performance.
- Use entrance fades and subtle translateY for cards and charts.

## Accessibility
- Maintain WCAG contrast ratios for all text.
- Provide keyboard focus states and ARIA labels on interactive elements.

## How to use
- Tokens are available in `src/utils/design_tokens.py` for Python and can be referenced by Streamlit templates.

