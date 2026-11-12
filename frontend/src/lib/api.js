let getAuthToken = null;

const configuredApiOrigin = (import.meta.env.VITE_API_ORIGIN || "").trim().replace(/\/$/, "");
if (configuredApiOrigin && !/^https:\/\/[^/?#]+$/i.test(configuredApiOrigin)) {
    throw new Error("VITE_API_ORIGIN must be an HTTPS origin without a path.");
}
const apiBase = `${configuredApiOrigin}/api`;

// Installed only while a Clerk-authenticated app tree is mounted.
export function setAuthTokenGetter(getter) {
    getAuthToken = getter;
}

export async function apiFetch(path, options = {}) {
    if (typeof getAuthToken !== "function") {
        throw new Error("Sign in is required before accessing Stillspace.");
    }

    const token = await getAuthToken();
    if (!token) {
        throw new Error("Your session is unavailable. Please sign in again.");
    }

    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${token}`);

    return fetch(`${apiBase}${path}`, {
        ...options,
        headers,
    });
}

export async function request(path, options = {}) {
    const response = await apiFetch(path, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        const message =
            response.status === 403
                ? "This account does not have an active Stillspace invitation."
                : response.status === 401
                    ? "Your session was not accepted. Please sign in again."
                    : response.status === 503
                        ? "Authentication service temporarily unavailable. Please try again."
                        : typeof errorData?.detail === "string"
                            ? errorData.detail
                            : `API request failed: ${response.status}`;

        throw new Error(message);
    }

    if (response.status === 204) return null;

    return response.json();
}

export function getJournals() {
    return request("/journals/");
}

export function getJournal(journalId) {
    return request(`/journals/${encodeURIComponent(journalId)}`);
}

export function getEntries(journalId) {
    return request(`/entries/?journal_id=${encodeURIComponent(journalId)}`);
}

export function createJournal({title, type}) {
    return request("/journals/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title, type}),
    });
}

export function renameJournal(journalId, title) {
    return request(`/journals/${encodeURIComponent(journalId)}/rename`, {
        method: "PATCH", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title}),
    });
}

export function archiveJournal(journalId) {
    return request(`/journals/${encodeURIComponent(journalId)}/archive`, {method: "PATCH"});
}

export function restoreJournal(journalId) {
    return request(`/journals/${encodeURIComponent(journalId)}/restore`, {method: "PATCH"});
}
