const BASE_URL = (process.env.REACT_APP_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

// Diagnostics are intentionally metadata-only: never log credentials, request bodies or tokens.
const DEBUG = process.env.NODE_ENV !== "production" || process.env.REACT_APP_DEBUG_REQUESTS === "true";
let sequence = 0;
function trace(id, stage, meta = {}) {
  if (DEBUG) console.info("[Orbit API]", id, stage, meta);
}

export async function apiRequest(path, { method = "GET", body, auth = true } = {}) {
  const id = ++sequence;
  const started = Date.now();
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = sessionStorage.getItem("orbit_access_token");
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  const controller = new AbortController();
  // MongoDB connectivity failures can take ~30 seconds. Bound UI waiting.
  const timeout = setTimeout(() => controller.abort(), 40000);
  let response;
  trace(id, "start", { method, path, auth, base: BASE_URL });
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method, headers, body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    trace(id, "response", { status: response.status, elapsedMs: Date.now() - started });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (auth && response.status === 401) {
        sessionStorage.removeItem("orbit_access_token");
        window.dispatchEvent(new Event("orbit:session-expired"));
      }
      trace(id, "http_error", { status: response.status, elapsedMs: Date.now() - started });
      throw new Error(typeof data.detail === "string" ? data.detail : `Request failed (${response.status}).`);
    }
    trace(id, "success", { elapsedMs: Date.now() - started });
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      trace(id, "timeout", { elapsedMs: Date.now() - started });
      throw new Error("Orbit API timed out. Check backend and MongoDB connectivity.");
    }
    trace(id, "failure", { type: error.name, elapsedMs: Date.now() - started });
    if (error instanceof TypeError) throw new Error("Orbit's server is unreachable. Check the backend URL and CORS.");
    throw error;
  } finally {
    clearTimeout(timeout);
  }
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
