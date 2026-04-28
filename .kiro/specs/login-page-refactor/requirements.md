# Requirements Document: Login Page Refactor

## Introduction

This document specifies the requirements for refactoring the login page to align with the project's architecture standards. The current implementation uses manual form validation and native HTML elements, while the architecture mandates React Hook Form + Zod for validation and Shadcn/ui components for UI elements. Additionally, Next.js 16 + React 19 introduces potential issues with native form submission that must be addressed.

## Glossary

- **Login_Page**: The authentication page located at `/login` that handles user credential submission
- **Form_Validator**: The Zod schema and React Hook Form integration responsible for validating user input
- **Auth_Service**: The authentication service layer (`lib/api/auth.ts`) that communicates with the backend login endpoint
- **Auth_Context**: The React Context (`lib/auth/context.tsx`) managing global authentication state
- **Shadcn_UI_Components**: The project's UI component library based on Radix UI and Tailwind CSS
- **OAuth2PasswordRequestForm**: The backend's expected request format with `username` (email) and `password` fields
- **Role_Based_Redirect**: The navigation logic that directs users to different pages based on their assigned roles

## Requirements

### Requirement 1: Form Validation with Zod Schema

**User Story:** As a developer, I want form validation implemented using Zod schema, so that validation logic is declarative, type-safe, and reusable.

#### Acceptance Criteria

1. THE Form_Validator SHALL define a Zod schema for login form with email and password fields
2. WHEN a user submits an empty email field, THE Form_Validator SHALL display the error message "请输入邮箱"
3. WHEN a user submits an invalid email format, THE Form_Validator SHALL display the error message "请输入有效的邮箱地址"
4. WHEN a user submits an empty password field, THE Form_Validator SHALL display the error message "请输入密码"
5. WHEN a user submits a password with fewer than 6 characters, THE Form_Validator SHALL display the error message "密码至少为 6 位"
6. THE Form_Validator SHALL integrate with React Hook Form using `@hookform/resolvers/zod`

### Requirement 2: Shadcn/ui Component Integration

**User Story:** As a developer, I want the login form to use Shadcn/ui components, so that the UI is consistent with the rest of the application.

#### Acceptance Criteria

1. THE Login_Page SHALL use the `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, and `CardFooter` components for layout
2. THE Login_Page SHALL use the `Input` component from `@/components/ui/input` for email and password fields
3. THE Login_Page SHALL use the `Label` component from `@/components/ui/label` for field labels
4. THE Login_Page SHALL use the `Button` component from `@/components/ui/button` for the submit action
5. WHEN the form is in a loading state, THE Button SHALL display loading text and be disabled

### Requirement 3: React Hook Form Integration

**User Story:** As a developer, I want the login form managed by React Hook Form, so that form state, validation, and submission are handled consistently.

#### Acceptance Criteria

1. THE Login_Page SHALL use `useForm` hook from `react-hook-form` to manage form state
2. THE Form_Validator SHALL register input fields using the `register` function or `Form` component patterns
3. WHEN validation errors occur, THE Form_Validator SHALL display error messages below corresponding input fields
4. WHEN a user types in an input field, THE Form_Validator SHALL clear the error message for that field
5. THE Form_Validator SHALL track the form submission state (idle, submitting, success, error)

### Requirement 4: Native Form Submission Prevention

**User Story:** As a developer, I want to prevent native form submission behavior, so that the login flow works correctly in Next.js 16 + React 19.

#### Acceptance Criteria

1. WHEN the login button is clicked, THE Login_Page SHALL execute the React submit handler instead of native form submission
2. THE Login_Page SHALL NOT trigger a GET request with credentials in the URL query parameters
3. IF a `<form>` element is used, THE Login_Page SHALL call `e.preventDefault()` in the submit handler
4. WHERE the Button component is used for submission, THE Button SHALL have `type="button"` with an `onClick` handler to avoid form association

### Requirement 5: Authentication Flow

**User Story:** As a user, I want to log in with my credentials, so that I can access the application based on my role.

#### Acceptance Criteria

1. WHEN a user submits valid credentials, THE Login_Page SHALL call the Auth_Service with email and password
2. WHEN the Auth_Service returns a successful response, THE Login_Page SHALL store the access token via Auth_Context
3. WHEN authentication succeeds, THE Login_Page SHALL display a success toast notification
4. WHEN authentication fails, THE Login_Page SHALL display an error toast notification with the error message
5. WHILE the authentication request is in progress, THE Login_Page SHALL disable the submit button and show a loading indicator

### Requirement 6: Role-Based Redirection

**User Story:** As a user, I want to be redirected to the appropriate page after login, so that I can access features relevant to my role.

#### Acceptance Criteria

1. WHEN a user with the "student" role logs in successfully, THE Login_Page SHALL redirect to `/`
2. WHEN a user with the "teacher" role logs in successfully, THE Login_Page SHALL redirect to `/admin`
3. WHEN a user with the "superuser" role logs in successfully, THE Login_Page SHALL redirect to `/admin`
4. WHEN a URL contains a `callbackUrl` query parameter, THE Login_Page SHALL redirect to the callback URL after successful login
5. THE Login_Page SHALL use Next.js `useRouter` for client-side navigation

### Requirement 7: Loading and Disabled States

**User Story:** As a user, I want clear visual feedback during the login process, so that I understand the current state of my request.

#### Acceptance Criteria

1. WHILE the form is submitting, THE Button SHALL display "登录中..." text
2. WHILE the form is submitting, THE Input fields SHALL be disabled
3. WHEN an authentication error occurs, THE Login_Page SHALL re-enable the form for retry
4. THE Login_Page SHALL maintain consistent styling between loading and non-loading states

### Requirement 8: Accessibility Compliance

**User Story:** As a user with accessibility needs, I want the login form to be accessible, so that I can use assistive technologies effectively.

#### Acceptance Criteria

1. THE Input components SHALL have associated Label components with proper `htmlFor` attributes
2. WHEN a validation error occurs, THE Input component SHALL have `aria-invalid` set to `true`
3. WHEN a validation error occurs, THE error message SHALL be linked to the input via `aria-describedby`
4. THE Button SHALL have appropriate `aria-label` or accessible text content
5. THE Login_Page SHALL support keyboard navigation through form fields

### Requirement 9: Error Handling

**User Story:** As a user, I want clear error messages when login fails, so that I can understand and correct the issue.

#### Acceptance Criteria

1. WHEN the backend returns an authentication error, THE Login_Page SHALL display the error message from the response
2. WHEN a network error occurs, THE Login_Page SHALL display a generic error message "登录失败，请检查网络连接"
3. WHEN an unexpected error occurs, THE Login_Page SHALL display "登录失败，请检查账号密码"
4. THE Login_Page SHALL log errors to the console for debugging purposes
5. WHEN an error occurs, THE Login_Page SHALL preserve the user's email input for convenience

### Requirement 10: Code Quality and Maintainability

**User Story:** As a developer, I want the login page code to be clean and maintainable, so that future changes are easy to implement.

#### Acceptance Criteria

1. THE Login_Page SHALL use TypeScript with strict type checking
2. THE Login_Page SHALL separate the form component from the page component if `useSearchParams` is required
3. THE Login_Page SHALL use the existing `login` function from `@/lib/api/auth` for API calls
4. THE Login_Page SHALL use the existing `useAuth` hook from `@/lib/auth/context` for authentication state
5. THE Login_Page SHALL follow the project's ESLint and Prettier configurations
