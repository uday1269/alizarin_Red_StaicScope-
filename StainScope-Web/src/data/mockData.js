// Scientific User Profile Data for StainScope Workstation

export const MOCK_USER = {
  name: "Dr. Sarah Chen",
  role: "Senior Bone Tissue Engineer",
  email: "admin@gmail.com",
  lab: "Regenerative Medicine & Osteogenesis Lab",
  institution: "BioMed Research Institute",
  scansCount: 0,
  calcificationAvg: "0.0%",
  memberSince: "Jan 2025",
  avatarInitials: "SC"
};

// No fake analysis records - analysis history strictly populated by real Classical CV backend runs
export const MOCK_RECENT_ANALYSES = [];

export const MOCK_SAMPLE_PRESETS = [];

export const MOCK_COLOR_HISTOGRAM = [
  { label: "Deep Red (Dense Calcification)", percentage: 38.5, color: "#801D1E" },
  { label: "Crimson (Moderate Nodule)", percentage: 26.2, color: "#DC2626" },
  { label: "Light Pink (Diffused Stain)", percentage: 19.8, color: "#FCA5A5" },
  { label: "Unstained Matrix / Background", percentage: 15.5, color: "#F3F4F6" }
];
