import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { Navbar, Nav, Container } from 'react-bootstrap'
import { FaNewspaper, FaShieldAlt, FaHome, FaDharmachakra, FaSun, FaMoon, FaTree, FaServer } from 'react-icons/fa'
import NewsComponent from './components/NewsComponent'
import CVEComponent from './components/CVEComponent'
import KubernetesComponent from './components/KubernetesComponent'
import SREComponent from './components/SREComponent'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
    document.body.setAttribute('data-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  return (
    <div className={`App ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand href="/">
            <FaTree className="me-2" />
            Güncel Teknoloji Haberleri
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={NavLink} to="/" end>
                <FaHome className="me-1" /> Ana Sayfa
              </Nav.Link>
              <Nav.Link as={NavLink} to="/news">
                <FaNewspaper className="me-1" /> Siber Güvenlik
              </Nav.Link>
              <Nav.Link as={NavLink} to="/cve">
                <FaShieldAlt className="me-1" /> CVE
              </Nav.Link>
              <Nav.Link as={NavLink} to="/k8s">
                <FaDharmachakra className="me-1" /> Kubernetes
              </Nav.Link>
              <Nav.Link as={NavLink} to="/sre">
                <FaServer className="me-1" /> SRE
              </Nav.Link>
            </Nav>
            <button
              className="theme-toggle-icon"
              onClick={() => setDarkMode(!darkMode)}
              title={darkMode ? 'Aydınlık Mod' : 'Karanlık Mod'}
              aria-label={darkMode ? 'Aydınlık Mod' : 'Karanlık Mod'}
            >
              {darkMode ? <FaSun /> : <FaMoon />}
            </button>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid className="px-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/news" element={<NewsComponent />} />
          <Route path="/cve" element={<CVEComponent />} />
          <Route path="/k8s" element={<KubernetesComponent />} />
          <Route path="/sre" element={<SREComponent />} />
        </Routes>
      </Container>
    </div>
  )
}

function HomePage() {
  return (
    <div className="text-center py-5">
      <h1 className="display-4 mb-4">Güncel Teknoloji Haberleri</h1>
      <p className="lead mb-5">
        Güncel siber güvenlik haberleri, CVE (Common Vulnerabilities and Exposures), 
        Kubernetes ve SRE (Site Reliability Engineering) güncellemelerini tek bir yerden takip edin.
      </p>
      
      <div className="row justify-content-center">
        <div className="col-md-3 mb-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <FaNewspaper size={48} className="text-primary mb-3" />
              <h5 className="card-title">Siber Güvenlik</h5>
              <p className="card-text">
                The Hacker News, Bleeping Computer, SecurityWeek ve daha fazlasından 
                güncel siber güvenlik haberlerini takip edin.
              </p>
              <NavLink to="/news" className="btn btn-primary">
                Siber Güvenlik Görüntüle
              </NavLink>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <FaShieldAlt size={48} className="text-danger mb-3" />
              <h5 className="card-title">CVE</h5>
              <p className="card-text">
                NVD, GitHub Advisory, Tenable gibi kaynaklardan son güvenlik 
                açıklarını takip edin ve Türkçe açıklamaları okuyun.
              </p>
              <NavLink to="/cve" className="btn btn-danger">
                CVE Görüntüle
              </NavLink>
            </div>
          </div>
        </div>

        <div className="col-md-3 mb-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <FaDharmachakra size={48} className="text-info mb-3" />
              <h5 className="card-title">Kubernetes</h5>
              <p className="card-text">
                Kubernetes Blog, GitHub Releases ve CNCF Blog'dan 
                güncel Kubernetes haberlerini ve sürüm bilgilerini takip edin.
              </p>
              <NavLink to="/k8s" className="btn btn-info text-white">
                Kubernetes Haberleri
              </NavLink>
            </div>
          </div>
        </div>

        <div className="col-md-3 mb-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <FaServer size={48} className="text-success mb-3" />
              <h5 className="card-title">SRE</h5>
              <p className="card-text">
                SRE Weekly ve InfoQ SRE'den güncel Site Reliability Engineering 
                haberlerini ve en iyi uygulamaları takip edin.
              </p>
              <NavLink to="/sre" className="btn btn-success">
                SRE Haberleri
              </NavLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
