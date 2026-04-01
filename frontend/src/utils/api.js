/**
 * Central API helper — always sends credentials (SSO cookie) and
 * never manually attaches a Bearer token.
 *
 * Usage:
 *   import { apiFetch } from '../utils/api';
 *   const res = await apiFetch('/api/clients/list');
 *   const data = await res.json();
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * @param {string} path  - e.g. '/api/clients/list'
 * @param {RequestInit} options - standard fetch options (method, body, headers, …)
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const mergedOptions = {
        ...options,
        credentials: 'include',          // send SSO cookie on every request
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
    };
    return fetch(url, mergedOptions);
}
