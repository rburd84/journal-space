async function request(path, options = {}) {
    const response = await fetch(`/api${path}`, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        console.error("API error:", {
            path,
            status: response.status,
            details: errorData,
        });

        throw new Error(`API request failed: ${response.status}`);
    }
    return response.json();
}

export function getJournals(userId) {
    return request(
        `/journals/?user_id=${encodeURIComponent(userId)}`
    );
}

export function getJournal(journalId) {
    return request(`/journals/${journalId}`);
}

export function getEntries(journalId) {
    return request(`/entries/?journal_id=${encodeURIComponent(journalId)}`);
}

export function createJournal({userId, title, type}) {
    return request("/journals/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            user_id: userId,
            title,
            type,
        })
    });
}

export function renameJournal(journalId, title) {
    return request(`/journals/${journalId}/rename`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({title}),
    });
}

export function archiveJournal(journalId) {
    return request(`/journals/${journalId}/archive`, {
        method: "PATCH",
    });
}

export function restoreJournal(journalId) {
    return request(`/journals/${journalId}/restore`, {
        method: "PATCH",
    });
}




















