// Mini Checklist App Logic
window.addEventListener('DOMContentLoaded', () => {
    let tg;
    try {
        tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
    } catch (e) {
        tg = { sendData: (d) => console.log('Local send:', d), themeParams: {} };
    }
    const isTG = !!tg.initData || window.Telegram?.WebApp?.initData;

    // ----- Telegram theme adaptation -----
    const root = document.documentElement;
    function applyTGTheme() {
        const p = tg.themeParams || {};
        const addHash = c => c ? (c.startsWith('#') ? c : '#' + c) : undefined;
        if (p.bg_color) root.style.setProperty('--bg', addHash(p.bg_color));
        if (p.button_color) root.style.setProperty('--primary', addHash(p.button_color));
        if (p.button_text_color) root.style.setProperty('--text', addHash(p.button_text_color));
        if (p.hint_color) {
            const clean = p.hint_color.replace('#', '');
            const rgb = clean.match(/.{2}/g).map(h => parseInt(h, 16));
            root.style.setProperty('--border', `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.3)`);
        }
    }
    applyTGTheme();
    tg.onEvent && tg.onEvent('themeChanged', applyTGTheme);

    // ----- Telegram MainButton -----
    function configureMainBtn() {
        if (!isTG) return;
        tg.MainButton.setParams({
            text: '📤 ផ្ញើទៅ Bot',
            color: tg.themeParams?.button_color ? `#${tg.themeParams.button_color}` : '#0066cc',
            text_color: tg.themeParams?.button_text_color ? `#${tg.themeParams.button_text_color}` : '#ffffff'
        });
        tg.onEvent('mainButtonClicked', () => sendToBot());
        tg.MainButton.show();
    }
    configureMainBtn();

    /* ------------------------------- State ------------------------------- */
    let tasks = [];
    try { tasks = JSON.parse(localStorage.getItem('checklist_tasks')) || []; } catch (_) {}
    // If empty, seed with default document checklist
    if (tasks.length === 0) {
        tasks = [
            { text: 'សំបុត្រកំណើត (Birth Certificate)', done: false, tag: '📑 Docs' },
            { text: 'អត្តសញ្ញាណប័ណ្ណ (National ID Copy)', done: false, tag: '📑 Docs' },
            { text: 'សញ្ញាបត្រសិក្សា (Diploma)', done: false, tag: '📚 Education' },
            { text: 'ពិន្ទុធម៌សិក្សា (Transcripts)', done: false, tag: '📚 Education' },
            { text: 'រូបថត (Passport Photo)', done: false, tag: '📸 Photo' }
        ];
    }

    /* ------------------------------- DOM ------------------------------- */
    const inputEl = document.getElementById('new-item-input');
    const addBtn = document.getElementById('add-btn');
    const listEl = document.getElementById('checklist-container');
    const progText = document.getElementById('progress-text');
    const progBar = document.getElementById('progress-bar');
    const markAllBtn = document.getElementById('mark-all-btn');
    const clearDoneBtn = document.getElementById('clear-done-btn');
    const sendBotBtn = document.getElementById('send-bot-btn');
    const tagTrigger = document.getElementById('tag-trigger');
    const tagOptions = document.getElementById('tag-options');
    const TAG_LIST = ["", "📑 Docs", "📚 Education", "📸 Photo", "🏠 Personal"]; // first empty = no tag
    const themeToggle = document.getElementById('theme-toggle');
    const actionsRow=document.querySelector('.actions-row');
    const searchInput=document.getElementById('search-input');
    const ringCanvas=document.getElementById('progress-ring');
    const rCtx=ringCanvas.getContext('2d');
    let confettiLoaded=false;

    /* --------------------------- Render & Update --------------------------- */
    function render() {
        const filter=searchInput.value.trim().toLowerCase();
        listEl.innerHTML = '';
        // Group by tag
        const groups = {};
        tasks.forEach(t => { const g = t.tag || 'Others'; if (!groups[g]) groups[g] = []; });

        Object.keys(groups).forEach(tag => {
            const heading = document.createElement('div'); heading.className = 'group-heading'; heading.textContent = tag; listEl.appendChild(heading);
            tasks.forEach((t, idx) => {
                if ((t.tag || 'Others') !== tag) return;
                if(filter && !t.text.toLowerCase().includes(filter)) return;
                const row = document.createElement('div'); row.className = 'check-item';
                row.setAttribute('draggable', 'true'); row.dataset.index = idx;

                // Checkbox & label
                const label = document.createElement('label'); label.style.flex = '1';
                const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = t.done;
                cb.addEventListener('change', () => { t.done = cb.checked; save(); });
                label.appendChild(cb); label.appendChild(document.createTextNode(' ' + t.text));
                row.appendChild(label);
                // Delete button
                const del = document.createElement('button'); del.className = 'icon-btn'; del.textContent = '✕';
                del.addEventListener('click', () => { const removed=tasks.splice(idx,1)[0]; save(); showToast('Deleted', ()=>{tasks.splice(idx,0,removed); save();}); });
                row.appendChild(del);

                // Drag events
                row.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', idx); row.classList.add('dragging'); });
                row.addEventListener('dragend', () => row.classList.remove('dragging'));

                row.addEventListener('dragover', e => { e.preventDefault(); const draggingIdx = parseInt(e.dataTransfer.getData('text/plain')); if (draggingIdx === idx) return; const after = idx > draggingIdx; listEl.insertBefore(document.querySelector('.dragging'), after ? row.nextSibling : row); });
                row.addEventListener('drop', e => { e.preventDefault(); const from = parseInt(e.dataTransfer.getData('text/plain')); const to = idx; const [moved] = tasks.splice(from, 1); tasks.splice(to, 0, moved); save(); });

                listEl.appendChild(row);
            });
        });
        updateProgress();
    }

    function updateProgress() {
        const total = tasks.length;
        const done = tasks.filter(t => t.done).length;
        progText.textContent = `${done}/${total} បញ្ចប់`;
        const pct = total ? (done / total) * 100 : 0;
        drawRing(pct);
        if(pct===100){ triggerConfetti(); }
    }

    function save() {
        localStorage.setItem('checklist_tasks', JSON.stringify(tasks));
        render();
        if(isTG) tg.MainButton.show();
    }

    /* ----------------------------- Add Task ------------------------------ */
    function addTask() {
        const text = inputEl.value.trim();
        if (!text) return;
        const tag = currentTag;
        tasks.push({ text, done: false, tag });
        inputEl.value = '';
        save();
    }
    addBtn.addEventListener('click', addTask);
    inputEl.addEventListener('keypress', e => { if (e.key === 'Enter') addTask(); });

    /* ----------- Quick Action Handlers --------- */
    markAllBtn.addEventListener('click', () => { tasks.forEach(t => t.done = true); save(); });
    clearDoneBtn.addEventListener('click', () => { tasks = tasks.filter(t => !t.done); save(); });
    function sendToBot() {
        const payload = { source: 'checklist', tasks, progress: progText.textContent };
        tg.sendData ? tg.sendData(JSON.stringify(payload)) : console.log(payload);
    }
    sendBotBtn.addEventListener('click', sendToBot);

    /* Theme Toggle */
    let isLight = localStorage.getItem('chk_theme') === 'light';
    applyTheme();
    themeToggle.addEventListener('click', () => { isLight = !isLight; localStorage.setItem('chk_theme', isLight ? 'light' : 'dark'); applyTheme(); });
    function applyTheme() { document.body.classList.toggle('light', isLight); themeToggle.textContent = isLight ? '☀️' : '🌙'; }

    // Build dropdown
    TAG_LIST.slice(1).forEach(tag => { const opt = document.createElement('div'); opt.className = 'tag-option'; opt.textContent = tag; opt.addEventListener('click', () => { currentTag = tag; tagTrigger.textContent = tag || 'Tag'; tagOptions.classList.add('hidden'); }); tagOptions.appendChild(opt); });
    let currentTag = "";
    tagTrigger.addEventListener('click', () => { tagOptions.classList.toggle('hidden'); });
    document.addEventListener('click', e => { if (!tagTrigger.contains(e.target) && !tagOptions.contains(e.target)) { tagOptions.classList.add('hidden'); } });

    // initial render
    render();

    function updatePadding(){
        const sectionEl=document.querySelector('.section');
        const topBar=document.querySelector('.top-bar');
        const searchWrap=document.querySelector('.input-wrap');
        const topPad=(topBar?.offsetHeight||0)+(searchWrap?.offsetHeight||0)+12;
        sectionEl.style.paddingTop=topPad+"px";
        sectionEl.style.paddingBottom=(actionsRow.offsetHeight+20)+"px";
    }
    window.addEventListener('resize',updatePadding); updatePadding();

    /* --------------------- Progress Ring --------------------- */
    function drawRing(pct){
        const w=ringCanvas.width; const h=ringCanvas.height; const rad=w/2-8; rCtx.clearRect(0,0,w,h);
        rCtx.lineWidth=10; rCtx.strokeStyle='rgba(255,255,255,0.15)'; rCtx.beginPath(); rCtx.arc(w/2,h/2,rad,0,Math.PI*2); rCtx.stroke();
        rCtx.strokeStyle=getComputedStyle(document.documentElement).getPropertyValue('--accent');
        rCtx.beginPath(); rCtx.arc(w/2,h/2,rad,-Math.PI/2,(-Math.PI/2)+ (Math.PI*2*pct/100)); rCtx.stroke();
    }

    /* --------------------- Confetti --------------------- */
    function triggerConfetti(){
        if(!confettiLoaded){
            const s=document.createElement('script'); s.src='https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js'; document.body.appendChild(s); s.onload=()=>{confettiLoaded=true; confetti(); };
        }else{ confetti(); }
        function confetti(){ window.confetti({particleCount:120,spread:70,origin:{y:0.6}}); try{tg.HapticFeedback.impactOccurred('rigid');}catch(_){} }
    }

    /* --------------------- Toast Undo --------------------- */
    function showToast(msg,undoCb){
        const t=document.createElement('div'); t.className='toast'; t.textContent=msg+'  Undo'; t.addEventListener('click',()=>{undoCb();document.body.removeChild(t);}); document.body.appendChild(t); setTimeout(()=>t.classList.add('show'),50); setTimeout(()=>{t.classList.remove('show'); setTimeout(()=>t.remove(),300);},4000);
    }

    /* Haptic on checkbox change */
    function hapticLight(){ try{tg.HapticFeedback.selectionChanged();}catch(_){} }
    // attach in render inside cb change

    searchInput.addEventListener('input', () => render());
}); 