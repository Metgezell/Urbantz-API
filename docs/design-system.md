# Urbantz Design System

## Kleurenpallet

### Primary Colors
```css
:root {
    --primary: #2563eb;           /* Modern Blue - Primary buttons, links */
    --primary-dark: #1d4ed8;      /* Darker blue - Hover states */
    --secondary: #64748b;         /* Slate Gray - Secondary elements */
    --accent: #06b6d4;           /* Cyan - Accent elements, edit buttons */
    --success: #10b981;          /* Emerald - Success states, selected items */
    --warning: #f59e0b;          /* Amber - Warning states */
    --danger: #ef4444;           /* Red - Danger states, delete buttons */
}
```

### Background & Surface Colors
```css
:root {
    --background: #f8fafc;        /* Light Gray - Main background */
    --surface: #ffffff;          /* White - Card backgrounds */
    --surface-secondary: #f1f5f9; /* Light Gray - Secondary surfaces */
}
```

### Text Colors
```css
:root {
    --text-primary: #0f172a;     /* Dark Slate - Primary text */
    --text-secondary: #475569;   /* Slate - Secondary text */
    --text-muted: #94a3b8;       /* Light Slate - Muted text */
}
```

### Border & Shadow Colors
```css
:root {
    --border: #e2e8f0;           /* Light Gray - Default borders */
    --border-light: #f1f5f9;     /* Very Light Gray - Subtle borders */
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
```

### Border Radius
```css
:root {
    --radius: 8px;              /* Standard border radius */
    --radius-lg: 12px;           /* Large border radius for cards */
}
```

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Sizes
- **Header H1**: `2.5rem` (40px)
- **Section Titles**: `1.5rem` (24px)
- **Body Text**: `1rem` (16px)
- **Small Text**: `0.9rem` (14px)
- **Button Text**: `0.9rem` (14px)

### Font Weights
- **Headers**: `700` (Bold)
- **Section Titles**: `600` (Semi-bold)
- **Body Text**: `400` (Regular)
- **Button Text**: `500` (Medium)

## Layout System

### Container
```css
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}
```

### Content Cards
```css
.content-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 2rem;
}
```

### Grid Layouts
```css
/* Import Grid */
.import-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

/* Data Grid */
.data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1.5rem;
}
```

## Component Styles

### Buttons
```css
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--radius);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
}
```

### Cards
```css
.delivery-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    position: relative;
    transition: all 0.3s ease;
}

.delivery-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
```

### Form Elements
```css
.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 0.9rem;
    background: var(--surface);
    font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary);
}
```

## Icon System

### Font Awesome 6.4.0
```html
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
```

### Icon Usage
- **Header**: `fas fa-truck`
- **Upload**: `fas fa-upload`
- **AI Scan**: `fas fa-robot`
- **Random Data**: `fas fa-dice`
- **List**: `fas fa-list`
- **Download**: `fas fa-download`
- **Edit**: `fas fa-edit`
- **Save**: `fas fa-save`
- **Cancel**: `fas fa-times`
- **Select**: `fas fa-check-square`
- **Delete**: `fas fa-trash`

## Animation & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Hover Effects
```css
/* Button hover */
transform: translateY(-1px);

/* Card hover */
transform: translateY(-2px);
box-shadow: var(--shadow-lg);
```

### Loading States
```css
.loading {
    opacity: 0.6;
    pointer-events: none;
}

.spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
```

## Responsive Design

### Breakpoints
```css
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    .import-grid {
        grid-template-columns: 1fr;
    }
    
    .data-grid {
        grid-template-columns: 1fr;
    }
}
```

## Usage Guidelines

### Color Usage
- **Primary Blue**: Main actions, primary buttons
- **Secondary Gray**: Secondary actions, muted elements
- **Accent Cyan**: Edit buttons, special actions
- **Success Green**: Selected states, success messages
- **Warning Amber**: Warning states
- **Danger Red**: Delete actions, errors

### Spacing
- **Small**: `0.5rem` (8px)
- **Medium**: `1rem` (16px)
- **Large**: `1.5rem` (24px)
- **Extra Large**: `2rem` (32px)

### Shadows
- **Default**: `var(--shadow)` - Subtle elevation
- **Large**: `var(--shadow-lg)` - Card hover states

Dit design system zorgt voor een consistente, moderne en professionele uitstraling voor alle Urbantz applicaties.
