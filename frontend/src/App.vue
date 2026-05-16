<script setup>
import { computed, onMounted, ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import {
  DEFAULT_CATEGORIES,
  DEFAULT_DOCUMENTS,
  DEFAULT_FLOORS,
  DEFAULT_PHASES,
  DEFAULT_PROJECT,
  LOCAL_IMAGES,
  resolveApiUrl,
  resolveImage,
} from './config/defaults.js'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const CONTACT_PHONES = [
  { display: '8850382276', tel: '+918850382276' },
  { display: '9372899982', tel: '+919372899982' },
]
const CONTACT_EMAIL = 'info@malkarenterprises.com'

const SOCIAL_LINKS = [
  { label: 'WhatsApp', href: 'https://wa.me/919372899982', icon: 'whatsapp' },
  { label: 'Call us', href: 'tel:+918850382276', icon: 'phone' },
  { label: 'Email', href: `mailto:${CONTACT_EMAIL}`, icon: 'mail' },
]

const mobileMenuOpen = ref(false)

const projects = ref([])
const selectedProjectId = ref(1)
const isLoading = ref(true)
const activeNav = ref('dashboard')
const activeTab = ref('overview')
const activePhase = ref('structure')
const selectedDocUrl = ref('')
const enquiry = ref({ name: '', mobile: '', email: '', message: '' })
const enquiryStatus = ref('')
const enquirySubmitOk = ref(false)
const apiError = ref('')

const sidebarLinks = [
  { id: 'dashboard', label: 'Dashboard', icon: 'grid', section: 'dashboard' },
  { id: 'projects', label: 'Projects', icon: 'building', section: 'projects' },
  { id: 'documents', label: 'Plans & PDFs', icon: 'file', section: 'documents' },
  { id: 'progress', label: 'Construction Progress', icon: 'chart', section: 'progress' },
  { id: 'analytics', label: 'Area Analytics', icon: 'analytics', section: 'overview' },
  { id: 'enquiries', label: 'Enquiries', icon: 'mail', section: 'enquiry' },
  { id: 'about', label: 'About Us', icon: 'info', section: 'about' },
  { id: 'contact', label: 'Contact Us', icon: 'phone', section: 'contact' },
]

const headerLinks = [
  { label: 'Home', section: 'dashboard' },
  { label: 'Projects', section: 'projects' },
  { label: 'About Us', section: 'about' },
  { label: 'Why Us', section: 'about' },
  { label: 'Contact', section: 'contact' },
]

const overviewTabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'documents', label: 'Plans & PDFs' },
  { id: 'amenities', label: 'Amenities' },
  { id: 'location', label: 'Location' },
]

const heroStats = [
  { icon: 'award', value: '10+', label: 'Years of Excellence' },
  { icon: 'building', value: '20+', label: 'Projects Delivered' },
  { icon: 'users', value: '500+', label: 'Happy Clients' },
  { icon: 'area', value: '5M+', label: 'Sq Ft Developed' },
  { icon: 'shield', value: '100%', label: 'Commitment to Quality' },
]

const activeProject = computed(() => {
  const api = projects.value.find((p) => p.id === selectedProjectId.value) || projects.value[0] || {}
  return {
    ...DEFAULT_PROJECT,
    ...api,
    categories: api.categories?.length ? api.categories : DEFAULT_CATEGORIES,
    construction_phases: api.construction_phases?.length ? api.construction_phases : DEFAULT_PHASES,
    floor_list: api.floor_list?.length ? api.floor_list : DEFAULT_FLOORS,
    parking: api.parking || DEFAULT_PROJECT.parking,
    launch_date: api.launch_date || DEFAULT_PROJECT.launch_date,
    possession_date: api.possession_date || DEFAULT_PROJECT.possession_date,
    floor_plans: api.floor_plans || {},
  }
})

const projectCount = computed(() => Math.max(projects.value.length, 1))
const hasUploadedDocs = computed(() => documents.value.length > 0)
const docsLoadFailed = computed(() => Boolean(apiError.value) && !hasUploadedDocs.value)

const projectImages = computed(() => {
  const api = activeProject.value?.images || {}
  return {
    hero: resolveImage(api.hero, LOCAL_IMAGES.hero),
    cover: resolveImage(api.cover, LOCAL_IMAGES.cover),
    thumbnail: resolveImage(api.thumbnail, LOCAL_IMAGES.thumbnail),
    construction: resolveImage(api.construction, LOCAL_IMAGES.construction),
  }
})

const categories = computed(() => {
  const api = activeProject.value?.categories
  if (!api?.length) return DEFAULT_CATEGORIES
  return api.map((cat, i) => ({
    ...cat,
    image: resolveImage(cat.image, DEFAULT_CATEGORIES[i % DEFAULT_CATEGORIES.length].image),
  }))
})

const phases = computed(() => {
  const api = activeProject.value?.construction_phases
  return api?.length ? api : DEFAULT_PHASES
})

const floors = computed(() => {
  const api = activeProject.value?.floor_list
  return api?.length ? api : DEFAULT_FLOORS
})

