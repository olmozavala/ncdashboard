# NCDashboard Web Application

A modern, responsive web application built with React, TypeScript, and Redux for state management. This application serves as the frontend interface for the NCDashboard system.

## 🚀 Tech Stack

- **Frontend Framework**: React 18
- **Language**: TypeScript
- **State Management**: Redux Toolkit
- **Routing**: React Router v7
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Maps Integration**: OpenLayers
- **UI Components**: React Resizable Panels, XYFlow React
- **HTTP Client**: Axios

## 📁 Project Structure

```
src/
├── components/     # Reusable UI components
├── screens/        # Page-level components
├── navigation/     # Routing configuration
├── redux/         # State management
│   ├── store.ts
│   ├── slices/    # Redux slices for different features
├── models/        # TypeScript interfaces and types
├── App.tsx        # Root application component
└── index.tsx      # Application entry point
```

## 🛠️ Development Setup

1. **Prerequisites**
   - Node.js (LTS version)
   - Yarn package manager

2. **Installation**
   ```bash
   yarn install
   ```

3. **Development Server**
   ```bash
   yarn start
   ```

4. **Build for Production**
   ```bash
   yarn build
   ```

5. **Linting**
   ```bash
   yarn lint
   ```

## 🏗️ Architecture & Best Practices

### State Management
- Uses Redux Toolkit for predictable state management
- Organized into feature-based slices
- Implements TypeScript for type safety
- Follows the Redux best practices for actions and reducers

### Component Structure
- Follows atomic design principles
- Components are organized by feature and reusability
- Implements proper TypeScript interfaces for props
- Uses functional components with hooks

### Code Quality
- ESLint configuration for code quality
- TypeScript for type safety
- Consistent code formatting
- Comprehensive documentation

### Performance
- Code splitting with React Router
- Optimized builds with Vite
- Efficient state updates with Redux
- Responsive design with Tailwind CSS

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request**

### Code Style Guidelines
- Follow TypeScript best practices
- Use functional components with hooks
- Implement proper error handling
- Write meaningful commit messages
- Include JSDoc comments for complex functions
- Keep components small and focused

### Testing
- Write unit tests for critical components
- Test Redux actions and reducers
- Ensure proper error handling
- Test edge cases

## 📝 Documentation

- Components should include JSDoc comments
- Complex functions should be documented
- Update README when adding new features
- Keep documentation up-to-date with code changes

## 🔒 Security

- Follow React security best practices
- Implement proper authentication
- Sanitize user inputs
- Use environment variables for sensitive data

## 📦 Dependencies

Key dependencies are managed in `package.json`. Use `yarn` for package management to ensure consistent installations.

## 🚨 Troubleshooting

Common issues and solutions:
1. **Build failures**: Clear node_modules and reinstall dependencies
2. **Type errors**: Ensure TypeScript types are properly defined
3. **State management issues**: Check Redux DevTools for state updates


For more detailed information about specific features or components, please refer to the respective documentation in the codebase.
