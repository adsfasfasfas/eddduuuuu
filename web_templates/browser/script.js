document.addEventListener('DOMContentLoaded', () => {
    let tgWebApp;
    try {
        tgWebApp = window.Telegram.WebApp;
        tgWebApp.ready();
        tgWebApp.expand();
    } catch (e) {
        console.warn("Telegram WebApp script not found. Running in local test mode.");
        tgWebApp = { sendData: (data) => console.log("Local Test:", data) };
    }

    let allUniversities = [];
    const universityGrid = document.getElementById('university-grid');
    const loadingState = document.getElementById('loading-state');
    const noResultsDiv = document.getElementById('no-results');
    const searchInput = document.getElementById('search-input');
    const selectWrappers = document.querySelectorAll('.custom-select-wrapper');
    const headerEl = document.querySelector('.app-header');
    const filterHeader = document.querySelector('.filter-header');
    const sortSelect = document.getElementById('sort-select');
    const favoritesOnlyCheckbox = document.getElementById('favorites-only');

    let currentFilters = { search: '', location: '', budget: '', major: '' };
    let currentSort = '';
    let favorites = JSON.parse(localStorage.getItem('university_favorites') || '[]');

    const headerHeight=headerEl?headerEl.offsetHeight:60;
    document.documentElement.style.setProperty('--header-height',headerHeight+'px');

    const renderUniversities = (universities) => {
        universityGrid.innerHTML = '';
        noResultsDiv.style.display = universities.length === 0 ? 'block' : 'none';

        universities.forEach(uni => {
            const card = document.createElement('div');
            card.className = 'university-card';
            card.dataset.id = uni.id;

            const isFavorite = favorites.includes(uni.id);
            const favoriteIcon = isFavorite ? '❤️' : '🤍';

            card.innerHTML = `
                <div class="card-header">
                    <h3>${uni.name_km}</h3>
                    <button class="favorite-btn" data-id="${uni.id}" title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                        ${favoriteIcon}
                    </button>
                </div>
                <p class="en-name">${uni.name_en}</p>
                <div class="info-chip location-chip">${uni.location}</div>
                <div class="info-chip budget-chip">$${uni.tuition_fees.range_min} - $${uni.tuition_fees.range_max}</div>
                ${uni.ranking_score ? `<div class="info-chip ranking-chip">⭐️ ${uni.ranking_score}</div>` : ''}
                <div class="majors">${(uni.major_categories_km || []).slice(0,3).join(' | ')}</div>
            `;
            universityGrid.appendChild(card);
        });
    };

    const applyFilters = () => {
        let filtered = allUniversities.filter(uni => {
            const searchText = currentFilters.search;
            const nameMatch = searchText === '' ||
                uni.name_km.toLowerCase().includes(searchText) ||
                uni.name_en.toLowerCase().includes(searchText) ||
                uni.name_short.toLowerCase().includes(searchText);
            const locationMatch = currentFilters.location === '' || uni.location === currentFilters.location;
            const majorMatch = currentFilters.major === '' || (uni.faculties && uni.faculties.some(f => f.majors && f.majors.some(m => m.category_km === currentFilters.major)));
            const favoritesMatch = !favoritesOnlyCheckbox.checked || favorites.includes(uni.id);

            let budgetMatch = true;
            if (currentFilters.budget !== '') {
                const maxBudget = parseInt(currentFilters.budget);
                if (maxBudget === 99999) {
                    budgetMatch = uni.tuition_fees.range_min > 1500;
                } else {
                    budgetMatch = uni.tuition_fees.range_max <= maxBudget;
                }
            }
            return nameMatch && locationMatch && budgetMatch && majorMatch && favoritesMatch;
        });

        if (currentSort === 'tuition_asc') {
            filtered.sort((a,b)=>a.tuition_fees.range_min - b.tuition_fees.range_min);
        } else if (currentSort==='tuition_desc') {
            filtered.sort((a,b)=>b.tuition_fees.range_max - a.tuition_fees.range_max);
        } else if (currentSort==='ranking_desc') {
            filtered.sort((a,b)=>(b.ranking_score||0)-(a.ranking_score||0));
        } else if (currentSort==='name_asc') {
            filtered.sort((a,b)=>a.name_en.localeCompare(b.name_en));
        }

        renderUniversities(filtered);
    };

    const populateCustomSelect = (filterName, options, defaultText) => {
        const wrapper = document.querySelector(`.custom-options[data-filter="${filterName}"]`);
        wrapper.innerHTML = "";
        const defaultOption = document.createElement('div');
        defaultOption.className = 'custom-option selected';
        defaultOption.textContent = defaultText;
        defaultOption.dataset.value = '';
        wrapper.appendChild(defaultOption);

        options.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'custom-option';
            optionEl.textContent = option;
            optionEl.dataset.value = option;
            wrapper.appendChild(optionEl);
        });
    };

    fetch('../../data/data.json')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            allUniversities = data;
            const locations = [...new Set(data.map(uni => uni.location))].sort();
            const majorCategories = [...new Set(
                data.flatMap(uni => uni.faculties?.flatMap(f => f.majors?.map(m => m.category_km) || []) || [])
            )].filter(Boolean).sort();

            populateCustomSelect("location", locations, "គ្រប់ទីតាំង");
            populateCustomSelect("major", majorCategories, "គ្រប់ជំនាញ");

            loadingState.style.display = 'none';
            universityGrid.classList.remove('hidden');
            renderUniversities(allUniversities);
        })
        .catch(error => {
            console.error("Fetch error:", error);
            loadingState.innerHTML = `<p style="color: red;">Error loading data. ${error.message}</p>`;
        });

    searchInput.addEventListener('input', () => {
        currentFilters.search = searchInput.value.toLowerCase();
        applyFilters();
    });

    selectWrappers.forEach(wrapper => {
        const trigger = wrapper.querySelector('.custom-select-trigger');
        const optionsContainer = wrapper.querySelector('.custom-options');
        trigger.addEventListener('click', () => {
            selectWrappers.forEach(other => { if (other !== wrapper) other.classList.remove('open'); });
            wrapper.classList.toggle('open');
        });
        optionsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains("custom-option")) {
                const filterName = trigger.dataset.filter;
                currentFilters[filterName] = e.target.dataset.value;
                trigger.textContent = e.target.textContent;
                wrapper.querySelectorAll('.custom-option').forEach(opt => opt.classList.remove('selected'));
                e.target.classList.add('selected');
                wrapper.classList.remove('open');
                applyFilters();
            }
        });
    });

    window.addEventListener('click', (e) => {
        if (!e.target.closest('.custom-select-wrapper')) {
            selectWrappers.forEach(w => w.classList.remove('open'));
        }
    });

    // Handle favorites and card clicks
    universityGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('favorite-btn')) {
            e.stopPropagation();
            const uniId = parseInt(e.target.dataset.id);
            toggleFavorite(uniId);
            return;
        }

        const card = e.target.closest('.university-card');
        if (card && card.dataset.id) {
            tgWebApp.sendData(JSON.stringify({ source: 'catalog', university_id: parseInt(card.dataset.id) }));
        }
    });

    function toggleFavorite(uniId) {
        const index = favorites.indexOf(uniId);
        if (index > -1) {
            favorites.splice(index, 1);
        } else {
            favorites.push(uniId);
        }
        localStorage.setItem('university_favorites', JSON.stringify(favorites));
        // Re-apply all current filters including the updated favorites
        applyFilters();
    }

    sortSelect.addEventListener('change', ()=>{
        currentSort = sortSelect.value;
        applyFilters();
    });

    favoritesOnlyCheckbox.addEventListener('change', applyFilters);
});