const documents = computed(() => {
  const apiDocs = activeProject.value?.documents || []
  const normalized = apiDocs.map((doc) => ({
    ...doc,
    url: resolveApiUrl(doc.url, API),
  }))
  if (normalized.length) return normalized
  return DEFAULT_DOCUMENTS.map((doc) => ({
    ...doc,
    url: resolveApiUrl(doc.url, API),
  }))
})
const maps = computed(() => activeProject.value?.maps || [])

const displayName = computed(() => activeProject.value.display_name)
const projectProgress = computed(() => Math.min(100, activeProject.value.progress ?? 10))
const projectStatusLabel = computed(() => (activeProject.value.status || 'ongoing').toUpperCase())

const selectedDocument = computed(() => {
  if (!documents.value.length) return null
  return documents.value.find((d) => d.url === selectedDocUrl.value) || documents.value[0]
})

function selectDocument(doc) {
  selectedDocUrl.value = doc.url
  scrollTo('documents')
}

function selectProject(project) {
  selectedProjectId.value = project.id
  syncSelectedDocument()
  scrollTo('overview')
}

function onImgError(event, fallback) {
  const el = event.target
  if (el.dataset.fallbackApplied) return
  el.dataset.fallbackApplied = '1'
  el.src = fallback
}

const docLabels = {
  'kala-chowki-draft-plans': 'Approved Municipal Plans',
  'kala-chowki-gallery': 'Project Gallery Booklet',
  'kala-chowki-municipal-1': 'Municipal Drawing Set',
}

function docTitle(doc) {
  const raw = doc.name || docLabels[doc.id] || 'Project document'
  return raw.length > 72 ? `${raw.slice(0, 70)}…` : raw
}

function docSubtitle(doc) {
  if (doc.id?.includes('draft') || doc.name?.toLowerCase().includes('draft')) return 'Municipal drawing · FSI plans'
  if (doc.id?.includes('gallery') || doc.name?.toLowerCase().includes('gallery')) return 'Project gallery booklet'
  if (doc.name?.toLowerCase().includes('municipal')) return 'Approved municipal set'
  return 'Project PDF'
}

function formatArea(v) {
  return Math.round(v || 339791).toLocaleString('en-IN')
}

