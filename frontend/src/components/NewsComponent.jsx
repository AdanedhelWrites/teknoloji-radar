import { useState, useEffect } from 'react'
import { 
  Container, Row, Col, Card, Button, Form, 
  Badge, Spinner, Alert, Modal 
} from 'react-bootstrap'
import { 
  FaDownload, FaSync, FaTrash, FaFileExport, 
  FaNewspaper, FaChartBar, FaCogs,
  FaSkullCrossbones, FaLaptopCode, FaShieldAlt, FaMoon, FaUserSecret
} from 'react-icons/fa'
import { newsApi } from '../services/api'

const sources = [
  { id: 'source1', name: 'The Hacker News', value: 'The Hacker News', icon: FaSkullCrossbones, color: '#e74c3c' },
  { id: 'source2', name: 'Bleeping Computer', value: 'Bleeping Computer', icon: FaLaptopCode, color: '#3498db' },
  { id: 'source3', name: 'SecurityWeek', value: 'SecurityWeek', icon: FaShieldAlt, color: '#2ecc71' },
  { id: 'source4', name: 'Dark Reading', value: 'Dark Reading', icon: FaMoon, color: '#9b59b6' },
  { id: 'source5', name: 'Krebs on Security', value: 'Krebs on Security', icon: FaUserSecret, color: '#f39c12' },
]

