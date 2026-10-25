"use strict";

async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    // Fallback for local HTTP development and older browsers.
    const temporaryInput = document.createElement("textarea");
    temporaryInput.value = text;
    temporaryInput.setAttribute("readonly", "");
    temporaryInput.style.position = "absolute";
    temporaryInput.style.left = "-9999px";
    document.body.appendChild(temporaryInput);
    temporaryInput.select();
    const copied = document.execCommand("copy");
    temporaryInput.remove();
    if (!copied) {
        throw new Error("The browser could not copy this link.");
    }
}

document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-url]");
    if (!button) return;

    const row = button.closest("td, .generated-link");
    const feedback = row ? row.querySelector(".copy-feedback") : null;
    const originalLabel = button.textContent;
    button.disabled = true;

    try {
        await copyText(button.dataset.copyUrl);
        button.textContent = "Copied";
        if (feedback) feedback.textContent = "Copied to clipboard.";
    } catch (_error) {
        button.textContent = "Try again";
        if (feedback) feedback.textContent = "Copy was unavailable. Select the link and copy it manually.";
    }

    window.setTimeout(() => {
        button.textContent = originalLabel;
        button.disabled = false;
    }, 1800);
});