function scrollTo(section) {
  mobileMenuOpen.value = false
  activeNav.value = sidebarLinks.find((l) => l.section === section)?.id || 'dashboard'
  document.getElementById(section)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

async function loadProjects() {
  isLoading.value = true
  apiError.value = ''
  try {
    const res = await fetch(`${API}/projects`)
    if (!res.ok) throw new Error('Failed to load')
    projects.value = await res.json()
    if (projects.value.length && !projects.value.find((p) => p.id === selectedProjectId.value)) {
      selectedProjectId.value = projects.value[0].id
    }
    syncSelectedDocument()
  } catch {
    projects.value = [{ ...DEFAULT_PROJECT }]
    apiError.value = ''
    syncSelectedDocument()
  } finally {
    isLoading.value = false
  }
}

function syncSelectedDocument() {
  const docs = documents.value
  if (!docs.length) {
    selectedDocUrl.value = ''
    return
  }
  if (!docs.some((d) => d.url === selectedDocUrl.value)) {
    selectedDocUrl.value = docs[0].url
  }
}

async function submitEnquiry() {
  enquiryStatus.value = ''
  enquirySubmitOk.value = false
  try {
    const res = await fetch(`${API}/enquiries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(enquiry.value),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const detail = data.detail
      const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join(', ') : detail
      throw new Error(msg || 'Could not submit enquiry')
    }
    enquirySubmitOk.value = true
    enquiryStatus.value = data.message || 'Submitted successfully.'
    enquiry.value = { name: '', mobile: '', email: '', message: '' }
  } catch (err) {
    enquiryStatus.value =
      err instanceof Error && err.message
        ? err.message
        : 'Could not submit right now. Please call us or try again later.'
  }
}

onMounted(loadProjects)
</script>

<template>
  <div class="dashboard">
    <div
      v-if="mobileMenuOpen"
      class="sidebar-backdrop"
      aria-hidden="true"
      @click="mobileMenuOpen = false"
    />

    <aside class="sidebar" :class="{ open: mobileMenuOpen }">
      <a class="sidebar-brand" href="#" @click.prevent="scrollTo('dashboard')">
        <span class="brand-mark">M</span>
        <span class="brand-copy">
          <strong>Malkar</strong>
          <small>Enterprises</small>
        </span>
      </a>

      <nav class="sidebar-nav">
        <button
          v-for="link in sidebarLinks"
          :key="link.id"
          type="button"
          class="sidebar-link"
          :class="{ active: activeNav === link.id }"
          @click="scrollTo(link.section); activeNav = link.id"
        >
          <AppIcon :name="link.icon" :size="18" class="link-icon" />
          {{ link.label }}
        </button>
      </nav>

      <div class="sidebar-footer">
        <p class="sidebar-contact">
          <span>Enquiries</span>
          <a :href="CONTACT_PHONES[0].tel">{{ CONTACT_PHONES[0].display }}</a>
          <span class="phone-sep"> / </span>
          <a :href="CONTACT_PHONES[1].tel">{{ CONTACT_PHONES[1].display }}</a>
        </p>
        <div class="social-row">
          <a
            v-for="s in SOCIAL_LINKS"
            :key="s.label"
            :href="s.href"
            :aria-label="s.label"
            :target="s.href.startsWith('http') ? '_blank' : undefined"
            :rel="s.href.startsWith('http') ? 'noopener noreferrer' : undefined"
          >
            <AppIcon :name="s.icon" :size="14" />
          </a>
        </div>
        <p class="copyright">© 2026 Malkar Enterprises</p>
      </div>
    </aside>

    <!-- Main -->
    <div class="main">
      <header class="top-header">
        <div class="header-left">
          <button
            type="button"
            class="menu-toggle"
            :aria-expanded="mobileMenuOpen"
            aria-label="Open menu"
            @click="toggleMobileMenu"
          >
            <AppIcon :name="mobileMenuOpen ? 'close' : 'menu'" :size="22" />
          </button>
          <nav class="header-nav">
            <button
              v-for="link in headerLinks"
              :key="link.label"
              type="button"
              class="header-link"
              @click="scrollTo(link.section)"
            >
              {{ link.label }}
            </button>
          </nav>
        </div>
        <div class="header-phones">
          <a
            v-for="p in CONTACT_PHONES"
            :key="p.tel"
            class="header-phone"
            :href="p.tel"
          >
            <AppIcon name="phone" :size="14" />
            <span>{{ p.display }}</span>
          </a>
        </div>
      </header>

      <div class="content">
        <!-- Hero -->
        <section id="dashboard" class="hero-row">
          <div class="hero-banner card">
            <img
              :src="projectImages.hero"
              alt="Malkar commercial landmark"
              class="hero-bg"
              @error="onImgError($event, LOCAL_IMAGES.hero)"
            />
            <div class="hero-overlay"></div>
            <div class="hero-content">
              <span class="eyebrow">Builders & Developers</span>
              <h1 class="hero-title">
                Crafting Spaces.<br />
                <em>Building Trust.</em>
              </h1>
              <p class="hero-desc">
                Delivering landmark commercial destinations with engineering precision and transparent delivery.
              </p>
              <div class="hero-btns">
                <button type="button" class="btn-gold" @click="scrollTo('projects')">Explore Projects</button>
                <button type="button" class="btn-outline" @click="scrollTo('about')">View Company Profile</button>
              </div>
            </div>
          </div>

          <div class="featured-card card">
            <span class="card-label">Featured Project</span>
            <h3>{{ displayName }}</h3>
            <p class="loc">
              <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 2a7 7 0 00-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 00-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z"/></svg>
              {{ activeProject?.location }}
            </p>
            <div class="featured-img-wrap">
              <img
                :src="projectImages.thumbnail"
                :alt="displayName"
                @error="onImgError($event, LOCAL_IMAGES.thumbnail)"
              />
              <span class="badge-ongoing">{{ projectStatusLabel }}</span>
            </div>
            <div class="featured-stats">
              <div><span>Total Area</span><strong>{{ formatArea(activeProject?.total_area_sqft) }} Sq Ft</strong></div>
              <div><span>Floors</span><strong>{{ activeProject?.floors || 7 }} + Basement</strong></div>
            </div>
            <button type="button" class="link-gold" @click="scrollTo('overview')">View Project →</button>
          </div>
        </section>

        <!-- All projects (multi-project switcher) -->
        <section v-if="projects.length > 1" class="card panel project-picker" id="all-projects">
          <div class="panel-head">
            <div>
              <span class="eyebrow">Portfolio</span>
              <h2>All Projects ({{ projectCount }})</h2>
              <p class="subtitle">Select a project to view its plans and documents.</p>
            </div>
          </div>
          <div class="project-cards-row">
            <button
              v-for="p in projects"
              :key="p.id"
              type="button"
              class="project-pick-card"
              :class="{ active: selectedProjectId === p.id }"
              @click="selectProject(p)"
            >
              <img :src="resolveImage(p.images?.thumbnail, LOCAL_IMAGES.thumbnail)" :alt="p.display_name" />
              <div class="project-pick-body">
                <span class="pick-status">{{ (p.status || 'ongoing').toUpperCase() }}</span>
                <strong>{{ p.display_name }}</strong>
                <small>{{ p.location }}</small>
                <span class="pick-progress">{{ p.progress ?? 10 }}% complete</span>
              </div>
            </button>
          </div>
        </section>

        <!-- Stats bar -->
        <section class="stats-bar card">
          <div v-for="stat in heroStats" :key="stat.label" class="stat-item">
            <AppIcon :name="stat.icon" :size="20" class="stat-icon" />
            <div>
              <strong>{{ stat.value }}</strong>
              <span>{{ stat.label }}</span>
            </div>
          </div>
        </section>

        <!-- Projects + Progress -->
        <section class="grid-2" id="projects">
          <div class="card panel">
            <div class="panel-head">
              <div>
                <span class="eyebrow">Our Projects</span>
                <h2>Spaces That Inspire Success</h2>
              </div>
              <button type="button" class="btn-sm" @click="scrollTo('overview')">View All →</button>
            </div>
            <div class="category-grid">
              <article v-for="cat in categories" :key="cat.title" class="category-card">
                <img
                  :src="cat.image"
                  :alt="cat.title"
                  @error="onImgError($event, LOCAL_IMAGES.cover)"
                />
                <div class="category-overlay">
                  <h4>{{ cat.title }}</h4>
                  <p>{{ cat.subtitle }}</p>
                </div>
              </article>
            </div>
          </div>

          <div class="card panel" id="progress">
            <div class="panel-head">
              <div>
                <span class="eyebrow">Live Site</span>
                <h2>Construction Progress</h2>
              </div>
              <strong class="progress-pct">{{ projectProgress }}%</strong>
            </div>

            <div class="phase-stepper">
              <button
                v-for="phase in phases"
                :key="phase.id"
                type="button"
                class="phase-step"
                :class="[phase.status, { selected: activePhase === phase.id }]"
                @click="activePhase = phase.id"
              >
                <span class="phase-dot"></span>
                {{ phase.label }}
              </button>
            </div>

            <div class="construction-visual">
              <img
                :src="projectImages.construction"
                alt="Construction site"
                @error="onImgError($event, LOCAL_IMAGES.construction)"
              />
              <div class="construction-overlay">
                <span>{{ phases.find((p) => p.id === activePhase)?.label || 'Structure' }} Phase</span>
                <strong>{{ projectProgress }}% Complete</strong>
              </div>
            </div>
          </div>
        </section>

        <!-- Project overview -->
        <section class="card panel overview-panel" id="overview">
          <div class="panel-head">
            <div>
              <span class="eyebrow">Project Overview</span>
              <h2>{{ displayName }}</h2>
              <p class="subtitle">{{ activeProject?.tagline }}</p>
            </div>
            <span class="rera-badge">RERA {{ activeProject?.rera_id || 'Registered' }}</span>
          </div>

          <div class="tabs">
            <button
              v-for="tab in overviewTabs"
              :key="tab.id"
              type="button"
              class="tab"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id; tab.id === 'documents' ? scrollTo('documents') : tab.id !== 'overview' && scrollTo('overview')"
            >
              {{ tab.label }}
            </button>
          </div>

          <div v-if="activeTab === 'overview'" class="overview-grid">
            <div class="overview-stat">
              <span>Shop Units</span>
              <strong>{{ activeProject?.shops || 217 }}</strong>
            </div>
            <div class="overview-stat">
              <span>Parking</span>
              <strong>{{ activeProject?.parking }}</strong>
            </div>
            <div class="overview-stat">
              <span>Total Built-up</span>
              <strong>{{ formatArea(activeProject?.total_area_sqft) }} Sq Ft</strong>
            </div>
            <div class="overview-stat">
              <span>Floors</span>
              <strong>{{ activeProject?.floors }} + Basement</strong>
            </div>
            <div class="overview-stat">
              <span>Launch</span>
              <strong>{{ activeProject?.launch_date }}</strong>
            </div>
            <div class="overview-stat">
              <span>Possession</span>
              <strong>{{ activeProject?.possession_date }}</strong>
            </div>
          </div>

          <div v-else-if="activeTab === 'amenities'" class="amenities-list">
            <span v-for="a in ['24×7 Security', 'High-speed Lifts', 'Fire Safety Systems', 'Dedicated Loading', 'Power Backup', 'Visitor Parking']" :key="a">{{ a }}</span>
          </div>

          <div v-else class="tab-placeholder">
            <p>Detailed {{ activeTab }} information available on request. Contact our sales desk.</p>
            <button type="button" class="btn-gold btn-sm-inline" @click="scrollTo('enquiry')">Get Details</button>
          </div>
        </section>

        <!-- Plans & PDFs -->
        <section class="docs-row">
          <div class="card panel docs-viewer-panel" id="documents">
            <div class="panel-head panel-head-split">
              <div>
                <span class="eyebrow">Project files</span>
                <h2>Plans &amp; PDFs</h2>
                <p class="subtitle">Municipal drawings for {{ displayName }} — click a file to preview below.</p>
              </div>
              <button type="button" class="btn-outline btn-sm-inline" :disabled="isLoading" @click="loadProjects">
                {{ isLoading ? 'Loading…' : 'Refresh' }}
              </button>
            </div>

            <div v-if="docsLoadFailed" class="empty-state">
              <AppIcon name="file" :size="32" />
              <strong>Documents unavailable</strong>
              <p>We couldn’t load plans right now. Please try again in a moment.</p>
              <button type="button" class="btn-outline btn-sm-inline" :disabled="isLoading" @click="loadProjects">
                Try again
              </button>
            </div>

            <div v-else-if="!hasUploadedDocs" class="empty-state">
              <AppIcon name="file" :size="32" />
              <strong>Plans coming soon</strong>
              <p>Municipal drawings for {{ displayName }} will be published here shortly.</p>
              <button type="button" class="btn-outline btn-sm-inline" @click="scrollTo('enquiry')">
                Request documents
              </button>
            </div>

            <template v-else>
              <div class="doc-cards-row">
                <button
                  v-for="doc in documents"
                  :key="doc.id"
                  type="button"
                  class="doc-card"
                  :class="{ active: selectedDocument?.url === doc.url }"
                  @click="selectDocument(doc)"
                >
                  <span class="doc-card-icon">PDF</span>
                  <div class="doc-card-text">
                    <strong>{{ docTitle(doc) }}</strong>
                    <span>{{ docSubtitle(doc) }}</span>
                  </div>
                  <span class="doc-card-action">View</span>
                </button>
              </div>

              <div v-if="selectedDocument" class="pdf-viewer-wrap">
                <div class="pdf-viewer-toolbar">
                  <strong>{{ docTitle(selectedDocument) }}</strong>
                  <div class="pdf-toolbar-actions">
                    <a :href="selectedDocument.url" target="_blank" rel="noopener" class="btn-outline btn-sm-inline">Open in new tab</a>
                    <a :href="selectedDocument.url" download class="btn-gold btn-sm-inline">Download</a>
                  </div>
                </div>
                <iframe
                  :key="selectedDocument.url"
                  :src="`${encodeURI(selectedDocument.url)}#toolbar=1&navpanes=1`"
                  class="pdf-iframe"
                  title="PDF preview"
                />
              </div>
            </template>
          </div>
        </section>
        <!-- Enquiry + About -->
        <section class="grid-2-bottom">
          <div class="card panel" id="about">
            <span class="eyebrow">Why Malkar</span>
            <h2>Trusted Builder. Proven Delivery.</h2>
            <p class="about-text">
              For over two decades, Malkar Enterprises has shaped commercial skylines across Maharashtra with
              RERA-compliant planning, premium retail formats, and transparent handovers.
            </p>
            <ul class="about-points">
              <li>End-to-end project management</li>
              <li>Grade-A construction standards</li>
              <li>Dedicated customer relationship desk</li>
            </ul>
          </div>

          <form class="card panel enquiry-form" id="enquiry" @submit.prevent="submitEnquiry">
            <span class="eyebrow">Get In Touch</span>
            <h2>Send An Enquiry</h2>
            <div class="form-grid">
              <label>
                <span>Name</span>
                <input v-model="enquiry.name" type="text" placeholder="Your name" required />
              </label>
              <label>
                <span>Mobile</span>
                <input v-model="enquiry.mobile" type="tel" placeholder="+91" required />
              </label>
              <label class="full">
                <span>Email</span>
                <input v-model="enquiry.email" type="email" placeholder="you@email.com" />
              </label>
              <label class="full">
                <span>Message</span>
                <textarea v-model="enquiry.message" rows="3" placeholder="I'm interested in…"></textarea>
              </label>
            </div>
            <button type="submit" class="btn-gold full-width">Submit Enquiry</button>
            <p v-if="enquiryStatus" :class="enquirySubmitOk ? 'form-success' : 'form-error'">{{ enquiryStatus }}</p>
          </form>
        </section>

        <footer class="site-footer" id="contact">
          <div>
            <strong>Malkar Enterprises</strong>
            <p>Builders & Developers · Kalyan, Thane</p>
          </div>
          <div class="footer-links">
            <a :href="CONTACT_PHONES[0].tel">{{ CONTACT_PHONES[0].display }}</a>
            <span class="phone-sep"> / </span>
            <a :href="CONTACT_PHONES[1].tel">{{ CONTACT_PHONES[1].display }}</a>
            <a :href="`mailto:${CONTACT_EMAIL}`">{{ CONTACT_EMAIL }}</a>
          </div>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  min-height: 100vh;
  background: var(--bg-deep);
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0.85rem;
  background: linear-gradient(180deg, #0e0e10 0%, #0a0a0b 100%);
  border-right: 1px solid var(--border);
  transition: transform 0.28s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.65rem 1.25rem;
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--gold-gradient);
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #1a1408;
  font-size: 1.1rem;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-copy strong {
  font-family: var(--serif);
  font-size: 1.05rem;
  letter-spacing: 0.04em;
}

.brand-copy small {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding-right: 0.15rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.75rem;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sidebar-link:hover,
.sidebar-link.active {
  background: rgba(212, 175, 55, 0.12);
  color: var(--gold-light);
}

.link-icon {
  flex-shrink: 0;
  color: var(--text-dim);
  transition: color 0.2s;
}

.sidebar-link:hover .link-icon,
.sidebar-link.active .link-icon {
  color: var(--gold-light);
}

.sidebar-footer {
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.sidebar-contact span {
  display: block;
  font-size: 0.65rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-contact .phone-sep,
.footer-links .phone-sep {
  color: var(--text-muted);
  margin: 0 0.15rem;
}

.sidebar-contact a {
  color: var(--gold);
  font-weight: 600;
  font-size: 0.85rem;
  text-decoration: none;
}

.social-row {
  display: flex;
  gap: 0.5rem;
  margin: 0.75rem 0;
}

.social-row a {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border);
  display: grid;
  place-items: center;
  color: var(--text-muted);
  text-decoration: none;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}

.social-row a:hover {
  border-color: var(--border-gold);
  color: var(--gold-light);
  background: rgba(212, 175, 55, 0.1);
}

.copyright {
  margin: 0;
  font-size: 0.68rem;
  color: var(--text-dim);
}

/* Main layout */
.main {
  flex: 1;
  margin-left: var(--sidebar-w);
  min-width: 0;
}

.sidebar-backdrop {
  display: none;
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.85rem 1.75rem;
  background: rgba(10, 10, 11, 0.88);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.menu-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-elevated);
  color: var(--text);
  cursor: pointer;
  flex-shrink: 0;
}

.menu-toggle:hover {
  border-color: var(--border-gold);
  color: var(--gold-light);
}

.header-nav {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.header-link {
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.2s;
}

.header-link:hover {
  color: var(--gold-light);
}

.header-phones {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.header-phone {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--border-gold);
  background: rgba(212, 175, 55, 0.1);
  color: var(--gold-light);
  font-weight: 600;
  font-size: 0.8rem;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s, border-color 0.2s;
}

.header-phone:hover {
  background: rgba(212, 175, 55, 0.2);
  border-color: var(--gold);
}

.content {
  padding: 1.25rem 1.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

/* Hero */
.hero-row {
  display: grid;
  grid-template-columns: 1.55fr 1fr;
  gap: 1.1rem;
}

.hero-banner {
  position: relative;
  min-height: 340px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-height: 340px;
  object-fit: cover;
  background: var(--bg-elevated);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, rgba(8, 8, 10, 0.92) 0%, rgba(8, 8, 10, 0.55) 50%, rgba(8, 8, 10, 0.35) 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: 2rem 2rem 2.25rem;
  max-width: 480px;
}

.eyebrow {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.75rem;
}

.hero-title {
  margin: 0 0 0.85rem;
  font-family: var(--serif);
  font-size: clamp(2rem, 3.5vw, 2.85rem);
  font-weight: 600;
  line-height: 1.05;
}

.hero-title em {
  font-style: italic;
  color: var(--gold-light);
}

.hero-desc {
  margin: 0 0 1.25rem;
  color: var(--text-muted);
  font-size: 0.92rem;
  line-height: 1.65;
}

.hero-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.btn-gold {
  padding: 0.75rem 1.35rem;
  border: none;
  border-radius: 10px;
  background: var(--gold-gradient);
  color: #1a1408;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(212, 175, 55, 0.2);
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-gold:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(212, 175, 55, 0.3);
}

.btn-outline {
  padding: 0.75rem 1.35rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
}

.btn-outline:hover {
  border-color: var(--border-gold);
  color: var(--gold-light);
}

.featured-card {
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold);
}

.featured-card h3 {
  margin: 0.35rem 0 0.25rem;
  font-family: var(--serif);
  font-size: 1.45rem;
}

.loc {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.85rem;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.featured-img-wrap {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  height: 140px;
  margin-bottom: 0.85rem;
}

.featured-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge-ongoing {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  background: var(--gold-gradient);
  color: #1a1408;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.featured-stats {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}

.featured-stats > div {
  display: flex;
  justify-content: space-between;
  padding: 0.55rem 0.7rem;
  border-radius: 10px;
  background: var(--bg-elevated);
  font-size: 0.8rem;
}

.featured-stats span {
  color: var(--text-muted);
}

.link-gold {
  margin-top: auto;
  border: none;
  background: none;
  color: var(--gold);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
  padding: 0;
}

/* Stats bar */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  padding: 1rem 1.25rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid var(--border-gold);
  flex-shrink: 0;
  display: grid;
  place-items: center;
  color: var(--gold);
}

.stat-item strong {
  display: block;
  font-size: 1rem;
  color: var(--gold-light);
}

.stat-item span {
  font-size: 0.68rem;
  color: var(--text-muted);
  line-height: 1.3;
}

/* Panels */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.1rem;
}

.docs-row {
  display: block;
}

.docs-viewer-panel {
  padding: 1.25rem 1.35rem 1.35rem;
}

.doc-cards-row {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  margin-bottom: 1rem;
}

.doc-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.doc-card:hover,
.doc-card.active {
  border-color: var(--border-gold);
  background: rgba(212, 175, 55, 0.08);
}

.doc-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(212, 175, 55, 0.15);
  color: var(--gold);
  font-size: 0.65rem;
  font-weight: 800;
  display: grid;
  place-items: center;
}

.doc-card-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.doc-card-text strong {
  font-size: 0.88rem;
  line-height: 1.35;
  word-break: break-word;
}

.doc-card-text span {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.doc-card-action {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--gold);
  white-space: nowrap;
}

.pdf-viewer-wrap {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--border-gold);
  background: #1a1a1c;
}

.pdf-viewer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.65rem 0.85rem;
  background: rgba(212, 175, 55, 0.1);
  border-bottom: 1px solid var(--border);
}

.pdf-viewer-toolbar strong {
  font-size: 0.82rem;
  color: var(--gold-light);
  max-width: 55%;
  line-height: 1.3;
}

.pdf-toolbar-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pdf-iframe {
  width: 100%;
  height: min(72vh, 620px);
  min-height: 420px;
  border: none;
  display: block;
  background: #2a2a2e;
}

.grid-2-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.1rem;
}

.span-2 {
  grid-column: span 1;
}

.panel {
  padding: 1.25rem 1.35rem;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.1rem;
}

.panel-head.compact {
  margin-bottom: 0.85rem;
}

.panel-head h2,
.panel-head h3 {
  margin: 0.25rem 0 0;
  font-family: var(--serif);
  font-size: 1.35rem;
  font-weight: 600;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.btn-sm {
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--gold);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.progress-pct {
  font-size: 1.5rem;
  color: var(--gold-light);
  font-family: var(--serif);
}

/* Category grid */
.category-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}

.category-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  min-height: 120px;
}

.category-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  min-height: 120px;
  transition: transform 0.4s ease;
}

