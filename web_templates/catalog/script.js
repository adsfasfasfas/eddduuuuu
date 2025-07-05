// Catalog mini-app logic fixed
const searchInput=document.getElementById('search');
const sortSelect=document.getElementById('sort-select');
const grid=document.getElementById('catalog-grid');
const chipRow=document.getElementById('filter-chips');
const tpl=document.getElementById('card-tpl').content;
let data=[]; let selected=[];

/* Skeleton */
const skTpl=document.getElementById('skeleton-tpl');
for(let i=0;i<8;i++){ grid.appendChild(skTpl.content.firstElementChild.cloneNode(true)); }

fetch('../../data/data.json').then(r=>r.json()).then(d=>{ data=d; buildChips(); render(); });

function buildChips(){
    // Budget chips first
    const budgets=[
        {label:'<$800',min:0,max:799},
        {label:'$800-1500',min:800,max:1500},
        {label:'>$1500',min:1501,max:Infinity}
    ];
    budgets.forEach(b=>{ const ch=document.createElement('div'); ch.className='chip budget'; ch.textContent=b.label; ch.dataset.min=b.min; ch.dataset.max=b.max===Infinity?Number.POSITIVE_INFINITY:b.max; ch.addEventListener('click',()=>{ document.querySelectorAll('.chip.budget').forEach(c=>c.classList.remove('active')); ch.classList.toggle('active'); render();}); chipRow.appendChild(ch); });

    // City chips
    const cities=[...new Set(data.map(u=>u.city).filter(Boolean))].slice(0,10);
    cities.forEach(c=>{ const chip=document.createElement('div'); chip.className='chip city'; chip.textContent=c; chip.addEventListener('click',()=>{chip.classList.toggle('active'); render();}); chipRow.appendChild(chip); });
}

function render(){
    grid.innerHTML='';

    let arr=[...data];
    const q=searchInput.value.trim().toLowerCase();
    if(q) arr=arr.filter(it=> (it.name_en||'').toLowerCase().includes(q) || (it.name_km||'').includes(q));

    // Budget filter
    const activeBudget=document.querySelector('.chip.budget.active');
    if(activeBudget){ const min=Number(activeBudget.dataset.min); const max=Number(activeBudget.dataset.max); arr=arr.filter(it=>{ const minFee=it.tuition_fees.range_min; const maxFee=it.tuition_fees.range_max||minFee; return minFee>=min && maxFee<=max;}); }

    // City filters
    const activeCities=[...document.querySelectorAll('.chip.city.active')].map(ch=>ch.textContent);
    if(activeCities.length) arr=arr.filter(it=>activeCities.includes(it.city));

    // Sorting
    switch(sortSelect.value){
        case 'tuition_asc':
            arr.sort((a,b)=>a.tuition_fees.range_min-b.tuition_fees.range_min);break;
        case 'tuition_desc':
            arr.sort((a,b)=>b.tuition_fees.range_min-a.tuition_fees.range_min);break;
        default:
            arr.sort((a,b)=>a.tuition_fees.range_min-b.tuition_fees.range_min);
    }

    // Render cards
    arr.forEach(it=>{
        const card=tpl.cloneNode(true); const root=card.querySelector('.card');
        root.querySelector('.title').textContent=it.name_short||it.name_en;
        root.querySelector('.cost').textContent=`$${it.tuition_fees.range_min.toLocaleString()} /yr`;
        root.querySelector('.tag').textContent=it.city||'';
        const img=root.querySelector('.logo');
        img.src=it.logo_url || `https://ui-avatars.com/api/?size=128&name=${encodeURIComponent(it.name_short||it.name_en)}`;
        const btn=root.querySelector('.select-btn');
        if(selected.includes(it.id)) btn.classList.add('selected');
        btn.addEventListener('click',()=>toggleSelect(it.id,btn));
        grid.appendChild(card);
    });
}

function toggleSelect(id,btn){
    if(selected.includes(id)){ selected=selected.filter(x=>x!==id); btn.classList.remove('selected'); }
    else if(selected.length<2){ selected.push(id); btn.classList.add('selected'); }
}

searchInput.addEventListener('input',render);
sortSelect.addEventListener('change',render); 