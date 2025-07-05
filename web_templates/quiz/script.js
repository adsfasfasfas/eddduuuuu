window.addEventListener('DOMContentLoaded', () => {
    const tg = (window.Telegram && window.Telegram.WebApp) || {
        ready: () => {},
        expand: () => {},
        sendData: (data) => console.log('Sending data:', data),
        close: () => console.log('Closing web app'),
    };
    tg.ready();
    tg.expand();

    const questions = [
        { key: "study_format", type: "single", title: "ទម្រង់ បែបបទនៃការរៀនដែលអ្នកចូលចិត្ត", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ការបង្រៀន", "ការអនុវត្ត", "ការងារជាក្រុម"] },
        { key: "study_hours", type: "single", title: "តើអ្នកមានបំណងសិក្សាប៉ុន្មានម៉ោងក្នុងមួយសប្តាហ៍", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["តិចជាង ១០", "១០-២០", "២០-៣០", "ច្រើនជាង ៣០"] },
        { key: "fav_subjects", type: "multiple", title: "មុខវិជ្ជាដែលចូលចិត្តជាងគេ", subtitle: "អាចជ្រើសរើសបានច្រើន", options: ["គណិតវិទ្យា", "វិទ្យាសាស្ត្រ", "ភាសា", "សិល្បៈ", "សង្គម"] },
        { key: "job_interest", type: "multiple", title: "អាជីពការាងរដែលចាប់អារម្មណ៍ជាងគេ", subtitle: "អាចជ្រើសរើសបានច្រើន", options: ["វិស្វករ", "គ្រូពេទ្យ", "គ្រូបង្រៀន", "អ្នកជំនួញ", "សិល្បករ", "អ្នកបង្កើតកម្មវិធី", "អ្នកទីផ្សារ"] },
        { key: "work_style", type: "single", title: "របៀបនៃការធ្វើការរបស់អ្នក", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ម្នាក់ឯង", "ជាក្រុម", "ជាអ្នកដឹកនាំ", "ជាអ្នកតាម"] },
        { key: "company_type", type: "single", title: "ប្រភេទស្ថាប័នដែលចង់ធ្វើការ", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["រដ្ឋាភិបាល", "ឯកជន", "ក្រុមហ៊ុនបច្ចេកវិទ្យាថ្មី (Startup)", "អង្គការមិនស្វែងរកប្រាក់ចំណេញ"] },
        { key: "value_priority", type: "single", title: "អ្វីដែលអ្នកឲ្យតម្លៃជាងគេ", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ប្រាក់ខែ", "ស្ថិរភាព", "តុល្យភាពការងារនិងជីវិត", "ការរីកចម្រើន"] },
        { key: "social_preference", type: "single", title: "តើអ្នកចូលចិត្តការងារសង្គមប៉ុណ្ណា?", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ចូលចិត្តខ្លាំង", "មធ្យម", "មិនចូលចិត្ត"] },
        { key: "future_aspiration", type: "single", title: "គោលដៅអនាគត", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["អ្នកជំនាញ", "អ្នកគ្រប់គ្រង", "ម្ចាស់អាជីវកម្ម", "អ្នកធ្វើការឯករាជ្យ"] },
        { key: "stress_tolerance", type: "single", title: "តើអ្នកអាចទ្រាំទ្រនឹងសម្ពាធបានកម្រិតណា?", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ល្អណាស់", "មធ្យម", "មិនល្អ"] },
        { key: "location", type: "single", title: "ខេត្ត/ក្រុងដែលចង់សិក្សា", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ភ្នំពេញ", "សៀមរាប", "បាត់ដំបង", "គ្រប់ទីកន្លែង"] },
        { key: "gpa", type: "single", title: "និទ្ទេសបាក់ឌុបរបស់អ្នក", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["A", "B", "C", "D", "E"] },
        { key: "budget", type: "single", title: "ថវិកាដែលអ្នកមានសម្រាប់ចំណាយថ្លៃសិក្សាប្រចាំឆ្នាំ (USD)", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["<$500", "$500-$1000", "$1000-$2000", ">$2000"] },
        { key: "english_proficiency", type: "single", title: "សមត្ថភាពភាសាអង់គ្លេសរបស់អ្នក", subtitle: "ជ្រើសរើសតែមួយប៉ុណ្ណោះ", options: ["ល្អណាស់", "មធ្យម", "តិចតួច"] }
    ];

    let currentIndex = 0;
    const answers = {};
    const cardStack = document.getElementById('card-stack');
    const nextBtn = document.getElementById('next-btn');
    const backBtn = document.getElementById('back-btn');
    const restartBtn = document.getElementById('restart-btn');
    const progressDots = document.getElementById('progress-dots');
    const progressBar = document.getElementById('progress-bar');
    const summaryPanel = document.getElementById('summary-panel');
    const summaryList = document.getElementById('summary-list');
    const submitBtn = document.getElementById('submit-btn');

    function renderDots() {
        progressDots.innerHTML = '';
        questions.forEach((_, i) => {
            const dot = document.createElement('span');
            dot.className = 'dot' + (i === currentIndex ? ' active' : '');
            progressDots.appendChild(dot);
        });
    }

    function updateProgress() {
        const percentage = ((currentIndex) / (questions.length - 1)) * 100;
        progressBar.style.width = `${percentage}%`;
        renderDots();
    }
    
    function renderCard() {
        const q = questions[currentIndex];
        const card = document.createElement('div');
        card.className = 'question-card';
        card.innerHTML = `<h2>${q.title}</h2><p>${q.subtitle}</p><div class="options"></div>`;
        const optionsContainer = card.querySelector('.options');
        
        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = opt;

            const currentAnswer = answers[q.key];
            if (q.type === 'multiple' && currentAnswer && currentAnswer.includes(opt)) {
                btn.classList.add('selected');
            } else if (q.type === 'single' && currentAnswer === opt) {
                btn.classList.add('selected');
            }

            btn.addEventListener('click', () => {
                const selectedAnswer = answers[q.key];
                if (q.type === 'multiple') {
                    if (!selectedAnswer) answers[q.key] = [];
                    const index = answers[q.key].indexOf(opt);
                    if (index > -1) {
                        answers[q.key].splice(index, 1);
                        btn.classList.remove('selected');
                    } else {
                        answers[q.key].push(opt);
                        btn.classList.add('selected');
                    }
                } else {
                    optionsContainer.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                    answers[q.key] = opt;
                    btn.classList.add('selected');
                }
                nextBtn.disabled = !answers[q.key] || (Array.isArray(answers[q.key]) && answers[q.key].length === 0);
            });
            optionsContainer.appendChild(btn);
        });

        cardStack.innerHTML = '';
        cardStack.appendChild(card);
        
        nextBtn.disabled = !answers[q.key] || (Array.isArray(answers[q.key]) && answers[q.key].length === 0);
        backBtn.disabled = currentIndex === 0;
        nextBtn.textContent = currentIndex === questions.length - 1 ? 'មើលការសង្ខេប' : 'បន្ទាប់';
        updateProgress();
    }

    function showSummary() {
        document.querySelector('.quiz-shell').style.display = 'none';
        summaryPanel.classList.remove('hidden');
        summaryList.innerHTML = '';
        questions.forEach(q => {
            const ans = answers[q.key];
            const displayAns = Array.isArray(ans) ? ans.join(', ') : ans;
            summaryList.innerHTML += `<div><strong>${q.title}:</strong> ${displayAns || 'N/A'}</div>`;
        });
    }

    nextBtn.addEventListener('click', () => {
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            renderCard();
        } else {
            showSummary();
        }
    });

    backBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            renderCard();
        }
    });

    restartBtn.addEventListener('click', () => {
        if (confirm('តើអ្នកពិតជាចង់ចាប់ផ្តើមម្តងទៀតមែនទេ? ការរីកចម្រើនរបស់អ្នកនឹងត្រូវបាត់បង់។')) {
            currentIndex = 0;
            for(const key in answers) delete answers[key];
            document.querySelector('.quiz-shell').style.display = 'block';
            summaryPanel.classList.add('hidden');
            renderCard();
        }
    });

    submitBtn.addEventListener('click', () => {
        // Disable button and show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'កំពុងបញ្ជូន...'; // "Submitting..."

        try {
            const payload = { ...answers, source: 'quiz' };
            const payloadString = JSON.stringify(payload);
            
            // This log is for debugging in the webview console
            console.log("Submitting payload:", payloadString);

            tg.sendData(payloadString);

            // Note: We do not close the window here. We let Telegram handle it
            // after the data is successfully sent and processed by the bot.

        } catch (error) {
            console.error("Failed to stringify or send payload:", error);
            submitBtn.textContent = 'Error! Please Restart';
             // Optionally send an error to the bot for logging
            tg.sendData(JSON.stringify({ source: 'quiz_error', error: error.message }));
        }
    });

    renderCard();
}); 