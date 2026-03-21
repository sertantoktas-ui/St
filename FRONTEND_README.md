# Enterprise Service Management System - Frontend

Profesyonel React.js web uygulaması. Admin panel, müşteri portalı ve raporlama sistemi.

## 🎨 Teknoloji Stack

- **React 18** - UI Framework
- **Material-UI (MUI)** - Component Library
- **React Router v6** - Client-side Routing
- **Zustand** - State Management
- **React Query** - Server State Management
- **Google Maps API** - Maps & Geolocation
- **Recharts** - Data Visualization
- **Tailwind CSS** - Styling
- **Axios** - HTTP Client
- **React Hook Form** - Form Management

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── customers/
│   │   │   ├── CustomerList.jsx
│   │   │   ├── CustomerForm.jsx
│   │   │   ├── CustomerDetail.jsx
│   │   │   └── CustomerMap.jsx
│   │   ├── requests/
│   │   │   ├── RequestList.jsx
│   │   │   ├── RequestForm.jsx
│   │   │   ├── RequestDetail.jsx
│   │   │   ├── RequestMap.jsx
│   │   │   └── RequestTimeline.jsx
│   │   ├── technicians/
│   │   │   ├── TechnicianList.jsx
│   │   │   ├── TechnicianForm.jsx
│   │   │   ├── TechnicianDetail.jsx
│   │   │   ├── TechnicianMap.jsx
│   │   │   ├── TechnicianSchedule.jsx
│   │   │   └── PerformanceChart.jsx
│   │   ├── invoicing/
│   │   │   ├── InvoiceList.jsx
│   │   │   ├── InvoiceForm.jsx
│   │   │   ├── InvoiceDetail.jsx
│   │   │   ├── PaymentForm.jsx
│   │   │   └── AgingReport.jsx
│   │   ├── inventory/
│   │   │   ├── PartsList.jsx
│   │   │   ├── PartForm.jsx
│   │   │   ├── InventoryStatus.jsx
│   │   │   └── LowStockAlert.jsx
│   │   └── analytics/
│   │       ├── Dashboard.jsx
│   │       ├── KPICards.jsx
│   │       ├── PerformanceCharts.jsx
│   │       ├── RevenueAnalysis.jsx
│   │       ├── TechnicianMetrics.jsx
│   │       └── SLACompliance.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── CustomersPage.jsx
│   │   ├── TechniciansPage.jsx
│   │   ├── RequestsPage.jsx
│   │   ├── InvoicingPage.jsx
│   │   ├── InventoryPage.jsx
│   │   ├── AnalyticsPage.jsx
│   │   ├── SettingsPage.jsx
│   │   └── NotFoundPage.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useApi.js
│   │   ├── useLocation.js
│   │   └── useLocalStorage.js
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── customerService.js
│   │   ├── technicianService.js
│   │   ├── requestService.js
│   │   ├── invoiceService.js
│   │   ├── inventoryService.js
│   │   └── analyticsService.js
│   ├── store/
│   │   ├── authStore.js
│   │   ├── customerStore.js
│   │   ├── technicianStore.js
│   │   ├── requestStore.js
│   │   └── uiStore.js
│   ├── utils/
│   │   ├── formatters.js
│   │   ├── validators.js
│   │   ├── constants.js
│   │   └── helpers.js
│   ├── styles/
│   │   ├── index.css
│   │   ├── tailwind.css
│   │   └── theme.js
│   ├── App.jsx
│   ├── index.jsx
│   └── config.js
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── package.json
└── tailwind.config.js
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 14+
- npm or yarn
- Backend API running on http://localhost:5000

### Installation Steps

1. **Create React App**
```bash
npx create-react-app service-management-frontend
cd service-management-frontend
```

2. **Install Dependencies**
```bash
npm install
# Copy dependencies from frontend_package.json
```

3. **Configure Environment**
```bash
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
echo "REACT_APP_GOOGLE_MAPS_KEY=your-google-maps-api-key" >> .env
```

4. **Run Development Server**
```bash
npm start
```

Application will open at `http://localhost:3000`

5. **Build for Production**
```bash
npm run build
```

---

## 🎯 Key Features