.category-card:hover img {
  transform: scale(1.05);
}

.category-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.85) 0%, transparent 60%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 0.85rem;
}

.category-overlay h4 {
  margin: 0;
  font-size: 0.9rem;
}

.category-overlay p {
  margin: 0.15rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Construction */
.phase-stepper {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}

.phase-step {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}

.phase-step.done {
  border-color: rgba(74, 222, 128, 0.3);
  color: #86efac;
}

.phase-step.active,
.phase-step.selected {
  border-color: var(--border-gold);
  background: rgba(212, 175, 55, 0.12);
  color: var(--gold-light);
}

.phase-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.construction-visual {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  height: 200px;
  background: var(--bg-elevated);
}

.construction-visual img {
  width: 100%;
  height: 100%;
  min-height: 200px;
  object-fit: cover;
}

.construction-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.85rem 1rem;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.9), transparent);
}

.construction-overlay span {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.construction-overlay strong {
  display: block;
  font-size: 1.1rem;
  color: var(--gold-light);
}

/* Overview */
.rera-badge {
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-gold);
  font-size: 0.72rem;
  color: var(--gold);
  white-space: nowrap;
}

.tabs {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tab {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.tab.active {
  background: rgba(212, 175, 55, 0.12);
  border-color: var(--border-gold);
  color: var(--gold-light);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.65rem;
}

.overview-stat {
  padding: 0.85rem 1rem;
  border-radius: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
}

.overview-stat span {
  display: block;
  font-size: 0.68rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
}

.overview-stat strong {
  font-size: 0.95rem;
}

.amenities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.amenities-list span {
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  font-size: 0.8rem;
}

.tab-placeholder {
  padding: 1rem;
  border-radius: 12px;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.tab-placeholder p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.88rem;
}

.btn-sm-inline {
  padding: 0.55rem 1rem;
  font-size: 0.8rem;
}

/* Floor plans */
.floor-layout {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 0.85rem;
  min-height: 220px;
}

.floor-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-height: 240px;
  overflow-y: auto;
}

.floor-btn {
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: var(--bg-elevated);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
}

.floor-btn.active {
  border-color: var(--border-gold);
  background: rgba(212, 175, 55, 0.1);
  color: var(--gold-light);
}

.floor-canvas {
  border-radius: 12px;
  overflow: auto;
  background: #0e1014;
  border: 1px solid var(--border);
  display: grid;
  place-items: center;
  min-height: 200px;
}

.floor-canvas img {
  max-width: 100%;
  transition: transform 0.2s ease;
  object-fit: contain;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.zoom-controls button {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text);
  cursor: pointer;
}

.zoom-controls span {
  font-size: 0.78rem;
  color: var(--text-muted);
  min-width: 36px;
  text-align: center;
}

/* Documents */
.doc-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.doc-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  border-radius: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}

