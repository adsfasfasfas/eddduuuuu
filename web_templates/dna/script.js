// REPLACE WHOLE FILE WITH NEW IMPLEMENTATION
// ===================================================================================
// EduGuide – DNA Results Page
// Dynamically render major recommendations and handle university requests
// ===================================================================================

document.addEventListener("DOMContentLoaded", () => {
    /* ---------------------------------------------------------------------------
     *  Telegram WebApp Initialisation
     * ------------------------------------------------------------------------ */
    const tgAvailable = !!(window.Telegram && window.Telegram.WebApp);
    const tg = tgAvailable ? window.Telegram.WebApp : null;
    if (tgAvailable) {
        tg.ready();
        tg.expand();
    }

    /* ---------------------------------------------------------------------------
     *  Helpers
     * ------------------------------------------------------------------------ */
    const qs = new URLSearchParams(window.location.search);
    const maxScore = parseFloat(qs.get("max_score")) || 0;

    const decodeJSONParam = (key, fallback) => {
        const raw = qs.get(key);
        if (!raw) return fallback;
        try {
            // First, base64 decode the raw string
            const decodedB64 = atob(raw);
            // Then, decode the URI component and parse JSON
            return JSON.parse(decodeURIComponent(decodedB64));
        } catch (err) {
            console.error(`Failed to parse query param ${key}:`, err);
            return fallback;
        }
    };

    /* ---------------------------------------------------------------------------
     *  Data – majors + user_profile passed from bot
     * ------------------------------------------------------------------------ */
    const majors = decodeJSONParam("majors", []);
    const userProfile = decodeJSONParam("user_profile", {});

    /* ---------------------------------------------------------------------------
     *  UI Elements
     * ------------------------------------------------------------------------ */
    const resultsContainer = document.getElementById("results-container");
    const uniContainer = document.getElementById("university-recommendations");

    if (!majors.length) {
        resultsContainer.innerHTML =
            "<p>No personalized recommendations could be generated. Please try the quiz again.</p>";
        return;
    }

    /* ---------------------------------------------------------------------------
     *  Toast helper – show feedback on card click
     * ------------------------------------------------------------------------ */
    function showToast(message) {
        let toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2500);
    }

    /* ---------------------------------------------------------------------------
     *  Render Major Cards (updated with toast call)
     * ------------------------------------------------------------------------ */
    majors.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "major-card";
        card.style.animationDelay = `${0.15 * index}s`;

        const title = document.createElement("h2");
        title.textContent = item.major_name;
        card.appendChild(title);

        // Optional match-score bar if score available (>0)
        if (typeof item.score === "number" && item.score > 0) {
            const scoreLabel = document.createElement("div");
            scoreLabel.className = "match-score";
            
            const pct = maxScore > 0 ? (item.score / maxScore) * 100 : 0;
            scoreLabel.textContent = `${Math.round(pct)}% match`;
            card.appendChild(scoreLabel);

            const bar = document.createElement("div");
            bar.className = "score-bar";
            const fill = document.createElement("div");
            fill.className = "score-fill";
            fill.style.width = `${pct}%`;
            bar.appendChild(fill);
            card.appendChild(bar);
        }

        const reason = document.createElement("p");
        reason.textContent = item.reason || "";
        card.appendChild(reason);

        // --- NEW: Feedback Buttons ---
        const feedbackContainer = document.createElement("div");
        feedbackContainer.className = "feedback-container";

        const createFeedbackButton = (type) => {
            const button = document.createElement("button");
            button.className = `feedback-btn ${type}`;
            button.innerHTML = type === 'like' ? '👍' : '👎';
            button.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card click event
                if (tgAvailable) {
                    const payload = {
                        source: "feedback",
                        major_name: item.major_name,
                        user_profile: userProfile,
                        feedback_type: type
                    };
                    console.log("Sending feedback:", payload);
                    tg.sendData(JSON.stringify(payload));
                    tg.HapticFeedback?.notificationOccurred(type === 'like' ? 'success' : 'warning');
                    showToast(`Feedback '${type}' submitted!`);
                    // Optional: Visually disable buttons after click
                    feedbackContainer.querySelectorAll('.feedback-btn').forEach(btn => btn.disabled = true);
                } else {
                    showToast("Feedback requires running inside Telegram.");
                }
            });
            return button;
        };

        feedbackContainer.appendChild(createFeedbackButton('like'));
        feedbackContainer.appendChild(createFeedbackButton('dislike'));
        card.appendChild(feedbackContainer);

        // Click handler – request university matches via bot
        card.addEventListener("click", () => {
            if (tgAvailable) {
                const payload = {
                    source: "dna_university_request",
                    major_name_en: item.major_name_en, // Use major_name_en consistently
                    user_profile: userProfile
                };
                console.log("Sending university request:", payload);
                tg.sendData(JSON.stringify(payload));
                tg.HapticFeedback?.impactOccurred("medium");
                showToast("🔍 Matching universities are being sent to chat…");
            } else {
                showToast("Telegram WebApp not detected – open inside Telegram to get full features.");
            }
        });

        resultsContainer.appendChild(card);
    });

    /* ---------------------------------------------------------------------------
     *  Placeholder text for university container (instructions)
     * ------------------------------------------------------------------------ */
    uniContainer.innerHTML =
        "<p>Tap a major above to get our top university recommendations. They will be sent back to you in the chat.</p>";
}); 