# Legal Team — SSO Integration Task Sheet

*Replace local JWT login with NiFo/TYN SSO and keep local legal roles*

> **Important caution**
> - Your backend is already closer to secure production than Invoice.
> - Main work is changing the auth source and fixing CORS for cookie-based auth.
> - Most legal endpoints already use `verify_token`, so this migration is straightforward if you do it cleanly.

---

## 1. What is changing

- Production login moves to NiFo/TYN.
- Your app must validate the central shared cookie instead of expecting `Authorization: Bearer` from browser storage.
- You still keep local Legal roles such as `admin`, `legal_team`, and `client`.

---

## 2. Code touch points in your repo

| Layer    | File / Area                          | What to change |
|----------|--------------------------------------|----------------|
| Backend  | `backend/main.py`                    | This is the key file. Replace `verify_token` auth source, add `/auth/me`, keep `/api/auth/login` only for local dev, and fix CORS. |
| Frontend | `frontend/src/App.jsx`               | Stop loading token and user from `localStorage` as primary auth state. |
| Frontend | `frontend/src/pages/Login.jsx`       | Keep only as local-dev fallback. In production, unauthenticated users should return to NiFo login. |
| Frontend | API calls across pages/components    | Switch to cookie-based requests with credentials included and remove manual bearer token attachment. |

---

## 3. Backend tasks

1. **Fix CORS first.** Cookie auth will not work correctly with `allow_origins=['*']` together with `allow_credentials=True`. Use explicit origins.
2. **Replace `verify_token`.** In production, `verify_token` must read the shared cookie and validate it via central `GET /api/sso/me`.
3. **Map identity to local legal user.** Use the central email to find the local user and return local legal role.
4. **Add `GET /auth/me`.** Frontend will use this to initialize session state.
5. **Keep local login only for dev.** `/api/auth/login` can remain behind `ALLOW_LOCAL_LOGIN=true`.
6. **Protect all existing routes through the new logic.** Because many routes already depend on `verify_token`, one clean change here gives broad coverage.

---

## 4. Frontend tasks

7. **Bootstrap from backend.** On app start, call `/auth/me`.
8. **Use credentials.** All requests must use `credentials: include` / `withCredentials: true`.
9. **Remove local bearer-token dependency.** Stop treating `localStorage` token as the production auth source.
10. **Keep only lightweight user state.** Store the returned user object for routing and display, not for trust.
11. **Hide local login in production.** The legal login screen remains useful only for standalone local testing.

---

## 5. Required API contract

```
GET /auth/me

200 → authenticated and authorized for Legal app
401 → not centrally logged in
403 → centrally logged in but not onboarded in Legal app
```

---

## 6. Special note on your current repo

- `backend/main.py` already contains `verify_token` and many protected endpoints. Replacing the implementation cleanly gives you the fastest migration path.
- `frontend/src/App.jsx` currently reads token and user from `localStorage`. That must stop being the production source of truth.
- Cookie auth will fail until CORS is corrected.

---

## 7. Do not do these shortcuts

- Do not keep wildcard origins with credentialed cookie auth.
- Do not parse role from frontend state and trust it.
- Do not keep both local bearer auth and SSO active in production without a clear feature flag.

---

## 8. Acceptance criteria

- A centrally logged-in user can open Legal without the local login page.
- Existing protected endpoints continue to enforce role checks correctly after `verify_token` is replaced.
- Cross-origin cookie requests succeed from the approved frontend origins.
- Local login still works only when `ALLOW_LOCAL_LOGIN=true`.

---

## 9. What you need from central team

- TYN server will own login and set one shared auth cookie.
- Child apps must validate the incoming cookie by calling the central SSO endpoint and must not trust frontend state.
- Each app will still map the central email to its own local user and local role.
- Final list of approved origins to place in CORS config.
- Central logout URL.
