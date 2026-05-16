/** Local bundled assets — always load from /public/images (no external CDN). */
export const LOCAL_IMAGES = {
  hero: '/images/hero.jpg',
  cover: '/images/cover.jpg',
  thumbnail: '/images/thumbnail.jpg',
  construction: '/images/construction.jpg',
  floorPlan: '/images/floor-plan.jpg',
  gallery: [
    '/images/gallery-1.jpg',
    '/images/gallery-2.jpg',
    '/images/gallery-3.jpg',
    '/images/gallery-4.jpg',
  ],
}

export const DEFAULT_CATEGORIES = [
  {
    title: 'Premium Retail',
    subtitle: 'High-street & mall formats',
    image: '/images/cat-retail.jpg',
  },
  {
    title: 'Modern Office',
    subtitle: 'Grade-A commercial spaces',
    image: '/images/cat-office.jpg',
  },
  {
    title: 'Smart Infrastructure',
    subtitle: 'Integrated utilities & services',
    image: '/images/cat-infra.jpg',
  },
  {
    title: 'Sustainable Development',
    subtitle: 'Green-certified planning',
    image: '/images/cat-green.jpg',
  },
]

export const DEFAULT_PHASES = [
  { id: 'planning', label: 'Planning', status: 'done' },
  { id: 'foundation', label: 'Foundation', status: 'pending' },
  { id: 'structure', label: 'Structure', status: 'active' },
  { id: 'interior', label: 'Interior', status: 'pending' },
  { id: 'completion', label: 'Completion', status: 'pending' },
]

export const DEFAULT_FLOORS = [
  'Basement',
  'Ground',
  '1st Floor',
  '2nd Floor',
  '3rd Floor',
  '4th Floor',
  '5th Floor',
  '6th Floor',
  '7th Floor',
]

/** Bundled PDFs — served from /public on Vercel (no backend required). */
export const DEFAULT_DOCUMENTS = [
  {
    id: 'kala-chowki-draft-plans',
    name: 'DRAFT PLANS — Phase II Municipal Drawing (FSI 5.40)',
    url: '/project-files/kala-chowki/draft-plans-municipal.pdf',
    available: true,
  },
  {
    id: 'kala-chowki-ganesha-galaxy',
    name: 'GANESHA GALAXY Municipal Drawing Set',
    url: '/project-files/kala-chowki/ganesha-galaxy-municipal.pdf',
    available: true,
  },
  {
    id: 'kala-chowki-gallery',
    name: 'Project Gallery Booklet',
    url: '/project-files/kala-chowki/project-gallery-booklet.pdf',
    available: true,
  },
]

export const DEFAULT_PROJECT = {
  id: 1,
  slug: 'kala-chowki',
  display_name: 'Kalyan Kala Chowk',
  tagline: 'Premium Commercial Complex',
  location: 'Kalyan (W), Thane, Maharashtra',
  type: 'Commercial Complex',
  status: 'ongoing',
  progress: 10,
  shops: 217,
  parking: '180 Scooters / 217 Cars',
  launch_date: 'Q2 2024',
  possession_date: 'Q4 2026',
  rera_id: 'P51700012345',
  total_area_sqft: 339791.47,
  floors: 7,
  floor_list: DEFAULT_FLOORS,
  images: LOCAL_IMAGES,
  categories: DEFAULT_CATEGORIES,
  construction_phases: DEFAULT_PHASES,
  documents: DEFAULT_DOCUMENTS,
  maps: [],
}

/** Normalize API asset URLs (fixes localhost links from the backend). */
export function resolveApiUrl(url, apiBase) {
  if (!url || typeof url !== 'string') return ''
  const base = (apiBase || '').replace(/\/$/, '')
  if (url.startsWith('/')) return url
  if (url.startsWith('/project-files/')) return url
  try {
    const parsed = new URL(url, base || 'http://localhost')
    if (parsed.hostname === '127.0.0.1' || parsed.hostname === 'localhost') {
      if (!base) return parsed.pathname
      return `${base}${parsed.pathname}${parsed.search}`
    }
    return parsed.href
  } catch {
    return url
  }
}

/** Prefer local assets when API returns missing or blocked CDN URLs. */
export function resolveImage(url, fallback) {
  if (!url || typeof url !== 'string') return fallback
  if (url.includes('unsplash.com') || url.includes('picsum.photos')) return fallback
  // Relative paths from API work on the Vite dev server and production build
  if (url.startsWith('/images/')) return url
  return url
}

export function resolveGallery(apiGallery) {
  if (!Array.isArray(apiGallery) || apiGallery.length === 0) return LOCAL_IMAGES.gallery
  const usable = apiGallery.filter((u) => u && !u.includes('unsplash.com'))
  return usable.length ? usable : LOCAL_IMAGES.gallery
}
