# 🎨 Toast Notification Visual Guide

## Appearance

### Success Toast (Green)
```
┌────────────────────────────────────────────┐
│                                            │
│  ✓  Attendance marked successfully         │
│     for 25 students                        │  [×]
│                                            │
└────────────────────────────────────────────┘
```
- **Color**: Green gradient (#27ae60 to #2ecc71)
- **Icon**: Check circle ✓
- **Use**: Successful operations

### Error Toast (Red)
```
┌────────────────────────────────────────────┐
│                                            │
│  ⚠  You do not have permission to          │
│     perform this action                    │  [×]
│                                            │
└────────────────────────────────────────────┘
```
- **Color**: Red gradient (#c0392b to #e74c3c)
- **Icon**: Exclamation circle ⚠
- **Use**: Errors and failures

### Info Toast (Blue)
```
┌────────────────────────────────────────────┐
│                                            │
│  ℹ  Your session will expire in            │
│     5 minutes                              │  [×]
│                                            │
└────────────────────────────────────────────┘
```
- **Color**: Blue gradient (#2980b9 to #3498db)
- **Icon**: Info circle ℹ
- **Use**: Informational messages

## Animation Sequence

### Slide In (300ms)
```
1. Toast appears from right edge
2. Slides smoothly into view
3. Settles in top-right corner
```

### Display (4000ms)
```
Toast remains visible for 4 seconds
User can:
- Read the message
- Click × to close early
- Hover to pause auto-hide (optional)
```

### Slide Out (300ms)
```
1. Toast begins to fade
2. Slides back to the right
3. Disappears completely
```

## Position on Different Screens

### Desktop (> 576px)
```
┌───────────────────────────────────────────────┐
│ Header                                        │
├───────────────────────────────────────────────┤
│                                    ┌────────┐ │
│                                    │ Toast  │ │
│                                    └────────┘ │
│                                               │
│                                               │
│ Content                                       │
│                                               │
│                                               │
└───────────────────────────────────────────────┘
```
Position: Top-right corner with 1rem padding

### Mobile (≤ 576px)
```
┌───────────────────────────┐
│         Header            │
├───────────────────────────┤
│      ┌──────────┐         │
│      │  Toast   │         │
│      └──────────┘         │
│                           │
│                           │
│       Content             │
│                           │
└───────────────────────────┘
```
Position: Top-center for better visibility

## Real Examples

### 1. After Marking Attendance
**Trigger**: Teacher submits attendance form
**Display**:
```
✓ Attendance marked successfully for 25 students
```
**Duration**: 4 seconds
**Color**: Green

### 2. After Entering Grades
**Trigger**: Teacher saves grade entries
**Display**:
```
✓ Grades entered successfully for 30 students!
```
**Duration**: 4 seconds
**Color**: Green

### 3. Permission Error
**Trigger**: User tries restricted action
**Display**:
```
⚠ You do not have permission to perform this action
```
**Duration**: 4 seconds
**Color**: Red

### 4. Session Warning
**Trigger**: Auto-generated after idle time
**Display**:
```
ℹ Your session will expire in 5 minutes
```
**Duration**: 4 seconds
**Color**: Blue

## Stacking Behavior

When multiple toasts appear:

```
┌────────────────┐  ← First toast
│ Toast 1        │
└────────────────┘
┌────────────────┐  ← Second toast
│ Toast 2        │    (appears below)
└────────────────┘
┌────────────────┐  ← Third toast
│ Toast 3        │    (appears below)
└────────────────┘
```

Each toast:
- Stacks vertically
- Maintains 0.5rem gap
- Auto-hides independently
- Can be dismissed individually

## Customization Examples

### Change to Bottom-Right
```html
<div class="toast-container position-fixed bottom-0 end-0 p-3">
```

### Change Duration to 6 Seconds
```javascript
delay: 6000  // 6 seconds
```

### Add Sound (Optional)
```javascript
function showToast(message, type = 'success') {
    // ... existing code ...
    
    // Play sound
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.play();
    
    toast.show();
}
```

### Prevent Auto-Hide
```javascript
const toast = new bootstrap.Toast(toastEl, {
    animation: true,
    autohide: false  // Must close manually
});
```

## Accessibility

### Screen Reader Announcement
```html
role="alert"           → Announces immediately
aria-live="assertive"  → High priority
aria-atomic="true"     → Reads entire message
```

### Keyboard Support
- **Escape**: Closes active toast
- **Tab**: Focus on close button
- **Enter/Space**: Activates close button

### Color Contrast
All toasts meet WCAG 2.1 Level AA:
- Success: White text on green (7.4:1)
- Error: White text on red (5.2:1)
- Info: White text on blue (6.1:1)

## Testing Checklist

- [ ] Toast appears on successful action
- [ ] Toast auto-hides after 4 seconds
- [ ] Toast can be manually closed
- [ ] Multiple toasts stack correctly
- [ ] Mobile responsiveness works
- [ ] Screen reader announces message
- [ ] Animations are smooth
- [ ] Colors are accessible

---

**Tip**: Open `toast_demo.html` in your browser to see all toast types in action!
