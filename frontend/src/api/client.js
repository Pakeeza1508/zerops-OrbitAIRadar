const BASE_URL = (process.env.REACT_APP_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

export async function apiRequest(path, { method = "GET", body, auth = true } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = sessionStorage.getItem("orbit_access_token");
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method, headers, body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch { throw new Error("Orbit's server is unreachable. Please try again."); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (auth && response.status === 401) {
      sessionStorage.removeItem("orbit_access_token");
      window.dispatchEvent(new Event("orbit:session-expired"));
    }
    throw new Error(typeof data.detail === "string" ? data.detail : `Request failed (${response.status}).`);
  }
  return data;
}

export function clearLegacyAuth() {
  ["orbit_auth", "orbit_demo", "orbit_demo_profile", "orbit_profile"].forEach((key) => localStorage.removeItem(key));
}

const categoryKey = (label) => ({
  "Open Source": "open_source", Research: "research", Scholarship: "scholarship",
  Internship: "internship", Fellowship: "fellowship", Hackathon: "hackathon",
  Competition: "competition",
}[label] || label.toLowerCase().trim().replace(/\s+/g, "_"));

export function fromApiProfile(data = {}) {
  const locations = data.locationPreference || [];
  const workMode = locations.includes("remote") ? "Remote" :
    locations.includes("hybrid") ? "Hybrid" : locations.includes("onsite") ? "On-site" : "Any";
  const funding = { funded_only: "Fully funded or paid", any: "Any funding",
    prize: "Prize opportunities", unfunded_ok: "Unpaid is okay" };
  return {
    fullName: data.fullName || "", country: data.country || "",
    education: data.educationLevel || "", field: data.fieldOfStudy || "",
    graduationYear: data.graduationYear == null ? "" : String(data.graduationYear),
    skills: data.skills || [], interests: data.interests || [],
    workMode,
    preferredRegions: [...(locations.includes("global") ? ["Global"] : []), ...(data.preferredCountries || [])],
    fundingPreference: funding[data.fundingPreference] || "Any funding",
  };
}

export function toApiProfile(profile) {
  const location = { Remote: "remote", Hybrid: "hybrid", "On-site": "onsite" };
  const funding = {
    "Fully funded or paid": "funded_only", "Any funding": "any",
    "Prize opportunities": "prize", "Unpaid is okay": "unfunded_ok",
  };
  const locations = location[profile.workMode] ? [location[profile.workMode]] : [];
  if ((profile.preferredRegions || []).includes("Global")) locations.push("global");
  const year = Number.parseInt(profile.graduationYear, 10);
  return {
    fullName: profile.fullName || null, country: profile.country || null,
    educationLevel: profile.education || null, fieldOfStudy: profile.field || null,
    graduationYear: Number.isFinite(year) ? year : null, experienceLevel: null,
    skills: profile.skills || [], interests: profile.interests || [],
    preferredCategories: (profile.interests || []).map(categoryKey),
    locationPreference: locations,
    preferredCountries: (profile.preferredRegions || []).filter((v) => v !== "Global"),
    fundingPreference: funding[profile.fundingPreference] || "any",
  };
}
