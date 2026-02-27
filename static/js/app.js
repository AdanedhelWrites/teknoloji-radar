/**
 * Cybersecurity News Scraper - Web App JavaScript
 */

let currentNews = [];
let selectedNewsIndex = null;

// DOM Elements
const daysRange = document.getElementById('daysRange');
const daysValue = document.getElementById('daysValue');
const fetchBtn = document.getElementById('fetchBtn');
const loadBtn = document.getElementById('loadBtn');
const clearBtn = document.getElementById('clearBtn');
const exportBtn = document.getElementById('exportBtn');
const newsList = document.getElementById('newsList');
const detailPanel = document.getElementById('detailPanel');
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');

// Gun slider event
daysRange.addEventListener('input', (e) => {
    daysValue.textContent = e.target.value + ' Gun';
});

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Get selected sources
function getSelectedSources() {
    const checkboxes = document.querySelectorAll('.form-check-input:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Fetch news
fetchBtn.addEventListener('click', async () => {
    const days = parseInt(daysRange.value);
    const sources = getSelectedSources();
    
    if (sources.length === 0) {
        showToast('Lutfen en az bir kaynak secin!', 'warning');
        return;
    }
    
    loadingModal.show();
    progressBar.style.width = '10%';
    progressText.textContent = 'Kaynaklara baglaniliyor...';
    
    try {
        const response = await fetch('/api/fetch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                days: days,
                sources: sources
            })
        });
        
        progressBar.style.width = '50%';
        progressText.textContent = 'Haberler cevriliyor...';
        
        const data = await response.json();
        
        progressBar.style.width = '100%';
        progressText.textContent = 'Tamamlandi!';
        
        if (data.success) {
            currentNews = data.data;
            renderNewsList();
            updateStats();
            showToast(`${data.count} haber basariyla cekildi!`);
        } else {
            showToast(data.message, 'warning');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'danger');
    } finally {
        setTimeout(() => {
            loadingModal.hide();
            progressBar.style.width = '0%';
        }, 500);
    }
});

// Load from cache
loadBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/news');
        const data = await response.json();
        
        if (data.success && data.count > 0) {
            currentNews = data.data;
            renderNewsList();
            updateStats();
            showToast(`${data.count} haber cache'den yuklendi`);
        } else {
            showToast('Cache bos. Once haberleri cekin.', 'warning');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'danger');
    }
});

// Clear cache
clearBtn.addEventListener('click', async () => {
    if (!confirm('Cache temizlensin mi?')) return;
    
    try {
        const response = await fetch('/api/clear', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            currentNews = [];
            renderNewsList();
            updateStats();
            detailPanel.innerHTML = `
                <div class="text-center p-5 text-muted">
                    <i class="fas fa-hand-pointer fa-3x mb-3"></i>
                    <p>Detaylari gormek icin<br>listeden bir haber secin.</p>
                </div>
            `;
            showToast('Cache basariyla temizlendi');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'danger');
    }
});

// Export news
exportBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/export');
        const data = await response.json();
        
        if (data.success) {
            const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cybersecurity_news_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('Haberler disari aktarildi');
        }
    } catch (error) {
        showToast('Hata: ' + error.message, 'danger');
    }
});

// Render news list
function renderNewsList() {
    if (currentNews.length === 0) {
        newsList.innerHTML = `
            <div class="text-center p-5 text-muted">
                <i class="fas fa-newspaper fa-3x mb-3"></i>
                <p>Haber listesi bos.<br>"Haberleri Cek" butonuna basin.</p>
            </div>
        `;
        document.getElementById('newsCount').textContent = '0 haber';
        return;
    }
    
    let html = '<div class="list-group list-group-flush">';
    
    currentNews.forEach((news, index) => {
        const sourceClass = 'source-' + news.source.toLowerCase().replace(/\s+/g, '-');
        const title = news.turkish_title.length > 70 
            ? news.turkish_title.substring(0, 70) + '...' 
            : news.turkish_title;
        
        html += `
            <div class="list-group-item news-item p-3 ${index === selectedNewsIndex ? 'active' : ''}" 
                 data-index="${index}" onclick="selectNews(${index})">
                <div class="d-flex w-100 justify-content-between mb-2">
                    <span class="source-badge ${sourceClass}">${news.source}</span>
                    <small class="text-muted">${news.date}</small>
                </div>
                <h6 class="mb-1 fw-bold">${title}</h6>
                <p class="mb-1 text-muted small">${news.turkish_summary ? news.turkish_summary.substring(0, 100) + '...' : ''}</p>
            </div>
        `;
    });
    
    html += '</div>';
    newsList.innerHTML = html;
    document.getElementById('newsCount').textContent = `${currentNews.length} haber`;
}

