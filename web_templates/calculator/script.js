document.addEventListener("DOMContentLoaded", () => {
    let tg;
    try {
        tg = window.Telegram.WebApp;
        tg.ready();
    } catch (e) {
        console.warn("Telegram WebApp not found. Using local mode.");
        tg = { sendData: (d) => console.log("Local send:", d) };
    }

    const tuitionEl = document.getElementById("annual-tuition");
    const livingEl = document.getElementById("living-cost");
    const durationEl = document.getElementById("duration");
    const scholarshipEl = document.getElementById("scholarship");
    const scholarshipVal = document.getElementById("scholarship-val");
    const otherCostEl = document.getElementById("other-cost");
    const incomeEl = document.getElementById("income");
    const salaryEl = document.getElementById("expected-salary");
    const advSection = document.getElementById("adv-section");
    const advToggle = document.getElementById("show-adv");
    const durationVal = document.getElementById("duration-val");

    const resultCard = document.getElementById("result-card");
    const tuitionAfterLbl = document.getElementById("tuition-after");
    const annualCostLbl = document.getElementById("annual-cost");
    const totalCostLbl = document.getElementById("total-cost");
    const shareBtn = document.getElementById("share-btn");
    const resetBtn = document.getElementById("reset-btn");

    let breakdown = null;

    const currency = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    // Compare IDs and prefill support
    const params = new URLSearchParams(location.search);
    const compareIdsParam = params.get("compare");
    const prefillTuition = params.get("prefill_tuition");
    const uniName = params.get("uni_name");
    let compareMode = false;
    let uniA = null; let uniB = null; let chart = null;

    function setupCompare(data){
        if(compareIdsParam){
            const ids = compareIdsParam.split(",").map(s=>parseInt(s));
            if(ids.length===2){
                uniA = data.find(u=>u.id===ids[0]);
                uniB = data.find(u=>u.id===ids[1]);
                if(uniA && uniB){
                    compareMode = true;
                    tuitionEl.value = uniA.tuition_fees.range_min;
                    livingEl.value = 0;
                    recalc();
                    return;
                }
            }
        }
    }

    // Restore previous session if exists
    const saved = JSON.parse(localStorage.getItem("calc-state")||"null");
    if(saved){
        [tuitionEl,livingEl,otherCostEl,incomeEl,salaryEl].forEach(el=>{ if(el && saved[el.id]!=null){ el.value = saved[el.id]; }});
        if(saved[scholarshipEl.id]!=null) scholarshipEl.value=saved[scholarshipEl.id];
        if(saved[durationEl.id]!=null) durationEl.value=saved[durationEl.id];
        advToggle.checked = !!saved.advOpen;
        advSection.classList.toggle("hidden", !advToggle.checked);
    }

    function updateChart(costA,costB){
        if(!compareMode) return;
        const ctx=document.getElementById("compareChart");
        document.getElementById("compareChart").classList.remove("hidden");
        if(chart){chart.data.datasets[0].data=[costA,costB]; chart.update(); return;}
        chart=new Chart(ctx,{
            type:"bar",
            data:{
                labels:[uniA.name_short||uniA.name_en,uniB.name_short||uniB.name_en],
                datasets:[{
                    label:"Total Cost",
                    data:[costA,costB],
                    backgroundColor:["#6366F1","#14B8A6"],
                    borderRadius:6,
                    maxBarThickness:60
                }]
            },
            options:{
                plugins:{legend:{display:false}},
                scales:{
                    x:{grid:{display:false},ticks:{color:getComputedStyle(document.documentElement).getPropertyValue('--text-color')}} ,
                    y:{grid:{color:"rgba(255,255,255,0.1)"},ticks:{color:getComputedStyle(document.documentElement).getPropertyValue('--text-color')}}
                }
            }
        });
    }

    function recalc() {
        const t = parseFloat(tuitionEl.value) || 0;
        const l = parseFloat(livingEl.value) || 0;
        const d = parseInt(durationEl.value) || 1;
        const sPct = parseFloat(scholarshipEl.value) || 0;
        const other = advToggle.checked ? parseFloat(otherCostEl.value) || 0 : 0;
        const income = advToggle.checked ? parseFloat(incomeEl.value) || 0 : 0;
        const salary = advToggle.checked ? parseFloat(salaryEl.value) || 0 : 0;

        scholarshipVal.textContent = `${sPct}%`;

        const tuitionAfter = t * (1 - sPct / 100);
        const annualCost = tuitionAfter + l + other - income;
        const total = annualCost * d;

        const yearlyIncome = salary * 12;
        const yearlyNet = yearlyIncome - annualCost;
        const paybackYears = yearlyNet > 0 ? (total / yearlyNet).toFixed(1) : "∞";

        tuitionAfterLbl.textContent = `ថ្លៃសិក្សាបន្ទាប់ពីអាហារូបករណ៍: ${currency(tuitionAfter)}/yr`;
        annualCostLbl.textContent = `ចំណាយសរុបក្នុងមួយឆ្នាំ: ${currency(annualCost)}`;
        totalCostLbl.textContent = `ចំណាយសរុប: ${currency(total)}`;
        if (document.getElementById("study-years")) {
            document.getElementById("study-years").textContent = `📚 ចំនួនឆ្នាំសិក្សា: ${d}`;
        } else {
            const liYears = document.createElement("li"); liYears.id = "study-years"; liYears.textContent = `📚 ចំនួនឆ្នាំសិក្សា: ${d}`; totalCostLbl.parentElement.appendChild(liYears);
        }

        let paybackLbl = document.getElementById("payback");
        if(!paybackLbl){ paybackLbl=document.createElement("li"); paybackLbl.id="payback"; totalCostLbl.parentElement.appendChild(paybackLbl);} 
        paybackLbl.textContent = `⏱ Pay-back period ≈ ${paybackYears} yrs`;

        // Update slider track gradient for scholarship
        scholarshipEl.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${sPct}%, rgba(255,255,255,0.2) ${sPct}%, rgba(255,255,255,0.2) 100%)`;

        resultCard.classList.remove("hidden");
        resetBtn.classList.remove("hidden");

        durationVal.textContent = d;

        // Breakdown chart update
        if(!breakdown){
            const ctx=document.getElementById("breakdownChart");
            const palette=["#6366F1","#14B8A6","#FBBF24","#F43F5E"]; // modern tailwind-esque colours
            breakdown = new Chart(ctx,{
                type:"doughnut",
                data:{
                    labels:["Tuition","Living","Other","Income (-)"],
                    datasets:[{
                        data:[],
                        backgroundColor:palette,
                        borderWidth:0,
                        hoverOffset:6,
                        borderRadius:4
                    }]
                },
                options:{
                    plugins:{
                        legend:{
                            position:"bottom",
                            labels:{
                                usePointStyle:true,
                                pointStyle:'circle',
                                padding:14,
                                color:getComputedStyle(document.documentElement).getPropertyValue('--text-color')||'#EAEAEA',
                                font:{
                                    size:12,
                                    family:'Kantumruy Pro, sans-serif'
                                }
                            }
                        }
                    },
                    cutout:"65%",
                }
            });
            ctx.classList.remove("hidden");
        }
        breakdown.data.datasets[0].data=[t,l,other,-income];
        breakdown.update();

        // persist state
        localStorage.setItem("calc-state",JSON.stringify({[tuitionEl.id]:tuitionEl.value,[livingEl.id]:livingEl.value,[otherCostEl.id]:otherCostEl.value,[incomeEl.id]:incomeEl.value,[salaryEl.id]:salaryEl.value,[scholarshipEl.id]:scholarshipEl.value,[durationEl.id]:durationEl.value,advOpen:advToggle.checked}));

        // Trigger MainButton if Telegram
        if(isTG){ tg.MainButton.show(); }

        return { t, l, d, sPct, other, income, salary, total };
    }

    [tuitionEl, livingEl, scholarshipEl, otherCostEl, incomeEl, salaryEl, durationEl].forEach(el => el.addEventListener("input", recalc));

    advToggle.addEventListener("change", () => {
        advSection.classList.toggle("hidden", !advToggle.checked);
        recalc();
    });

    // --- Telegram WebApp enhancements ---
    const isTG = !!tg.initData || window.Telegram.WebApp?.initData; // simple check
    const root = document.documentElement;

    function applyTGTheme(){
        if(!isTG) return;
        const p = tg.themeParams || {};
        // Map Telegram theme params to CSS custom properties with graceful fallbacks
        const addHash = (c)=> c ? (c.startsWith('#')?c:'#'+c) : undefined;
        if(p.bg_color)          root.style.setProperty('--bg-color', addHash(p.bg_color));
        if(p.secondary_bg_color)root.style.setProperty('--card-color', addHash(p.secondary_bg_color));
        if(p.text_color)        root.style.setProperty('--text-color', addHash(p.text_color));
        if(p.button_color)      root.style.setProperty('--primary-color', addHash(p.button_color));
        if(p.hint_color){
            // Slightly transparent border based on hint color
            const clean = p.hint_color.replace('#','');
            const rgb = clean.match(/.{2}/g).map(h=>parseInt(h,16));
            root.style.setProperty('--border-color', `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.35)`);
        }
    }

    applyTGTheme();
    tg.onEvent && tg.onEvent('themeChanged', applyTGTheme);

    // Expand the WebApp for better user experience
    try{ tg.expand(); }catch(_){}

    // Configure the MainButton behaviour
    if(isTG){
        tg.MainButton.setParams({
            text: '📤 បញ្ជូនទៅ Bot',
            color: tg.themeParams?.button_color ? `#${tg.themeParams.button_color}` : '#0A84FF',
            text_color: tg.themeParams?.button_text_color ? `#${tg.themeParams.button_text_color}` : '#ffffff'
        });
        tg.onEvent('mainButtonClicked', ()=>{
            sendResults();
        });
    }

    // Replace share button behaviour depending on context
    if(isTG){
        shareBtn.classList.add('hidden');
    }

    // Haptic feedback helper
    const haptic = (type='light')=>{
        try{ tg.HapticFeedback.impactOccurred(type); }catch(_){}
    };

    function sendResults(){
        const v = recalc();
        if(compareMode){
            const costA=v.total;
            const costB=costA; // placeholder, real compare calc TBD
            tg.sendData(JSON.stringify({source:"compare",uni_a:uniA?.id,uni_b:uniB?.id,cost_a:costA,cost_b:costB}));
        }else{
            tg.sendData(JSON.stringify({source:"calculator",annual_tuition:v.t,living_cost:v.l,other_cost:v.other,income:v.income,salary:v.salary,duration:v.d,scholarship_pct:v.sPct}));
        }
        haptic('medium');
    }

    shareBtn.addEventListener("click", sendResults);

    resetBtn.addEventListener("click", () => {
        [tuitionEl, livingEl, otherCostEl, incomeEl].forEach(el => (el.value = ""));
        scholarshipEl.value = 0;
        scholarshipVal.textContent = "0%";
        if(document.getElementById("study-years")) document.getElementById("study-years").remove();
        recalc();
    });

    // Currency formatting on blur
    document.querySelectorAll('input[type="number"]').forEach(el=>{
        el.addEventListener('blur',()=>{
            if(!el.value) return;
            const val=parseFloat(el.value); if(isNaN(val)) return;
            el.value = val;
        });
    });

    // Add haptic feedback for slider movement
    [scholarshipEl,durationEl].forEach(sl=>{
        sl.addEventListener('input',()=>{ try{ tg.HapticFeedback.selectionChanged(); }catch(_){} });
    });

    // Handle immediate prefill (no need to wait for data)
    if(prefillTuition){
        tuitionEl.value = prefillTuition;
        if(uniName){
            document.querySelector('h1').textContent = `Calculator - ${decodeURIComponent(uniName)}`;
        }
        recalc();
    }

    // Skeleton loader for compare mode
    const skeleton = document.getElementById('compare-skeleton');
    if(compareIdsParam){ skeleton.classList.remove('hidden'); }
    function hideSkeleton(){ skeleton && skeleton.classList.add('hidden'); }
    fetch("../../data/data.json").then(r=>r.json()).then(d=>{hideSkeleton(); setupCompare(d);});
});