.doc-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(212, 175, 55, 0.15);
  color: var(--gold);
  font-size: 0.6rem;
  font-weight: 800;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.doc-info strong {
  display: block;
  font-size: 0.78rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-info small {
  font-size: 0.65rem;
  color: var(--text-dim);
}

.doc-dl {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--gold-gradient);
  color: #1a1408;
  display: grid;
  place-items: center;
  font-weight: 800;
  text-decoration: none;
  flex-shrink: 0;
}

/* About & Enquiry */
.about-text {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.7;
  margin: 0.75rem 0 1rem;
}

.about-points {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.45rem;
}

.about-points li {
  padding-left: 1rem;
  position: relative;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.about-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.55em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--gold);
}

.enquiry-form h2 {
  margin: 0.25rem 0 1rem;
  font-family: var(--serif);
  font-size: 1.35rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-grid label.full {
  grid-column: span 2;
}

.form-grid span {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.form-grid input,
.form-grid textarea {
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text);
  outline: none;
}

.form-grid input:focus,
.form-grid textarea:focus {
  border-color: var(--border-gold);
}

.full-width {
  width: 100%;
}

.form-success {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: #86efac;
}

.form-error {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: #f0a0a0;
}

.site-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.25rem 0 0.5rem;
  border-top: 1px solid var(--border);
  margin-top: 0.5rem;
}

