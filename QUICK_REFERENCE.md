# Professional UI Design - Quick Reference Guide

## 🎨 Color Palette Quick Reference

### Primary Colors
```
Primary Blue       #3498db    (RGB: 52, 152, 219)    - Main actions, buttons, links
Success Green      #2ecc71    (RGB: 46, 204, 113)    - Positive states, success
Warning Orange     #f39c12    (RGB: 243, 156, 18)    - Warnings, attention needed
Danger Red         #e74c3c    (RGB: 231, 76, 60)     - Errors, destructive actions
Info Teal          #1abc9c    (RGB: 26, 188, 156)    - Information, secondary CTAs
```

### Text & Background Colors
```
Dark Gray          #2c3e50    (RGB: 44, 62, 80)      - Headings, body text
Muted Gray         #7f8c8d    (RGB: 127, 140, 141)   - Secondary text, labels
Light Gray         #ecf0f1    (RGB: 236, 240, 241)   - Backgrounds
Very Light Gray    #f8f9fa    (RGB: 248, 249, 250)   - Alternative backgrounds
```

---

## 🧩 Component Quick Reference

### 1️⃣ Stat Card (Compact)
```html
<div class="col-6 col-md-3">
    <div class="card stat-card border-left-primary h-100" style="border-left: 4px solid #3498db;">
        <div class="card-body py-3">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <p class="stat-card-label">Metric Label</p>
                    <h4 class="stat-card-value">999</h4>
                </div>
                <div class="stat-icon bg-primary text-white">
                    <i class="bi bi-icon-name"></i>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Color Variants**:
- Blue: `style="border-left: 4px solid #3498db;"` + `bg-primary`
- Green: `style="border-left: 4px solid #2ecc71;"` + `bg-success`
- Orange: `style="border-left: 4px solid #f39c12;"` + `bg-warning`
- Red: `style="border-left: 4px solid #e74c3c;"` + `bg-danger`
- Teal: `style="border-left: 4px solid #1abc9c;"` + `bg-info`

---

### 2️⃣ Card with Colored Header
```html
<div class="card border-0 shadow-sm">
    <div class="card-header bg-primary text-white py-3">
        <h6 class="mb-0" style="font-weight: 600;">
            <i class="bi bi-icon-name me-2"></i>Card Title
        </h6>
    </div>
    <div class="card-body p-4">
        <!-- Content here -->
    </div>
</div>
```

**Header Color Options**:
- Blue: `bg-primary`
- Green: `bg-success`
- Red: `bg-danger`
- Info: `bg-info`
- Light: `bg-light`

---

### 3️⃣ Page Header
```html
<div class="page-header mb-4">
    <h1><i class="bi bi-icon-name me-2"></i>Page Title</h1>
    <p class="page-subtitle">Page description or tagline</p>
</div>
```

---

### 4️⃣ Professional Table
```html
<table class="table table-hover mb-0">
    <thead class="table-light">
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
            <th>Column 3</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
            <td>Data 3</td>
        </tr>
    </tbody>
</table>
```

---

### 5️⃣ Alert with Icon
```html
<div class="alert alert-info border-0 border-left-info" style="border-left: 4px solid #1abc9c;">
    <i class="bi bi-info-circle me-2"></i>
    <strong>Alert Title</strong>
    <p>Alert description text</p>
</div>
```

**Alert Types**:
- Info: `alert-info` + `style="border-left: 4px solid #1abc9c;"`
- Success: `alert-success` + `style="border-left: 4px solid #2ecc71;"`
- Warning: `alert-warning` + `style="border-left: 4px solid #f39c12;"`
- Danger: `alert-danger` + `style="border-left: 4px solid #e74c3c;"`

---

### 6️⃣ Responsive Grid
```html
<div class="row g-3">
    <!-- 4 columns on desktop, 2 on tablet, 1 on mobile -->
    <div class="col-6 col-md-3">Item 1</div>
    <div class="col-6 col-md-3">Item 2</div>
    <div class="col-6 col-md-3">Item 3</div>
    <div class="col-6 col-md-3">Item 4</div>
</div>
```

---

### 7️⃣ Form Layout
```html
<div class="mb-3">
    <label class="form-label">Field Label</label>
    <input type="text" class="form-control" placeholder="Placeholder text">
</div>
```

---

### 8️⃣ Button Styles
```html
<!-- Primary -->
<button class="btn btn-primary"><i class="bi bi-icon me-1"></i>Primary</button>

<!-- Success -->
<button class="btn btn-success"><i class="bi bi-icon me-1"></i>Success</button>

<!-- Danger -->
<button class="btn btn-danger"><i class="bi bi-icon me-1"></i>Danger</button>

<!-- Outline -->
<button class="btn btn-outline-primary"><i class="bi bi-icon me-1"></i>Outline</button>
```

---

## 📐 Spacing Standards

### Container Padding
```html
<div class="container-fluid px-3 px-md-4 py-4">
    <!-- Mobile: 12px left/right, 16px top/bottom -->
    <!-- Desktop: 16px left/right, 16px top/bottom -->