function NewsComponent() {
  const [news, setNews] = useState([])
  const [selectedNews, setSelectedNews] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({ total: 0, by_source: {}, last_update: null })
  const [days, setDays] = useState(7)
  const [selectedSources, setSelectedSources] = useState(
    sources.reduce((acc, s) => ({ ...acc, [s.value]: true }), {})
  )

  useEffect(() => {
    loadNews()
    loadStats()
  }, [])

  const loadNews = async () => {
    try {
      setLoading(true)
      const response = await newsApi.getNews()
      if (response.data.success) {
        setNews(response.data.data)
      }
    } catch (err) {
      setError('Siber güvenlik haberleri yüklenirken hata oluştu')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await newsApi.getStats()
      if (response.data.success) {
        setStats(response.data)
      }
    } catch (err) {
      console.error('Stats yüklenirken hata:', err)
    }
  }

  const handleFetchNews = async () => {
    const activeSources = sources
      .filter(s => selectedSources[s.value])
      .map(s => s.value)

    if (activeSources.length === 0) {
      setError('Lütfen en az bir kaynak seçin!')
      return
    }

    try {
      setFetching(true)
      setError(null)
      
      // Önce cache'i temizle
      await newsApi.clearCache()
      
      // Haberleri çek
      const response = await newsApi.fetchNews({
        days: parseInt(days),
        sources: activeSources
      })
      
      if (response.data.success) {
        setNews(response.data.data)
        loadStats()
      } else {
        setError(response.data.message)
      }
    } catch (err) {
      setError('Siber güvenlik haberleri getirilirken hata oluştu: ' + err.message)
    } finally {
      setFetching(false)
    }
  }

  const handleClearCache = async () => {
    if (!window.confirm('Tüm haberler silinecek ve sıfırlanacak. Emin misiniz?')) return
    
    try {
      await newsApi.clearCache()
      setNews([])
      setSelectedNews(null)
      loadStats()
    } catch (err) {
      setError('Sıfırlama sırasında hata oluştu')
    }
  }

  const handleExport = async () => {
    try {
      const response = await newsApi.exportNews()
      if (response.data.success) {
        const blob = new Blob([JSON.stringify(response.data.data, null, 2)], 
          { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `cybersecurity_news_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (err) {
      setError('Dışarı aktarma hatası')
    }
  }

  const toggleSource = (value) => {
    setSelectedSources(prev => ({
      ...prev,
      [value]: !prev[value]
    }))
  }

  const getSourceClass = (source) => {
    return `source-${source.toLowerCase().replace(/\s+/g, '-')}`
  }

  const getSourceIcon = (sourceName) => {
    const found = sources.find(s => s.value === sourceName)
    if (found) {
      const IconComp = found.icon
      return <IconComp className="me-1" size={12} />
    }
    return null
  }

  return (
    <Container fluid>
      <Row>
        {/* Sol Panel - Kontroller */}
        <Col md={3}>
          <Card className="mb-4">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0"><FaCogs className="me-2" />Kontroller</h5>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-4">
                <Form.Label className="fw-bold">Kaç Günlük Haber?</Form.Label>
                <Form.Range 
                  min={1} 
                  max={15} 
                  value={days} 
                  onChange={(e) => setDays(e.target.value)}
                />
                <div className="text-center">
                  <Badge bg="secondary" className="fs-6">{days} Gün</Badge>
                </div>
              </Form.Group>

              <Form.Group className="mb-4">
                <Form.Label className="fw-bold">Haber Kaynakları</Form.Label>
                {sources.map(source => {
                  const IconComp = source.icon
                  return (
                    <Form.Check 
                      key={source.id}
                      type="checkbox"
                      id={source.id}
                      checked={selectedSources[source.value]}
                      onChange={() => toggleSource(source.value)}
                      label={
                        <span className="d-flex align-items-center gap-2">
                          <IconComp style={{ color: source.color }} />
                          {source.name}
                        </span>
                      }
                    />
                  )
                })}
              </Form.Group>

              <Button 
                variant="primary" 
                className="w-100 mb-2" 
                onClick={handleFetchNews}
                disabled={fetching}
              >
                {fetching ? (
                  <><Spinner size="sm" className="me-2" />Getiriliyor...</>
                ) : (
                  <><FaDownload className="me-2" />Siber Güvenlik Haberlerini Getir</>
                )}
              </Button>
              
              <Button 
                variant="outline-secondary" 
                className="w-100 mb-2" 
                onClick={loadNews}
                disabled={loading}
              >
                <FaSync className="me-2" />Yenile
              </Button>
              
              <div className="d-flex gap-2">
                <Button 
                  variant="outline-danger" 
                  className="flex-fill" 
                  size="sm"
                  onClick={handleClearCache}
                  title="Tüm haberleri sil ve sıfırla"
                >
                  <FaTrash className="me-1" />Sıfırla
                </Button>
                
                <Button 
                  variant="outline-warning" 
                  className="flex-fill" 
                  size="sm"
                  onClick={handleExport}
                   title="Siber güvenlik haberlerini JSON olarak indir"
                >
                  <FaFileExport className="me-1" />İndir
                </Button>
              </div>
            </Card.Body>
          </Card>

          <Card className="stats-card">
            <Card.Body>
              <h5 className="card-title"><FaChartBar className="me-2" />İstatistikler</h5>
              <div className="mt-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Toplam Haber:</span>
                  <span className="fw-bold fs-5">{stats.total}</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Son Güncelleme:</span>
                  <span className="fw-bold">
                    {stats.last_update 
                      ? new Date(stats.last_update).toLocaleString('tr-TR') 
                      : '-'}
                  </span>
                </div>
                <div className="mt-3">
                  <small><strong>Kaynaklar:</strong></small><br/>
                  {Object.entries(stats.by_source).map(([source, count]) => (
                    <div key={source} className="d-flex justify-content-between mt-1">
                      <span>{source}:</span>
                      <span className="fw-bold">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Orta Panel - Haber Listesi */}
        <Col md={5}>
          <Card className="panel-card" style={{ height: 'calc(100vh - 150px)' }}>
            <Card.Header className="bg-info text-white d-flex justify-content-between align-items-center">
              <h5 className="mb-0"><FaNewspaper className="me-2" />Siber Güvenlik</h5>
              <Badge bg="light" text="dark">{news.length} haber</Badge>
            </Card.Header>
            <Card.Body className="p-0">
              {loading ? (
                <div className="text-center p-5">
                  <Spinner animation="border" />
                   <p className="mt-3">Siber güvenlik haberleri yükleniyor...</p>
                </div>
              ) : news.length === 0 ? (
                <div className="text-center p-5 text-muted">
                  <FaNewspaper size={48} className="mb-3" />
                   <p>Haber listesi boş.<br/>"Siber Güvenlik Haberlerini Getir" butonuna basın.</p>
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {news.map((item, index) => (
                    <div 
                      key={index}
                      className={`list-group-item news-item p-3 ${selectedNews === item ? 'active' : ''}`}
                      onClick={() => setSelectedNews(item)}
                    >
                      <div className="d-flex w-100 justify-content-between mb-2">
                        <span className={`source-badge ${getSourceClass(item.source)}`}>
                          {getSourceIcon(item.source)}{item.source}
                        </span>
                        <small className="text-muted">{item.date}</small>
                      </div>
                      <h6 className="mb-1 fw-bold">
                        {item.turkish_title?.length > 70 
                          ? item.turkish_title.substring(0, 70) + '...' 
                          : item.turkish_title}
                      </h6>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Sağ Panel - Haber Detayları */}
        <Col md={4}>
          <Card className="panel-card" style={{ height: 'calc(100vh - 150px)' }}>
            <Card.Header className="bg-secondary text-white">
              <h5 className="mb-0"><FaNewspaper className="me-2" />Haber Detayı</h5>
            </Card.Header>
            <Card.Body>
              {!selectedNews ? (
                <div className="text-center p-5 text-muted">
                  <FaNewspaper size={48} className="mb-3" />
                  <p>Detayları görmek için<br/>listeden bir haber seçin.</p>
                </div>
              ) : (
                <div className="fade-in">
                  <div 
                    className="p-2 text-white mb-3 rounded d-flex justify-content-between align-items-center"
                    style={{ 
                      backgroundColor: {
                        'The Hacker News': '#e74c3c',
                        'Bleeping Computer': '#3498db',
                        'SecurityWeek': '#2ecc71',
                        'Dark Reading': '#9b59b6',
                        'Krebs on Security': '#f39c12'
                      }[selectedNews.source] || '#95a5a6'
                    }}
                  >
                    <small><FaNewspaper className="me-2" />{selectedNews.source}</small>
                    <small>{selectedNews.date}</small>
                  </div>
                  
                  <h5 className="fw-bold mb-3">{selectedNews.turkish_title}</h5>
                  
                  <div className="mb-3 article-content p-3 bg-light rounded">
                    {selectedNews.turkish_description ? (
                      selectedNews.turkish_description.split('\n\n').map((paragraph, idx) => (
                        <p key={idx} className="mb-2" style={{ lineHeight: '1.7', textAlign: 'justify' }}>
                          {paragraph}
                        </p>
                      ))
                    ) : (
                      <p className="text-muted">İçerik bulunmuyor.</p>
                    )}
                  </div>
                  
                  <a 
                    href={selectedNews.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-outline-primary btn-sm"
                  >
                    <FaNewspaper className="me-2" />Orijinal Habere Git
                  </a>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Loading Modal */}
      <Modal show={fetching} backdrop="static" keyboard={false} centered>
        <Modal.Body className="text-center p-5">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <h5 className="mt-3">Siber Güvenlik Haberleri Getiriliyor...</h5>
          <p className="text-muted mb-0">Lütfen bekleyin, bu işlem biraz zaman alabilir.</p>
        </Modal.Body>
      </Modal>

      {/* Error Alert */}
      {error && (
        <Alert 
          variant="danger" 
          className="position-fixed top-0 end-0 m-3"
          style={{ zIndex: 9999, minWidth: '300px' }}
          dismissible
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}
    </Container>
  )
}

export default NewsComponent