.site-footer strong {
  font-family: var(--serif);
  font-size: 1.1rem;
}

.site-footer p {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: right;
}

.footer-links a {
  color: var(--gold);
  font-weight: 600;
  font-size: 0.88rem;
  text-decoration: none;
}

.project-picker {
  margin-bottom: 0;
}

.project-cards-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.85rem;
}

.project-pick-card {
  display: flex;
  gap: 0.75rem;
  padding: 0.65rem;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  cursor: pointer;
  text-align: left;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.project-pick-card:hover,
.project-pick-card.active {
  border-color: var(--border-gold);
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.25);
}

.project-pick-card img {
  width: 72px;
  height: 72px;
  border-radius: 10px;
  object-fit: cover;
  flex-shrink: 0;
}

.project-pick-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.pick-status {
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--gold);
}

.project-pick-body strong {
  font-size: 0.9rem;
}

.project-pick-body small {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.pick-progress {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 0.15rem;
}

.upload-hint {
  padding: 0.85rem;
  margin-bottom: 0.75rem;
  border-radius: 12px;
  background: rgba(212, 175, 55, 0.08);
  border: 1px dashed var(--border-gold);
  font-size: 0.82rem;
}

.upload-hint strong {
  display: block;
  color: var(--gold-light);
  margin-bottom: 0.35rem;
}

.upload-hint p {
  margin: 0.25rem 0;
  color: var(--text-muted);
}

.folder-path {
  display: block;
  margin: 0.35rem 0;
  padding: 0.4rem 0.55rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.35);
  font-size: 0.68rem;
  color: #c9e6ff;
  word-break: break-all;
}

