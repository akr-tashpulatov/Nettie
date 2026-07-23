## Project Overview
# Nettie
Nettie is an intelligent test preparation platform that streamlines exam studying. Create tests in two flexible ways: upload pre-formatted question files for instant processing, or build them manually. Each test automatically generates a randomized set of random questions tailored to your preparation mode.

```bash
yarn dev      # Start dev server (localhost:3000)
yarn build    # Production build (standalone output)
yarn lint     # ESLint
npx tsc --noEmit # Type-check
```

No test framework is configured.

### Feature Modules (`src/features/<name>/`)

Every feature follows this structure:

- **`api/`** — React Query hooks (`useQuery`/`useMutation`) wrapping functions from `src/shared/api/generated.ts`. Queries use `staleTime: 60000`. Mutations invalidate their query key on success.
- **`model/`** — Zod schema factories that accept a `t` translator function for i18n validation messages, plus React Hook Form hooks (`useCreate*Form`, `useUpdate*Form`) that wire together the schema, mutation, toast notifications, and error handling.
- **`ui/`** — Components: TanStack React Table tables, Shadcn Dialog-based create/edit/delete dialogs, select dropdowns.

### i18n
- Two locales: Russian (`ru`, default) and Kazakh (`kk`). Set via `NEXT_LOCALE` cookie.
- Translation files: `src/shared/messages/ru.json` and `kk.json`.
- `useTranslations()` in client components. Zod schemas take `t` as parameter.

## Key Conventions
- **Adding a feature:** Create `src/features/<name>/` with `api/`, `model/`, `ui/`. Add types in `types.ts`, endpoints in `endpoints.ts`, API functions in `generated.ts`, translations in both `ru.json` and `kk.json`, page in `src/app/dashboard/<name>/page.tsx`.
- **Query keys:** `['resourceName', queryParams]` — e.g., `['branches', query]`.
- **Form pattern:** `getCreate*Schema(t)` → `useForm({ resolver: zodResolver(...) })` → `mutateAsync` → toast success/error → `setError("root", ...)` for server errors.
- **Classnames:** Use `cn()` from `src/shared/lib/utils.ts` for merging.

## Key Patterns & Architecture

### 1. Feature-Driven Module Structure
Each feature follows a consistent pattern:
```
feature/
├── api/              # API calls & mutations
│   └── *-api.tsx     # Export useQuery/useMutation hooks
├── model/            # Business logic & forms
│   ├── use-*-form.ts # Form hook (react-hook-form)
│   └── *-schema.ts   # Zod validation schema
└── ui/               # React components
    ├── *-table.tsx   # Data display tables
    ├── *-dialog.tsx  # Create/edit/delete dialogs
    └── *-form.tsx    # Form components
```

### 2. API Layer
- **Location:** `/src/shared/api/generated.ts` (auto-generated functions)
- **HTTP Client:** Axios instance
- **Request Format:** 
  - Standard JSON for data endpoints
  - FormData for file uploads (via `createInstanceWithFile`)
- **Response Handling:** All responses return typed DTOs

**Key Files:**
- `api-instance.ts` - Axios setup with 401 interceptor + token refresh queue
- `api.config.ts` - Environment-aware base URL (dev uses NEXT_PUBLIC_API_URL, prod uses /api/v1)
- `types.ts` - Shared TypeScript interfaces for DTOs

### 5. Form Handling Pattern
**Standard approach across all features:**
```typescript
// 1. Define schema with i18n support
export const getCreateBranchSchema = (t: (key: string) => string) => 
  z.object({ name: z.string().min(2, t("errors.minLength2")) })

// 2. Create form hook
export const useCreateBranchForm = ({ onSuccess }) => {
  const t = useTranslations();
  const { mutateAsync, isPending } = useCreateBranchMutation();
  const { register, handleSubmit, errors, setError } = useForm({
    resolver: zodResolver(getCreateBranchSchema(t))
  });
  
  const onSubmit = async (data) => {
    try { await mutateAsync(data); onSuccess(); }
    catch (error) { setError("root", { message: ... }) }
  };
  return { register, handleSubmit: handleSubmit(onSubmit), errors, isPending };
}

// 3. Use in component
export function CreateBranchForm() {
  const { register, handleSubmit, errors } = useCreateBranchForm({ ... });
  return <form onSubmit={handleSubmit}>...</form>;
}
```

### 6. Data Fetching with React Query
- **Queries:** Implement with `useQuery` + `staleTime` (e.g., 1 minute)
- **Mutations:** Invalidate cache on success with `queryClient.invalidateQueries`
- **QueryKey Pattern:** `['resourceName', queryParams?]`

Example:
```typescript
export const useGetBranchesQuery = (query?: QueryBranchesDto) => {
  return useQuery({
    queryFn: () => getBranches(query),
    queryKey: ['branches', query],
    staleTime: 1 * 60 * 1000
  });
}
```

## Development Guidelines

### Adding a New Feature
1. Create feature directory in `/src/features/[feature-name]/`
2. Structure: `api/`, `model/`, `ui/`
3. Define DTOs in `/src/shared/api/types.ts`
4. Add API endpoint to `/src/shared/constants/endpoints.ts`
5. Generate API function in `/src/shared/api/generated.ts`
6. Create useQuery/useMutation hooks in `api/[feature]-api.tsx`
7. Create form schema & hook in `model/`
8. Create UI components in `ui/`
9. Add translations to `messages/ru.json` and `messages/kk.json`
10. Add page in `/src/app/dashboard/[feature]/page.tsx`

### Forms
- Always use Zod for validation
- Accept i18n translations in schema builder functions
- Use React Hook Form with `resolver: zodResolver()`
- Handle both field-level and server errors
- Display errors with React Hot Toast for notifications

### API Calls
- Use auto-generated functions from `generated.ts`
- Wrap in React Query hooks (useQuery/useMutation)
- Always invalidate affected query keys on mutation success
- Handle Axios errors properly (check response.status, response.data.message)

### Components
- Use Shadcn/ui base components
- Apply Tailwind CSS classes directly (no CSS files typically)
- Keep components focused and reusable
- Props should be typed with TypeScript interfaces
- Use `cn()` utility for conditional classnames

### Styling
- Tailwind CSS v4 with design tokens in CSS variables
- Color palette: primary, secondary, destructive, muted, accent, etc.
- Border radius: Use --radius variable (0.625rem base)
- Responsive: Use Tailwind breakpoints (sm, md, lg, etc.)
- Dark mode: Supported via custom --dark variant

### Type Safety
- All API responses typed via DTOs in `shared/api/types.ts`
- Form data typed via Zod schema inference
- React components use TypeScript interfaces for props
- No `any` types without justification