</div>
```

### Card Body Padding
- Small: `p-3` (12px)
- Large: `p-4` (16px)

### Gap Between Cards
- Comfortable: `g-3` (12px)
- Spacious: `g-4` (16px)

### Section Margins
- Large gap: `mb-4` (16px)
- Medium gap: `mb-3` (12px)

---

## 📱 Responsive Breakpoints

### Stat Cards (4 cards row)
```html
<div class="col-6 col-md-3">
    <!-- Displays: 2 per row on mobile, 4 per row on desktop -->
</div>
```

### Content Cards (2 cards row)
```html
<div class="col-12 col-md-6 col-lg-6">
    <!-- Displays: 1 per row on mobile, 2 per row on tablet/desktop -->
</div>
```

### Child Cards (3 cards row)
```html
<div class="col-12 col-md-6 col-lg-4">
    <!-- Displays: 1 per row on mobile, 2 on tablet, 3 on desktop -->
</div>
```

---

## 🎯 Icon Usage

### Common Icons (Bootstrap Icons)
```
Navigation:
  bi bi-arrow-right       → Go/Next
  bi bi-arrow-left        → Back/Previous
  bi bi-arrow-repeat      → Refresh/Reload
  
Students:
  bi bi-people-fill       → Group/Students
  bi bi-person-check-fill → Attendance
  bi bi-person-circle     → User/Profile
  
Academic:
  bi bi-book-fill         → Classes/Books
  bi bi-mortarboard-fill  → Education
  bi bi-pencil-square     → Grades/Edit
  bi bi-file-earmark-pdf  → Documents
  
Actions:
  bi bi-check-circle      → Confirm/Submit
  bi bi-x-circle          → Cancel/Delete
  bi bi-eye               → View/Details
  bi bi-download          → Export
  bi bi-upload            → Import
  
Status:
  bi bi-check-circle-fill → Success/Present
  bi bi-x-circle-fill     → Error/Absent
  bi bi-info-circle       → Information
  bi bi-exclamation-triangle → Warning
```

**Icon Size**: `font-size: 1.5rem;` for header icons

---

## 🎨 Styling Quick Snippets

### Rounded Corners (everywhere)
```css
border-radius: 6px  /* Forms, buttons */
border-radius: 8px  /* Cards, containers */
```

### Shadows
```css
box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);    /* Subtle */
box-shadow: 0 5px 15px rgba(0, 0, 0, 0.12);   /* Medium */
box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);  /* Large */
```

### Hover Effects
```css
transform: translateY(-2px);  /* Lift on hover */
transition: all 0.2s ease;    /* Smooth animation */
```

### Text Weights
```
400 - Regular body text
500 - Secondary/medium text
600 - Labels, secondary headings
700 - Primary headings, strong text
```

---

## 🔧 Common Patterns

### Page Structure
```html
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid px-3 px-md-4 py-4">
    <!-- 1. Page Header -->
    <div class="page-header mb-4">
        <h1><i class="bi bi-icon me-2"></i>Title</h1>
        <p class="page-subtitle">Subtitle</p>
    </div>

    <!-- 2. Stats (if applicable) -->
    <div class="row g-3 mb-4">
        <!-- Stat cards here -->
    </div>

    <!-- 3. Main Content -->
    <div class="card border-0 shadow-sm">
        <!-- Content here -->
    </div>
</div>
{% endblock %}
```

---

## ✨ Pro Tips

1. **Always use `border-0 shadow-sm`** on cards for consistency
2. **Include icon in headers** for visual interest
3. **Use left-bordered stat cards** for brand consistency
4. **Test on mobile** - use Chrome DevTools
5. **Maintain color palette** - don't add new colors
6. **Use responsive classes** - don't hardcode widths
7. **Include loading states** - show spinners during data fetching
8. **Handle empty states** - show helpful messages with icons
9. **Add proper spacing** - use consistent gap/padding
10. **Always use professional CSS** - include the professional-ui.css

---

## 📝 Copy-Paste Snippets

### Skeleton Loading (5 rows)
```html
<div id="skeletonLoader" style="display: none;">
    <table class="table">
        <tbody>
            {% for i in "12345" %}
            <tr>
                <td><div class="skeleton skeleton-text" style="width: 30px;"></div></td>
                <td><div class="skeleton skeleton-avatar"></div></td>
                <td><div class="skeleton skeleton-text" style="width: 150px;"></div></td>
                <td><div class="skeleton skeleton-text" style="width: 100px;"></div></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### Empty State
```html
<tr>
    <td colspan="8" class="text-center text-muted py-4">
        <i class="bi bi-inbox" style="font-size: 2.5rem; opacity: 0.5;"></i>
        <p class="mt-2" style="font-weight: 500;">No items found</p>
    </td>
</tr>
```

### Live Clock
```html
<div id="clock" style="font-size: 1.1rem; color: #7f8c8d; font-weight: 600;"></div>

<script>
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
}
updateClock();
setInterval(updateClock, 1000);
</script>
```

---

## 🎓 Learning Path

1. **Start**: Review color palette
2. **Explore**: Look at professional-ui.css
3. **Study**: Review DESIGN_SYSTEM.md
4. **Practice**: Update a new page using patterns
5. **Master**: Create custom components following system
6. **Maintain**: Keep consistency across all pages

---

**Quick Reference v1.0** | School Management System Professional UI