.hint-note {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.65rem;
  padding: 2.5rem 1.5rem;
  border-radius: var(--radius);
  border: 1px dashed var(--border);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-muted);
}

.empty-state :deep(.app-icon) {
  color: var(--gold);
  opacity: 0.85;
}

.empty-state strong {
  color: var(--text);
  font-family: var(--serif);
  font-size: 1.15rem;
  font-weight: 600;
}

.empty-state p {
  margin: 0;
  max-width: 36ch;
  font-size: 0.88rem;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .hero-row,
  .grid-2,
  .docs-row,
  .grid-2-bottom {
    grid-template-columns: 1fr;
  }

  .pdf-iframe {
    min-height: 360px;
    height: 55vh;
  }

  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
  }

  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 99;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(4px);
  }

  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.28s ease;
    box-shadow: var(--shadow);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main {
    margin-left: 0;
  }

  .menu-toggle {
    display: flex;
  }

  .header-nav {
    display: none;
  }

  .header-phones {
    gap: 0.35rem;
  }

  .header-phone span {
    display: none;
  }

  .header-phone {
    width: 40px;
    height: 40px;
    padding: 0;
    justify-content: center;
    border-radius: 10px;
  }

  .top-header {
    padding: 0.75rem 1rem;
  }

  .content {
    padding: 1rem;
  }

  .footer-links {
    flex-direction: column;
    align-items: flex-end;
    gap: 0.35rem;
  }

  .panel-head,
  .panel-head-split {
    flex-direction: column;
    align-items: stretch;
  }

  .pdf-viewer-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .pdf-viewer-toolbar strong {
    max-width: 100%;
  }

  .pdf-toolbar-actions {
    width: 100%;
  }

  .pdf-toolbar-actions a {
    flex: 1;
    text-align: center;
  }

  .doc-card {
    grid-template-columns: auto 1fr;
    gap: 0.65rem;
  }

  .doc-card-action {
    grid-column: 2;
    justify-self: start;
  }

  .rera-badge {
    align-self: flex-start;
  }

  .site-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .footer-links {
    align-items: flex-start;
    text-align: left;
  }
}

@media (max-width: 640px) {
  .header-phones {
    flex-wrap: wrap;
    justify-content: flex-end;
    max-width: calc(100% - 48px);
  }

  .header-phone span {
    display: inline;
    font-size: 0.68rem;
  }

  .header-phone {
    width: auto;
    height: auto;
    padding: 0.35rem 0.55rem;
    border-radius: 999px;
  }

  .stats-bar {
    grid-template-columns: 1fr;
  }

  .category-grid {
    grid-template-columns: 1fr;
  }

  .hero-btns {
    flex-direction: column;
  }

  .hero-btns .btn-gold,
  .hero-btns .btn-outline {
    width: 100%;
    text-align: center;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-grid label.full {
    grid-column: span 1;
  }

  .pdf-iframe {
    min-height: 280px;
    height: 50vh;
  }
}

@media (max-width: 400px) {
  .top-header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .header-left {
    flex: 1;
    min-width: 0;
  }

  .header-phones {
    width: 100%;
    max-width: none;
    justify-content: stretch;
    gap: 0.35rem;
  }

  .header-phone {
    flex: 1;
    justify-content: center;
    min-width: 0;
  }

  .header-phone span {
    font-size: 0.62rem;
    letter-spacing: -0.02em;
  }
}
</style>