### 📊 Admin Dashboard
- Real-time KPI metrics
- Service request overview
- Revenue tracking
- Technician utilization
- Upcoming appointments
- Alerts and notifications

### 👥 Customer Management
- Customer directory
- Contact information
- Service history
- Location mapping
- Contract management
- Communication log

### 👨‍🔧 Technician Management
- Technician directory
- Skills and certifications
- Availability scheduling
- Performance metrics
- Real-time location tracking
- Workload assignment

### 📋 Service Request Management
- Create and manage work orders
- Priority and status tracking
- Assignment to technicians
- GPS location mapping
- Photo and signature capture
- Customer rating system
- SLA monitoring

### 💰 Invoicing & Billing
- Automated invoice generation
- Payment tracking
- Aging analysis
- Receipt generation
- Multi-currency support (future)

### 📦 Inventory Management
- Parts and components catalog
- Stock level tracking
- Low stock alerts
- Supplier management
- Usage history

### 📈 Analytics & Reporting
- Dashboard with key metrics
- Revenue analysis
- Technician performance
- Customer satisfaction
- SLA compliance
- Monthly and yearly reports
- Export to PDF/Excel

### 🗺️ Maps & Geolocation
- Real-time technician tracking
- Service location mapping
- Route optimization
- Service area visualization
- Distance calculation

---

## 🔐 Authentication

### Login Flow
```
1. User enters credentials
2. API validates and returns JWT token
3. Token stored in localStorage
4. Token added to all API requests
5. Token refreshed on expiry
```

### Protected Routes
All routes except login are protected with role-based access:
- **Admin** - Full system access
- **Manager** - Management and reporting access
- **Technician** - Field service access
- **Customer** - Portal access only

---

## 📡 API Integration

### Example API Call
```javascript
import { useQuery } from 'react-query';
import axios from 'axios';

const useCustomers = () => {
  return useQuery('customers', async () => {
    const { data } = await axios.get('/api/customers', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return data;
  });
};
```

### Error Handling
- Global error boundary
- Toast notifications
- Graceful fallbacks
- Retry logic for failed requests

---

## 🎨 UI/UX Features

### Responsive Design
- Mobile-first approach
- Works on all screen sizes
- Touch-friendly interface
- Adaptive layouts

### Dark Mode
- System preference detection
- Toggle button
- Persistent preference

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode

### Performance
- Code splitting
- Lazy loading
- Image optimization
- Caching strategies

---

## 📱 Mobile App (React Native)

For mobile app development, create a separate React Native project:

```bash
npx react-native init ServiceManagementApp
```

Share code with web app using:
- Shared business logic
- Common API services
- Shared utilities

---

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
# Using Cypress
npx cypress open
```

### Coverage Report
```bash
npm test -- --coverage
```

---

## 📦 Deployment

### Build Optimized Version
```bash
npm run build
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
```bash
npm run build
# Upload 'build' folder to Netlify
```

### Docker Deployment
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build"]
```

---

## 🔄 Development Workflow

### Component Development
1. Create component file
2. Add PropTypes or TypeScript types
3. Write component logic
4. Add styling with Tailwind/MUI
5. Create stories with Storybook (optional)
6. Add tests

### State Management
- Use Zustand for global state
- Use React Query for server state
- Use local state for UI state

### Code Style
- ESLint rules enforced
- Prettier formatting
- File naming conventions
- Import organization

---

## 🚨 Common Issues

### CORS Errors
- Ensure backend API has CORS enabled
- Check API_URL in .env
- Verify proxy setting in package.json

### Authentication Issues
- Clear localStorage cache
- Check token expiration
- Verify JWT_SECRET in backend

### Map Not Loading
- Verify Google Maps API key
- Check billing enabled
- Verify domain whitelist

---

## 📚 Resources

- [React Documentation](https://react.dev)
- [Material-UI Documentation](https://mui.com)
- [React Query Docs](https://tanstack.com/query)
- [Google Maps API](https://developers.google.com/maps)

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -m "Add new feature"`
3. Push to branch: `git push origin feature/new-feature`
4. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

**Version:** 1.0.0
**Last Updated:** March 2026
**Developed by:** Claude AI