// Select news
function selectNews(index) {
    selectedNewsIndex = index;
    const news = currentNews[index];
    
    // Update active state
    document.querySelectorAll('.news-item').forEach((item, i) => {
        if (i === index) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Source color mapping
    const sourceColors = {
        'The Hacker News': '#e74c3c',
        'Bleeping Computer': '#3498db',
        'SecurityWeek': '#2ecc71',
        'Dark Reading': '#9b59b6',
        'Krebs on Security': '#f39c12'
    };
    
    const sourceColor = sourceColors[news.source] || '#95a5a6';
    
    detailPanel.innerHTML = `
        <div class="fade-in">
            <div class="p-3 text-white mb-3" style="background-color: ${sourceColor}; border-radius: 10px;">
                <small><i class="fas fa-newspaper me-2"></i>${news.source}</small>
            </div>
            
            <h4 class="fw-bold mb-3">${news.turkish_title}</h4>
            
            <div class="mb-3">
                <span class="badge bg-light text-dark border me-2">
                    <i class="far fa-calendar-alt me-1"></i>${news.date}
                </span>
                <span class="badge bg-light text-dark border">
                    <i class="far fa-clock me-1"></i>${news.original_date}
                </span>
            </div>
            
            <div class="mb-4">
                <h6 class="fw-bold text-primary">
                    <i class="fas fa-align-left me-2"></i>Ozet
                </h6>
                <div class="p-3 bg-light rounded">
                    ${news.turkish_summary || 'Ozet bulunmuyor.'}
                </div>
            </div>
            
            <div class="mb-4">
                <h6 class="fw-bold text-primary">
                    <i class="fas fa-align-justify me-2"></i>Detayli Aciklama
                </h6>
                <div class="p-3 bg-light rounded">
                    ${news.turkish_description || 'Aciklama bulunmuyor.'}
                </div>
            </div>
            
            <div class="mb-3">
                <h6 class="fw-bold text-primary">
                    <i class="fas fa-globe me-2"></i>Link
                </h6>
                <a href="${news.link}" target="_blank" class="btn btn-outline-primary btn-sm">
                    <i class="fas fa-external-link-alt me-2"></i>Orijinal Habere Git
                </a>
            </div>
            
            <hr>
            
            <div class="text-muted small">
                <strong>Orijinal Baslik:</strong><br>
                ${news.original_title}
            </div>
        </div>
    `;
}

// Update stats
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalNews').textContent = data.total;
            document.getElementById('lastUpdate').textContent = data.last_update 
                ? new Date(data.last_update).toLocaleString('tr-TR') 
                : '-';
            
            // Source stats
            let statsHtml = '<small><strong>Kaynak Dagilimi:</strong></small><br>';
            for (const [source, count] of Object.entries(data.by_source)) {
                statsHtml += `<div class="d-flex justify-content-between mt-1">
                    <span>${source}:</span>
                    <span class="fw-bold">${count}</span>
                </div>`;
            }
            document.getElementById('sourceStats').innerHTML = statsHtml;
        }
    } catch (error) {
        console.error('Stats error:', error);
    }
}

// Load initial stats
updateStats();

// Auto-load cached news on startup
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/news');
        const data = await response.json();
        
        if (data.success && data.count > 0) {
            currentNews = data.data;
            renderNewsList();
            updateStats();
        }
    } catch (error) {
        console.log('No cached data on startup');
    }
});
