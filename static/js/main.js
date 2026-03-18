// ── File count for ranker page ────────────────────────────────────────────────
function updateFileCount(input) {
    const count = input.files.length;
    const label = document.getElementById('file-count');
    if (!label) return;
    if (count === 0) {
        label.textContent = 'No files selected.';
        label.style.color = '';
    } else if (count > 20) {
        label.textContent = `⚠️ ${count} files selected — maximum is 20.`;
        label.style.color = '#dc2626';
    } else {
        label.textContent = `✅ ${count} file${count > 1 ? 's' : ''} selected.`;
        label.style.color = '#059669';
    }
}

// ── Loader overlay ─────────────────────────────────────────────────────────────
function showLoader(isRanker = false) {
    const fileInput = isRanker
        ? document.getElementById('resumes')
        : document.getElementById('resume');

    if (fileInput && fileInput.files.length > 0) {
        const overlay = document.getElementById('loader');
        if (overlay) overlay.classList.remove('hidden');
    }
}
