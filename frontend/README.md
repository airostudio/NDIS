# Velma Frontend

Modern, clinical-styled HTML5 frontend for the Velma NDIS AI Assistant.

## Features

### Clinical Design System
- Clean, professional healthcare/clinical aesthetic
- WCAG 2.1 AA accessibility compliant
- Fully responsive (mobile-first design)
- Modern CSS with CSS Variables (Custom Properties)
- No external CSS frameworks - custom lightweight design system

### Latest UX Technologies
- **CSS Grid & Flexbox** for modern layouts
- **CSS Custom Properties** for theming and consistency
- **CSS Transitions & Animations** for smooth interactions
- **Intersection Observer API** for performance
- **Fetch API** for modern AJAX requests
- **ES6+ JavaScript** with classes and modules
- **Session Storage** for client-side state

### Components

#### Core Components
- **Navigation Sidebar** - Collapsible, responsive navigation
- **Top Bar** - Search, notifications, user profile
- **Dashboard Cards** - Statistics and metrics display
- **Chat Interface** - Real-time AI conversation UI
- **Forms** - Accessible, validated form controls
- **Tables** - Sortable, responsive data tables
- **Modals** - Accessible dialog system
- **Toast Notifications** - Non-intrusive alerts
- **Badges** - Status indicators
- **Buttons** - Multiple variants and sizes

#### Specialized Components
- **Stat Cards** - Animated dashboard statistics
- **Activity Feed** - Timeline of recent events
- **Suggested Prompts** - Quick action buttons
- **Typing Indicator** - Chat loading state
- **Message Bubbles** - Chat message display

### Accessibility Features
- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast ratios
- Reduced motion support

### Performance
- Minimal dependencies (no jQuery, no Bootstrap)
- Optimized CSS (~50KB minified)
- Lazy loading where appropriate
- Debounced events
- Efficient DOM manipulation

## File Structure

```
frontend/
├── css/
│   ├── velma-core.css          # Design system and base styles
│   └── velma-components.css    # Component-specific styles
├── js/
│   ├── velma-core.js           # Core utilities and API client
│   ├── chat.js                 # Chat interface logic
│   └── dashboard.js            # Dashboard functionality
├── index.html                  # Main dashboard
├── chat.html                   # AI chat interface
└── README.md                   # This file
```

## Getting Started

### 1. Run the Backend API

First, start the Velma API server:

```bash
cd /path/to/NDIS
python scripts/run_api.py
```

The API will run on http://localhost:8000

### 2. Serve the Frontend

#### Option A: Python HTTP Server
```bash
cd frontend
python -m http.server 8080
```

Then open http://localhost:8080

#### Option B: Node.js HTTP Server
```bash
cd frontend
npx http-server -p 8080
```

#### Option C: Production (Nginx/Apache)
Configure your web server to serve the `frontend/` directory and proxy `/api` to the backend.

## Usage

### Dashboard
Navigate to `index.html` to see:
- Overview statistics
- Recent activity
- Upcoming tasks
- Compliance alerts

### Chat Interface
Navigate to `chat.html` to:
- Ask Velma questions about NDIS operations
- Get payroll calculations
- Check compliance status
- Schedule appointments
- Manage tasks

### Suggested Prompts
Click any suggested prompt button to quickly ask common questions:
- SCHADS Award rates
- Compliance requirements
- Pay calculations
- Employee onboarding
- Leave loading
- Credential expiry checks

## API Integration

The frontend connects to the Velma API at:
- **Development**: `http://localhost:8000`
- **Production**: Configured in `js/velma-core.js`

### API Endpoints Used
- `GET /health` - Health check
- `GET /api/config` - Configuration
- `POST /api/chat` - Send chat messages

## Customization

### Colors
Edit CSS variables in `css/velma-core.css`:

```css
:root {
  --color-primary: #0066CC;
  --color-secondary: #00A896;
  /* ... */
}
```

### Typography
Change fonts in the `<head>` of HTML files:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Logo
Replace the "V" logo in the sidebar with your own:

```html
<div class="sidebar-logo-icon">
  <img src="path/to/logo.png" alt="Logo">
</div>
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android 90+)

## Accessibility

The frontend meets WCAG 2.1 Level AA standards:
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Color contrast ratios
- ✅ Focus indicators
- ✅ ARIA labels
- ✅ Semantic HTML
- ✅ Reduced motion support

## Development

### Adding New Pages

1. Copy `index.html` as a template
2. Update the `<title>` and page content
3. Include required CSS/JS files
4. Add navigation link in sidebar
5. Create page-specific JS if needed

### Adding Components

1. Add CSS to `css/velma-components.css`
2. Follow naming convention: `.component-name`
3. Use CSS variables for colors and spacing
4. Ensure responsive behavior
5. Add accessibility attributes

### Testing

Test on:
- Different screen sizes (mobile, tablet, desktop)
- Different browsers
- Keyboard-only navigation
- Screen readers (NVDA, JAWS, VoiceOver)
- Slow network conditions

## Production Deployment

### 1. Build (Optional Optimization)
While the frontend works as-is, you can minify for production:

```bash
# Minify CSS
npx clean-css-cli -o dist/css/styles.min.css css/*.css

# Minify JS
npx uglify-js js/*.js -o dist/js/scripts.min.js
```

### 2. Configure Web Server

#### Nginx Example
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/NDIS/frontend;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable HTTPS
Use Let's Encrypt for free SSL:

```bash
certbot --nginx -d your-domain.com
```

## Performance Tips

1. **Enable Gzip/Brotli** compression on your web server
2. **Cache static assets** (CSS, JS, images)
3. **Use CDN** for production deployments
4. **Lazy load images** if adding more visuals
5. **Monitor bundle size** - keep JS/CSS minimal

## Troubleshooting

### API Connection Issues
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_BASE_URL in `js/velma-core.js`

### Styles Not Loading
- Check file paths in HTML `<link>` tags
- Ensure CSS files are in `css/` directory
- Clear browser cache

### JavaScript Errors
- Check browser console (F12)
- Ensure all JS files are loaded
- Verify script order in HTML

## Contributing

When adding features:
1. Follow existing code style
2. Use semantic HTML
3. Maintain accessibility
4. Test on multiple browsers
5. Update this README

## License

Part of the Velma NDIS AI Assistant project.

## Support

For issues or questions about the frontend, please refer to the main project documentation or contact the development team.
