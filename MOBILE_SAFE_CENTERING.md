# Mobile-Safe Centering System - Implementation Guide

## Overview
This document describes the mobile-safe centering system implemented across the P.A.T.R.I.O.T. App to fix issues with dynamic browser chrome on iPadOS and mobile Safari.

## Problem Statement
Previously, the app used:
- `100vh` units which don't account for dynamic browser UI
- Fixed positioning with `transform: translate(-50%, -50%)` hacks
- `display: grid` with `place-items: center`

These patterns break on mobile Safari and iPadOS because:
- The viewport height changes as the address bar shows/hides
- Fixed positioning with transform can cause layout shifts
- Content can get cut off or become inaccessible

## Solution

### 1. New Shared Component: `CenteredLayout`

Location: `/shared/ui/components/CenteredLayout/`

A reusable component that provides mobile-safe centering:

```jsx
import CenteredLayout from 'shared/ui/components/CenteredLayout';

<CenteredLayout fullViewport={true} enableScroll={true}>
  <YourContent />
</CenteredLayout>
```

**Props:**
- `fullViewport` (default: true) - Fill the full viewport height
- `enableScroll` (default: true) - Allow scrolling for overflow content
- `className` - Additional CSS classes for the wrapper
- `contentClassName` - Additional CSS classes for the content

**Key Features:**
- Uses `svh` (small viewport height) with `vh` fallback
- Flexbox centering: `display: flex`, `align-items: center`, `justify-content: center`
- Respects safe areas: `env(safe-area-inset-*)`
- Allows overflow scrolling

### 2. Updated Patterns

#### Before (Problematic):
```css
.container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  height: 100vh;
}
```

#### After (Mobile-Safe):
```css
.container {
  position: fixed;
  inset: 0;
  min-height: 100vh; /* Fallback */
  min-height: 100svh; /* Mobile-safe */
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### 3. Viewport Unit Standards

| Unit | Usage | Browser Support |
|------|-------|----------------|
| `vh` | Fallback only | All browsers |
| `svh` | Primary mobile unit | Modern browsers (2023+) |
| `lvh` | Large viewport height | Consider for future |
| `dvh` | Dynamic viewport height | Alternative option |

**Implementation Pattern:**
```css
/* Always provide fallback first */
min-height: 100vh;  /* Fallback */
min-height: 100svh; /* Mobile-safe */
```

### 4. Safe Area Insets

For notched devices (iPhone X+, iPad Pro):

```css
.wrapper {
  padding-top: env(safe-area-inset-top, 0);
  padding-right: env(safe-area-inset-right, 0);
  padding-bottom: env(safe-area-inset-bottom, 0);
  padding-left: env(safe-area-inset-left, 0);
}
```

## Files Updated

### Shared Components
- ✅ `/shared/ui/components/CenteredLayout/` - New component
- ✅ `/shared/ui/components/Layout/Layout.module.css` - Updated to use svh

### Sentinel Login Pages
- ✅ `/sentinel_login/frontend/src/pages/Patriot-Login/Patriot-Login.module.css`
  - Replaced fixed transform centering with flexbox
  - Updated all vh units to svh with fallbacks
  - Removed duplicate CSS blocks
  
- ✅ `/sentinel_login/frontend/src/pages/Register/Register.module.css`
  - Replaced grid centering with flexbox
  - Updated all vh units to svh with fallbacks
  - Fixed responsive breakpoints

### Patriot Pages
All patriot pages already use the Layout component which now has mobile-safe centering. No page-specific changes needed.

## Testing Checklist

### Desktop Browsers
- [ ] Chrome - Content centered correctly
- [ ] Firefox - Content centered correctly
- [ ] Safari - Content centered correctly
- [ ] Edge - Content centered correctly

### Mobile Devices
- [ ] iPhone Safari - Content remains centered when address bar appears/disappears
- [ ] iPad Safari - Content centered in both portrait and landscape
- [ ] Android Chrome - Content centered correctly
- [ ] Android Firefox - Content centered correctly

### Specific Scenarios
- [ ] Login page - Logo and form remain centered
- [ ] Register page - Logo and form remain centered
- [ ] Dashboard - Content fills viewport properly
- [ ] Scroll behavior - Overflow content scrolls correctly
- [ ] Safe areas - No content hidden behind notches
- [ ] Responsive - Works at all breakpoints

## Migration Guide for New Pages

### For Full-Screen Centered Pages (Login, Register style):

```jsx
import CenteredLayout from 'shared/ui/components/CenteredLayout';

function MyPage() {
  return (
    <CenteredLayout>
      <div className={styles.content}>
        {/* Your centered content */}
      </div>
    </CenteredLayout>
  );
}
```

### For App Pages (Dashboard, Settings, etc.):

Use the existing `Layout` component - it already has mobile-safe centering:

```jsx
import Layout from 'shared/ui/components/Layout/Layout';

function MyPage() {
  return (
    <Layout>
      {/* Your page content */}
    </Layout>
  );
}
```

## Best Practices

### DO:
✅ Use `svh` with `vh` fallback for viewport heights
✅ Use flexbox for centering (`display: flex`, `align-items: center`, `justify-content: center`)
✅ Use `min-height` instead of `height` for containers
✅ Use `inset: 0` instead of `top/right/bottom/left: 0`
✅ Test on actual mobile devices, not just device emulators
✅ Add safe area insets for notched devices
✅ Allow overflow scrolling for content that might be taller than viewport

### DON'T:
❌ Use `height: 100vh` without `svh` fallback
❌ Use `top: 50%; left: 50%; transform: translate(-50%, -50%)` for page centering
❌ Use `display: grid; place-items: center` without considering mobile
❌ Trap content vertically (always allow scroll if needed)
❌ Rely on device emulators for final testing

## Browser Support

- **svh unit**: Chrome 108+, Safari 15.4+, Firefox 101+
- **Flexbox**: All modern browsers (IE11+ with prefixes)
- **Safe area insets**: All browsers with notched displays

The fallback chain ensures support for older browsers while providing optimal experience on modern devices.

## Resources

- [CSS Values and Units Module Level 4](https://www.w3.org/TR/css-values-4/#viewport-relative-lengths)
- [Safe Area Insets](https://webkit.org/blog/7929/designing-websites-for-iphone-x/)
- [Small Viewport Units](https://developer.mozilla.org/en-US/docs/Web/CSS/length#relative_length_units_based_on_viewport)

## Background Logo System

**Location:** `/shared/styles/background-logo.css`

A specialized system for background/hero logos with Stark-tech inspired animations:

### Features
- **Viewport-based sizing**: Uses `vmax`/`svmax` for 85% of larger viewport dimension
- **GPU-accelerated animations**: Only animates transform, opacity, and filter
- **HUD recalibration feel**: Smooth mechanical transitions during orientation changes
- **No snapping**: Eliminates iPad Safari size jumping issues
- **Reusable**: Apply `data-role="background-logo"` to any background logo

### Usage
```jsx
<img 
  src={logo} 
  className={styles.logo}
  data-role="background-logo"
  alt="Background Logo"
/>
```

### Animation States
- **entering**: Fade in with scale-up and blur (HUD powering up)
- **active**: Stable display state
- **exiting**: Fade out with scale-down and blur (HUD powering down)

### Performance
- Uses `will-change` sparingly during transitions only
- Respects `prefers-reduced-motion`
- Ultra-wide and large display optimizations included

---

**Last Updated:** December 31, 2025
**Implemented By:** GitHub Copilot
**Status:** ✅ Complete
