# Implementation Plan: Login Page Refactor

## Overview

This implementation plan refactors the login page to use React Hook Form + Zod for validation and Shadcn/ui components for UI. The key changes include:
- Creating a Zod schema for form validation
- Extracting LoginForm into a separate component with Suspense boundary
- Using Shadcn/ui Card, Input, Label, and Button components
- Preventing native form submission issues in Next.js 16 + React 19

---

## Tasks

- [x] 1. Create Zod schema for login form validation
  - Create `lib/schemas/login.ts` file
  - Define `loginFormSchema` with email and password validation rules
  - Export `LoginFormValues` type inferred from schema
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Create LoginForm component with React Hook Form integration
  - [x] 2.1 Create `app/(auth)/login/login-form.tsx` file
    - Import `useForm` from `react-hook-form` and `zodResolver` from `@hookform/resolvers/zod`
    - Import Shadcn/ui components: Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Input, Label, Button
    - Import `useSearchParams` for callback URL handling
    - Configure `useForm` with `zodResolver` and `mode: 'onChange'`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.5_

  - [x] 2.2 Implement form UI with Shadcn/ui components
    - Use Card components for layout structure
    - Use Input components with `register` for email and password fields
    - Use Label components with proper `htmlFor` attributes
    - Use Button component with `type="button"` and `onClick={handleSubmit(onSubmit)}`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.4_

  - [x] 2.3 Implement validation error display
    - Display error messages below corresponding input fields
    - Set `aria-invalid` on inputs when errors exist
    - Link error messages via `aria-describedby`
    - _Requirements: 3.3, 3.4, 8.2, 8.3_

  - [x] 2.4 Implement authentication flow
    - Call `loginApi` with email and password on valid submission
    - Store token via `useAuth().login()`
    - Display success toast on successful login
    - Display error toast on failed login
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 2.5 Implement role-based redirection
    - Redirect to `callbackUrl` if present in URL params
    - Redirect to `/admin` for teacher or superuser roles
    - Redirect to `/` for student role
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 2.6 Implement loading and disabled states
    - Display "登录中..." text on button while submitting
    - Disable input fields while submitting
    - Re-enable form after error
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 2.7 Implement error handling
    - Display backend error message on authentication failure
    - Display "登录失败，请检查网络连接" for network errors
    - Display "登录失败，请检查账号密码" for unexpected errors
    - Log errors to console for debugging
    - Preserve email input on error
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 3. Update LoginPage with Suspense wrapper
  - [x] 3.1 Update `app/(auth)/login/page.tsx`
    - Import `Suspense` from React
    - Import `LoginForm` from `./login-form`
    - Wrap `LoginForm` with `Suspense` boundary
    - Provide loading spinner as fallback
    - _Requirements: 10.2_

- [x] 4. Checkpoint - Verify form validation and UI
  - Ensure form displays validation errors correctly
  - Ensure Shadcn/ui components render properly
  - Ensure loading states work as expected
  - Ask the user if questions arise.

- [x] 5. Write unit tests for login form
  - [x] 5.1 Write tests for Zod schema validation
    - Test empty email shows "请输入邮箱"
    - Test invalid email format shows "请输入有效的邮箱地址"
    - Test empty password shows "请输入密码"
    - Test password < 6 chars shows "密码至少为 6 位"
    - Test valid inputs pass validation
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 5.2 Write tests for form state and UI behavior
    - Test button shows "登录中..." when submitting
    - Test inputs are disabled when submitting
    - Test form re-enabled after error
    - Test error messages are cleared on input
    - _Requirements: 3.4, 7.1, 7.2, 7.3_

  - [x] 5.3 Write tests for accessibility
    - Test Label components have proper `htmlFor` attributes
    - Test inputs have `aria-invalid` when errors exist
    - Test error messages are linked via `aria-describedby`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6. Write integration tests for login flow
  - [x] 6.1 Write test for successful login flow
    - Fill valid credentials
    - Click login button
    - Verify API call made with correct data
    - Verify token stored
    - Verify redirect to correct page based on role
    - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3_

  - [x] 6.2 Write test for failed login flow
    - Fill invalid credentials
    - Click login button
    - Verify error toast displayed
    - Verify form re-enabled for retry
    - _Requirements: 5.4, 7.3, 9.1_

  - [x] 6.3 Write test for callback URL handling
    - Navigate to `/login?callbackUrl=/profile`
    - Complete login
    - Verify redirect to `/profile`
    - _Requirements: 6.4_

- [x] 7. Final checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all integration tests
  - Verify all acceptance criteria are met
  - Ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- The design uses TypeScript with Next.js 16 + React 19
- Form submission uses `type="button"` with `onClick` handler to prevent native form submission issues
- `useSearchParams()` requires Suspense boundary in Next.js 15+
