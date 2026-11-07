import { apiRequest } from "./client";

// Numeric matchScore and Mongo saved-row IDs are deliberately adapted here.
const list = (value) => Array.isArray(value) ? value : [];
const score = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 0;
};
const humanCategory = (value) => String(value || "Opportunity").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
export function fromApiOpportunity(raw = {}) {
  const item = raw || {};
  const deadline = item.deadline ? new Date(item.deadline) : null;
  const remaining = item.daysRemaining == null ? null : Number(item.daysRemaining);
  const created = item.createdAt ? new Date(item.createdAt) : null;
  return {
    ...item,
    id: String(item.id || ""),
    title: item.title || "Untitled opportunity",
    organization: item.organization || "Organization not listed",
    category: humanCategory(item.category),
    match: score(item.matchScore), // Backend match is a structured object.
    matchDetails: item.match,
    applicationUrl: item.applyUrl || item.applicationUrl || item.sourceUrl || "",
    sourceUrl: item.sourceUrl || "",
    matchedSkills: list(item.matchedSkills),
    missingSkills: list(item.missingSkills),
    eligibility: list(item.eligibility),
    requirements: list(item.requirements),
    benefits: list(item.benefits),
    gaps: list(item.gaps).length ? list(item.gaps) : list(item.missingSkills),
    daysRemaining: Number.isFinite(remaining) ? remaining : null,
    deadline: deadline && !Number.isNaN(deadline.getTime()) ? item.deadline : null,
    location: item.location || (item.remote ? "Remote" : list(item.countriesEligible).join(", ") || "Not specified"),
    workMode: item.workMode || (item.remote ? "Remote" : "Not specified"),
    funding: item.funding || item.fundingType || "Not specified",
    verified: item.verified === true || item.verificationStatus === "verified",
    isNew: created && !Number.isNaN(created.getTime()) ? Date.now() - created.getTime() < 86400000 : false,
    lastChecked: item.lastChecked || (item.lastCheckedAt ? new Date(item.lastCheckedAt).toLocaleDateString() : "not available"),
    shortDescription: item.shortDescription || item.description || "",
    description: item.description || item.shortDescription || "No description provided.",
  };
}
export function fromApiSaved(row = {}) {
  const snapshot = fromApiOpportunity(row.snapshot || {});
  return {
    id: String(row.id || ""),
    originalOpportunityId: String(row.originalOpportunityId || snapshot.id || ""),
    snapshot,
    status: row.applicationStatus || "saved",
    expired: row.expired === true,
    savedAt: row.savedAt || null,
  };
}
export function opportunityQuery(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "" && value !== "All" && value !== "Any") {
      params.set(key, String(value));
    }
  });
  return `/api/opportunities${params.toString() ? "?" + params : ""}`;
}
export const getOpportunities = async (filters = {}) => {
  const response = await apiRequest(opportunityQuery(filters));
  return { ...response, items: list(response.items).map(fromApiOpportunity) };
};
export const getOpportunity = async (id) => fromApiOpportunity(await apiRequest(`/api/opportunities/${encodeURIComponent(id)}`));
export const getSaved = async () => {
  const response = await apiRequest("/api/saved");
  return list(response.items).map(fromApiSaved);
};
export const saveOpportunity = async (id) => fromApiSaved(await apiRequest(`/api/opportunities/${encodeURIComponent(id)}/save`, { method: "POST" }));
export const unsaveOpportunity = (id) => apiRequest(`/api/opportunities/${encodeURIComponent(id)}/save`, { method: "DELETE" });
export const updateSavedStatus = async (savedId, status) => fromApiSaved(await apiRequest(`/api/saved/${encodeURIComponent(savedId)}`, { method: "PATCH", body: { applicationStatus: status } }));
export const askOrbitApi = async (query) => {
  const response = await apiRequest("/api/search/ai", { method: "POST", body: { query } });
  return { ...response, items: list(response.items).map(fromApiOpportunity) };
};
