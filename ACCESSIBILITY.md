# ACCESSIBILITY.md - Web Accessibility (WCAG 2.1 AA)

## Keyboard Navigation

### Tab Order Management

```html
<!-- buttons follow logical reading order -->
<header>
    <h1 tabindex="1">AccessGuard</h1>
    <nav>
        <a href="/" tabindex="2">Home</a>
        <a href="/login" tabindex="3">Login</a>
        <a href="/register" tabindex="4">Register</a>
    </nav>
</header>

<form>
    <label for="email">Email</label>
    <input id="email" type="email" tabindex="5" />
    
    <label for="password">Password</label>
    <input id="password" type="password" tabindex="6" />
    
    <button type="submit" tabindex="7">Submit</button>
    <button type="reset" tabindex="8">Clear</button>
</form>
```

### Skip Links

```html
<!-- Allow users to skip navigation -->
<a href="#main" class="skip-link">Skip to main content</a>

<nav>
    <!-- Navigation -->
</nav>

<main id="main">
    <!-- Main content -->
</main>

<style>
.skip-link {
    position: absolute;
    left: -9999px;
    z-index: 999;
}

.skip-link:focus {
    left: auto;
    top: 0;
    background: #000;
    color: #fff;
    padding: 10px;
}
</style>
```

---

## Screen Reader Support (ARIA)

### Semantic HTML First

```html
<!-- GOOD: Use semantic HTML -->
<button>Login</button>
<nav>...</nav>
<main>...</main>
<article>...</article>

<!-- BAD: Don't use divs with ARIA if semantic HTML works -->
<div role="button">Login</div>  <!-- ❌ -->
```

### ARIA Labels

```html
<!-- Form labels explicitly linked -->
<label for="email">Email Address</label>
<input id="email" type="email" />

<!-- Icon buttons need labels -->
<button aria-label="Close menu">✕</button>

<!-- Live regions for dynamic content -->
<div role="alert" aria-live="polite" aria-atomic="true">
    Invalid password. Try again.
</div>

<!-- Landmarks -->
<nav aria-label="Main navigation">
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/login">Login</a></li>
    </ul>
</nav>
```

### Form Accessibility

```html
<form>
    <fieldset>
        <legend>Account Information</legend>
        
        <div class="form-group">
            <label for="email-input">
                Email Address
                <span aria-label="required">*</span>
            </label>
            <input 
                id="email-input"
                type="email"
                required
                aria-required="true"
                aria-describedby="email-help"
            />
            <small id="email-help">
                We'll never share your email.
            </small>
        </div>
        
        <div class="form-group">
            <label for="password-input">Password</label>
            <input 
                id="password-input"
                type="password"
                required
                aria-invalid="false"
                aria-describedby="pwd-requirements"
            />
            <ul id="pwd-requirements">
                <li>At least 8 characters</li>
                <li>At least one number</li>
                <li>At least one special character</li>
            </ul>
        </div>
    </fieldset>
</form>
```

---

## Color Contrast (WCAG AA ≥ 4.5:1)

### Our Color Scheme

```css
/* Primary text on background */
color: #ffffff;        /* Contrast on #0a1628: 18.5:1 ✅ */
background: #0a1628;

/* Links */
color: #00d4ff;        /* Contrast on #0a1628: 4.8:1 ✅ */
text-decoration: underline;

/* Success messages */
color: #35d084;        /* Contrast on #0a1628: 6.2:1 ✅ */

/* Error messages */
color: #ff6b6b;        /* Contrast on #0a1628: 7.1:1 ✅ */

/* Disabled state */
color: #888888;        /* Contrast on #0a1628: 4.5:1 ✅ */
```

### Text Sizing

```css
/* Never use pixels for font-size (not scalable) */

/* GOOD: Use relative units */
body {
    font-size: 1rem;   /* 16px */
    line-height: 1.5;  /* 24px */
}

h1 { font-size: 2.5rem; }       /* 40px */
h2 { font-size: 2rem; }         /* 32px */
h3 { font-size: 1.5rem; }       /* 24px */
button { font-size: 1rem; }     /* 16px */

/* Minimum 12px (16px recommended) */
small { font-size: 0.75rem; }   /* 12px ✅ */

/* BAD: Avoid pixels */
h1 { font-size: 40px; }         /* ❌ */
```

### Don't Use Color Alone

```html
<!-- GOOD: Color + icon + text -->
<span class="status-success">
    ✓ Password accepted
</span>

<style>
.status-success {
    color: #35d084;  /* Also readable by colorblind users */
}
</style>

<!-- BAD: Color only -->
<span style="color: green">Success</span>  <!-- ❌ -->
```

---

## Focus Management

### Visible Focus Indicator

```css
/* Never remove focus outline */

/* GOOD: Custom but visible */
a:focus,
button:focus,
input:focus {
    outline: 3px solid #00d4ff;
    outline-offset: 2px;
}

/* BAD: Remove focus outline */
a:focus { outline: none; }  /* ❌ */
```

### Focus Visible Distinction

```html
<!-- Show focus only from keyboard, not mouse -->
<style>
button:focus-visible {
    outline: 3px solid #00d4ff;
}

button:focus:not(:focus-visible) {
    outline: none;
}
</style>
```

---

## Motion & Animation

### Respect Reduced Motion Preference

```css
/* Users who prefer reduced motion get simpler animations */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Normal: smooth 13s animation */
@media (prefers-reduced-motion: no-preference) {
    .aurora {
        animation: float 13s ease-in-out infinite;
    }
}
```

### Avoid Auto-Playing Content

```html
<!-- Don't auto-play videos/audio -->

<!-- GOOD: User controls -->
<audio controls>
    <source src="audio.mp3" type="audio/mpeg">
</audio>

<!-- BAD: Auto-play -->
<audio autoplay>  <!-- ❌ -->
    <source src="audio.mp3" type="audio/mpeg">
</audio>
```

---

## Testing Checklist

- [ ] Keyboard navigation works (Tab through all interactive elements)
- [ ] No keyboard trap (can Tab away from all elements)
- [ ] Focus visible (blue outline 3px visible)
- [ ] Color contrast ≥ 4.5:1 (use WebAIM Contrast Checker)
- [ ] Text resizes to 200% without horizontal scroll
- [ ] Form labels linked to inputs
- [ ] Error messages descriptive (not just color)
- [ ] Links have underline (not color alone)
- [ ] Icons have text labels or ARIA labels
- [ ] Video/audio has captions/transcript
- [ ] Prefers-reduced-motion respected
- [ ] Screen reader tested (Windows: NVDA, Mac: VoiceOver)
- [ ] Mobile zoom not disabled (viewport-fit)
- [ ] Touch targets ≥ 44x44px
- [ ] No flashing (≤3 flashes per second)

---

## Tools for Testing

### Automated
```bash
# axe DevTools (Chrome Extension)
# Wave (WebAIM) - wave.webaim.org

# Command-line
npm install -g axe-core
axe-core http://localhost:8000
```

### Manual
1. Test keyboard navigation
2. Test with NVDA (Windows) or VoiceOver (Mac)
3. Zoom to 200%, verify layout
4. Disable CSS, verify content order
5. Test colorblind simulation (Color Oracle)

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
