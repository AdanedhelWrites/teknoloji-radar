        // Task durumunu kontrol et
        async function checkTaskStatus(taskId) {
            try {
                const response = await fetch(`/api/task-status/${taskId}/`);
                if (!response.ok) {
                    console.log('Task status endpoint not available, waiting...');
                    return null;
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Task status error:', error);
                return null;
            }
        }
        
        // Haber çekme işlemini kontrol et (basit polling)
        async function waitForNews(maxAttempts = 30) {
            let attempts = 0;
            while (attempts < maxAttempts) {
                // Her 3 saniyede bir veritabanını kontrol et
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                const response = await fetch('/api/news/');
                const data = await response.json();
                
                if (data.success && data.count > 0) {
                    // Haberler geldi!
                    currentNews = data.data;
                    renderNewsList();
                    updateStats();
                    return true;
                }
                
                attempts++;
                console.log(`Waiting for news... attempt ${attempts}`);
            }
            return false;
        }
        
        fetchBtn.addEventListener('click', async () => {
            const days = parseInt(daysRange.value);
            const sources = getSelectedSources();
            
            if (sources.length === 0) {
                showToast('Lutfen en az bir kaynak secin!', 'warning');
                return;
            }
            
            loadingModal.show();
            
            try {
                // 1. Önce veritabanını temizle
                console.log('Clearing database...');
                const clearResponse = await fetch('/api/clear/', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken() 
                    }
                });
                const clearData = await clearResponse.json();
                console.log('Clear response:', clearData);
                
                // Listeyi temizle
                currentNews = [];
                renderNewsList();
                updateStats();
                
                // 2. Haber çekme task'ını başlat
                console.log('Starting fetch task...');
                const response = await fetch('/api/fetch/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ days: days, sources: sources })
                });
                
                const data = await response.json();
                console.log('Fetch response:', data);
                
                if (data.success) {
                    showToast('Haberler cekiliyor, lutfen bekleyin...');
                    
                    // 3. Haberler gelene kadar bekle (polling)
                    const success = await waitForNews();
                    
                    if (success) {
                        showToast(`${currentNews.length} haber basariyla yuklendi!`);
                    } else {
                        showToast('Haberler yuklenirken zaman asimi olustu. Lutfen tekrar deneyin.', 'warning');
                    }
                } else {
                    showToast(data.message, 'danger');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('Hata: ' + error.message, 'danger');
            } finally {
                loadingModal.hide();
            }
        });
        
        // Veritabanindan haberleri yükle
        async function loadNewsFromDatabase() {
            const response = await fetch('/api/news/');
            const data = await response.json();
            
            if (data.success && data.count > 0) {
                currentNews = data.data;
                renderNewsList();
                updateStats();
            }
        }