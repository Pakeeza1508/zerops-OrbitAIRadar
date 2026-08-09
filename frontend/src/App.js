import { createContext, useContext, useMemo, useState } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Bookmark,
  CalendarClock,
  Check,
  CheckCircle2,
  ChevronDown,
  Clock3,
  Compass,
  Database,
  ExternalLink,
  FileCheck2,
  Filter,
  Globe2,
  GraduationCap,
  Loader2,
  MapPin,
  Play,
  Radar,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  Trophy,
  UserRound,
  WandSparkles,
  Zap,
  UploadCloud,
  FileText,
} from "lucide-react";

import AppShell from "./components/AppShell";
import MetricCard from "./components/MetricCard";
import OpportunityCard from "./components/OpportunityCard";
import OrbitLogo from "./components/OrbitLogo";

const OrbitContext = createContext(null);

const useOrbit = () => useContext(OrbitContext);

const opportunitySeed = [
  {
    id: "gsoc-2027",
    title: "Google Summer of Code 2027",
    organization: "Google Open Source",
    category: "Open Source",
    match: 96,
    deadline: "2027-03-31",
    daysRemaining: 235,
    location: "Global",
    remote: true,
    workMode: "Remote",
    funding: "Paid stipend",
    fundingType: "Paid",
    verified: true,
    isNew: false,
    lastChecked: "9 min ago",
    sourceUrl: "https://summerofcode.withgoogle.com/",
    applicationUrl: "https://summerofcode.withgoogle.com/",
    shortDescription:
      "A global open-source program connecting contributors with established organizations for a mentored software project.",
    description:
      "Google Summer of Code is a global program focused on bringing new contributors into open-source software development. Contributors work with participating organizations under experienced mentors.",
    eligibility: [
      "Open to eligible contributors worldwide",
      "Must satisfy the program's contributor eligibility rules",
      "Availability for the full coding period",
    ],
    requirements: [
      "Interest in open source",
      "Ability to work with a mentor and community",
      "Project proposal for a participating organization",
    ],
    benefits: [
      "Paid stipend",
      "Real open-source contribution experience",
      "Mentorship from established communities",
    ],
    matchedSkills: ["Python", "Open Source", "Git"],
    gaps: ["Add 1–2 public open-source contributions before applying"],
  },
  {
    id: "mlh-fellowship",
    title: "MLH Fellowship — Software Engineering",
    organization: "Major League Hacking",
    category: "Fellowship",
    match: 94,
    deadline: "2026-09-01",
    daysRemaining: 24,
    location: "Global",
    remote: true,
    workMode: "Remote",
    funding: "Stipend available",
    fundingType: "Paid",
    verified: true,
    isNew: true,
    lastChecked: "12 min ago",
    sourceUrl: "https://fellowship.mlh.io/",
    applicationUrl: "https://fellowship.mlh.io/",
    shortDescription:
      "A remote, mentor-led program where developers collaborate on real-world projects and strengthen production engineering skills.",
    description:
      "The MLH Fellowship is a remote program designed to give developers practical experience through structured, mentor-supported project work.",
    eligibility: [
      "Developer or technical student profile",
      "Can participate remotely",
      "Availability during the program",
    ],
    requirements: [
      "Programming foundations",
      "Collaborative communication",
      "Portfolio or examples of technical work",
    ],
    benefits: ["Mentorship", "Peer community", "Project experience"],
    matchedSkills: ["React", "Python", "Open Source"],
    gaps: ["Portfolio links would strengthen your application"],
  },
  {
    id: "global-ai-research",
    title: "Global AI Research Fellowship 2026",
    organization: "Future Systems Lab",
    category: "Research",
    match: 92,
    deadline: "2026-08-29",
    daysRemaining: 21,
    location: "Remote / Global",
    remote: true,
    workMode: "Remote",
    funding: "Fully funded",
    fundingType: "Fully funded",
    verified: true,
    isNew: true,
    lastChecked: "8 min ago",
    sourceUrl: "https://example.org/future-systems-lab",
    applicationUrl: "https://example.org/apply/future-systems-lab",
    shortDescription:
      "A remote research fellowship for undergraduate and early-career builders exploring practical AI systems and responsible deployment.",
    description:
      "A structured research fellowship focused on applied artificial intelligence, experimentation, technical communication, and mentor-guided project work.",
    eligibility: [
      "Undergraduate or early-career applicant",
      "International applicants accepted",
      "Computer science or related technical field",
    ],
    requirements: [
      "Python fundamentals",
      "Interest in AI research",
      "Short technical statement",
    ],
    benefits: [
      "Fully funded participation",
      "Research mentorship",
      "Final project showcase",
    ],
    matchedSkills: ["Python", "AI", "Machine Learning"],
    gaps: ["Research writing sample recommended"],
  },
  {
    id: "devpost-climate",
    title: "Build for Climate Hackathon",
    organization: "Open Impact Network",
    category: "Hackathon",
    match: 89,
    deadline: "2026-08-18",
    daysRemaining: 10,
    location: "Online",
    remote: true,
    workMode: "Remote",
    funding: "$10K prize pool",
    fundingType: "Prize",
    verified: true,
    isNew: true,
    lastChecked: "16 min ago",
    sourceUrl: "https://devpost.com/",
    applicationUrl: "https://devpost.com/",
    shortDescription:
      "A fast-moving online hackathon for software and AI prototypes that address climate, energy, mobility, or resilience problems.",
    description:
      "Teams build and ship a working climate-focused product during a time-boxed online hackathon with technical and impact judging.",
    eligibility: [
      "Open online participation",
      "Team or solo entry",
      "Public project demo required",
    ],
    requirements: [
      "Working software project",
      "Public demo",
      "Short submission description",
    ],
    benefits: ["Prize pool", "Public showcase", "Mentor feedback"],
    matchedSkills: ["React", "AI", "Python"],
    gaps: ["Add a climate-specific problem statement"],
  },
  {
    id: "europe-tech-scholarship",
    title: "Emerging Technologists Scholarship",
    organization: "European Digital Foundation",
    category: "Scholarship",
    match: 86,
    deadline: "2026-10-15",
    daysRemaining: 68,
    location: "Europe",
    remote: false,
    workMode: "On-site",
    funding: "Tuition support",
    fundingType: "Fully funded",
    verified: true,
    isNew: false,
    lastChecked: "32 min ago",
    sourceUrl: "https://example.org/edf-scholarship",
    applicationUrl: "https://example.org/edf-scholarship/apply",
    shortDescription:
      "A scholarship supporting high-potential computing students pursuing advanced technical study and community impact.",
    description:
      "A scholarship program for students in computing-related disciplines with a focus on academic promise, community contribution, and technology leadership.",
    eligibility: [
      "Computing-related field",
      "Academic enrollment required",
      "International route available for selected institutions",
    ],
    requirements: [
      "Academic transcript",
      "Personal statement",
      "One reference",
    ],
    benefits: [
      "Tuition support",
      "Mentor network",
      "Community events",
    ],
    matchedSkills: ["Computer Science", "AI"],
    gaps: ["Check institution eligibility before applying"],
  },
  {
    id: "remote-frontend-intern",
    title: "Frontend Engineering Internship",
    organization: "Nova Labs",
    category: "Internship",
    match: 84,
    deadline: "2026-08-26",
    daysRemaining: 18,
    location: "Remote",
    remote: true,
    workMode: "Remote",
    funding: "Paid",
    fundingType: "Paid",
    verified: true,
    isNew: true,
    lastChecked: "20 min ago",
    sourceUrl: "https://example.org/nova-labs-careers",
    applicationUrl:
      "https://example.org/nova-labs-careers/frontend-intern",
    shortDescription:
      "A remote product engineering internship focused on React interfaces, accessibility, experimentation, and shipping user-facing features.",
    description:
      "A product-focused frontend internship where interns contribute to a React application with guidance from senior engineers and designers.",
    eligibility: [
      "Student or recent graduate",
      "Remote availability",
      "Portfolio or project experience",
    ],
    requirements: ["React", "JavaScript", "Git"],
    benefits: [
      "Paid internship",
      "Mentorship",
      "Production experience",
    ],
    matchedSkills: ["React", "JavaScript", "UI/UX"],
    gaps: ["Add one polished public React project"],
  },
  {
    id: "open-data-challenge",
    title: "Global Open Data Challenge",
    organization: "Civic Data Alliance",
    category: "Competition",
    match: 81,
    deadline: "2026-09-20",
    daysRemaining: 43,
    location: "Global",
    remote: true,
    workMode: "Remote",
    funding: "$5K awards",
    fundingType: "Prize",
    verified: false,
    isNew: false,
    lastChecked: "1 hr ago",
    sourceUrl: "https://example.org/open-data-challenge",
    applicationUrl: "https://example.org/open-data-challenge",
    shortDescription:
      "A public-data competition for teams building useful visualizations, civic tools, and applied analytics from open datasets.",
    description:
      "A global challenge inviting participants to turn public datasets into meaningful applications, visualizations, or research prototypes.",
    eligibility: [
      "Global participation",
      "Public submission",
      "Use of open datasets",
    ],
    requirements: [
      "Working prototype",
      "Public repository",
      "Short impact note",
    ],
    benefits: [
      "Awards",
      "Public recognition",
      "Community feedback",
    ],
    matchedSkills: ["Python", "Data Science"],
    gaps: ["Data visualization experience would improve fit"],
  },
  {
    id: "linux-mentorship",
    title: "Open Source Mentorship Program",
    organization: "Linux Ecosystem Initiative",
    category: "Open Source",
    match: 78,
    deadline: "2026-11-05",
    daysRemaining: 89,
    location: "Global",
    remote: true,
    workMode: "Remote",
    funding: "Stipend varies",
    fundingType: "Paid",
    verified: true,
    isNew: false,
    lastChecked: "44 min ago",
    sourceUrl: "https://example.org/linux-mentorship",
    applicationUrl:
      "https://example.org/linux-mentorship/apply",
    shortDescription:
      "Mentored contributions to open-source infrastructure projects with structured technical guidance and community review.",
    description:
      "A mentorship pathway for developers who want to contribute to open-source infrastructure and learn community development workflows.",
    eligibility: [
      "Global applicants",
      "Basic development experience",
      "Can contribute asynchronously",
    ],
    requirements: [
      "Git",
      "Programming fundamentals",
      "Interest in systems or infrastructure",
    ],
    benefits: [
      "Mentorship",
      "Open-source portfolio",
      "Community network",
    ],
    matchedSkills: ["Open Source", "Git"],
    gaps: ["Linux systems experience would improve your match"],
  },
];

const initialRuns = [
  {
    id: 1,
    started: "Today · 02:00",
    status: "Success",
    sources: 12,
    urls: 73,
    newCount: 6,
    updated: 4,
    expired: 1,
    aiCalls: 8,
  },
  {
    id: 2,
    started: "Yesterday · 02:00",
    status: "Success",
    sources: 12,
    urls: 61,
    newCount: 4,
    updated: 2,
    expired: 3,
    aiCalls: 6,
  },
  {
    id: 3,
    started: "Aug 6 · 02:00",
    status: "Partial",
    sources: 12,
    urls: 58,
    newCount: 5,
    updated: 1,
    expired: 0,
    aiCalls: 7,
  },
];

const defaultProfile = {
  fullName: "",
  country: "Pakistan",
  education: "Undergraduate",
  field: "Computer Science",
  graduationYear: "2027",
  skills: ["Python", "React", "AI"],
  interests: ["Fellowship", "Open Source", "Hackathon"],
  workMode: "Remote",
  preferredRegions: ["Global", "Europe"],
  fundingPreference: "Fully funded or paid",
};

const demoProfile = {
  ...defaultProfile,
  fullName: "Ayesha Khan",
  country: "Pakistan",
  education: "Undergraduate",
  field: "Computer Science",
  graduationYear: "2027",
  skills: [
    "Python",
    "React",
    "AI",
    "Machine Learning",
    "Open Source",
  ],
  interests: [
    "Fellowship",
    "Open Source",
    "Hackathon",
    "Research",
  ],
  workMode: "Remote",
  preferredRegions: ["Global", "Europe", "Asia"],
  fundingPreference: "Fully funded or paid",
};

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function OrbitProvider({ children }) {
  const [auth, setAuth] = useState(
    () => localStorage.getItem("orbit_auth") === "1"
  );

  const [demoMode, setDemoMode] = useState(
    () => localStorage.getItem("orbit_demo") === "1"
  );

  const [profile, setProfileState] = useState(() =>
    localStorage.getItem("orbit_demo") === "1"
      ? readJson("orbit_demo_profile", demoProfile)
      : readJson("orbit_profile", defaultProfile)
  );

  const [opportunities, setOpportunities] =
    useState(opportunitySeed);

  const [saved, setSaved] = useState(() =>
    readJson("orbit_saved", {})
  );

  const [runs, setRuns] = useState(() =>
    readJson("orbit_runs", initialRuns)
  );

  const login = () => {
    localStorage.removeItem("orbit_demo");
    localStorage.removeItem("orbit_demo_profile");
    localStorage.setItem("orbit_auth", "1");

    setDemoMode(false);
    setProfileState(
      readJson("orbit_profile", defaultProfile)
    );
    setAuth(true);
  };

  const startDemo = () => {
    localStorage.setItem("orbit_demo", "1");
    localStorage.setItem(
      "orbit_demo_profile",
      JSON.stringify(demoProfile)
    );
    localStorage.setItem("orbit_auth", "1");

    setDemoMode(true);
    setProfileState(demoProfile);
    setAuth(true);
  };

  const logout = () => {
    localStorage.removeItem("orbit_auth");
    localStorage.removeItem("orbit_demo");
    localStorage.removeItem("orbit_demo_profile");

    setDemoMode(false);
    setProfileState(
      readJson("orbit_profile", defaultProfile)
    );
    setAuth(false);
  };

  const saveProfile = (next) => {
    setProfileState(next);

    localStorage.setItem(
      demoMode
        ? "orbit_demo_profile"
        : "orbit_profile",
      JSON.stringify(next)
    );
  };

  const toggleSave = (opp) => {
    setSaved((current) => {
      const next = { ...current };

      if (next[opp.id]) {
        delete next[opp.id];
      } else {
        next[opp.id] = {
          status: "saved",
          savedAt: new Date().toISOString(),
          snapshot: opp,
        };
      }

      localStorage.setItem(
        "orbit_saved",
        JSON.stringify(next)
      );

      return next;
    });
  };

  const setSavedStatus = (id, status) => {
    setSaved((current) => {
      if (!current[id]) return current;

      const next = {
        ...current,
        [id]: {
          ...current[id],
          status,
        },
      };

      localStorage.setItem(
        "orbit_saved",
        JSON.stringify(next)
      );

      return next;
    });
  };

  const addRun = (run) => {
    setRuns((current) => {
      const next = [run, ...current].slice(0, 8);

      localStorage.setItem(
        "orbit_runs",
        JSON.stringify(next)
      );

      return next;
    });
  };

  return (
    <OrbitContext.Provider
      value={{
        auth,
        demoMode,
        login,
        startDemo,
        logout,
        profile,
        saveProfile,
        opportunities,
        setOpportunities,
        saved,
        toggleSave,
        setSavedStatus,
        runs,
        addRun,
      }}
    >
      {children}
    </OrbitContext.Provider>
  );
}

function Protected({ children }) {
  const { auth } = useOrbit();

  return auth ? (
    children
  ) : (
    <Navigate to="/login" replace />
  );
}

function ShellRoute({ children }) {
  const { profile, logout } = useOrbit();

  return (
    <Protected>
      <AppShell
        profile={profile}
        onLogout={logout}
      >
        {children}
      </AppShell>
    </Protected>
  );
}

function LandingPage() {
  const navigate = useNavigate();
  const { startDemo } = useOrbit();

  const openDemo = () => {
    startDemo();
    navigate("/dashboard");
  };

  const examples = [
    {
      score: 96,
      title: "Open-source mentorship",
      meta: "Global · Paid · 235 days",
    },
    {
      score: 92,
      title: "AI research fellowship",
      meta: "Remote · Fully funded · 21 days",
    },
    {
      score: 89,
      title: "Build for Climate",
      meta: "Online · $10K prizes · 10 days",
    },
  ];

  return (
    <div className="min-h-screen overflow-hidden bg-[#f7f8fa] text-slate-950">
      <header className="mx-auto flex h-20 max-w-7xl items-center justify-between px-5 sm:px-8">
        <OrbitLogo />

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/login")}
            className="rounded-xl px-4 py-2.5 text-sm font-bold text-slate-600 hover:bg-white"
          >
            Sign in
          </button>

          <button
            onClick={() => navigate("/register")}
            className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-bold text-white shadow-sm"
          >
            Build my radar
          </button>
        </div>
      </header>

      <main>
        <section className="relative mx-auto max-w-7xl px-5 pb-20 pt-14 sm:px-8 lg:grid lg:grid-cols-[1.03fr_.97fr] lg:items-center lg:gap-14 lg:pb-28 lg:pt-20">
          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-600 shadow-sm">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Continuous opportunity intelligence
            </div>

            <h1 className="mt-7 text-5xl font-black leading-[0.98] tracking-[-0.05em] sm:text-6xl lg:text-7xl">
              Tell Orbit who you are once.{" "}
              <span className="text-blue-600">
                Never miss an opportunity again.
              </span>
            </h1>

            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
              Orbit discovers scholarships, fellowships,
              internships, hackathons and open-source
              programs, verifies the source, checks your
              fit, and ranks what deserves your attention.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <button
                onClick={() => navigate("/register")}
                className="flex items-center justify-center gap-2 rounded-2xl bg-slate-950 px-6 py-4 text-sm font-black text-white shadow-lg shadow-slate-950/10 transition hover:-translate-y-0.5"
              >
                Build my opportunity radar
                <ArrowRight size={16} />
              </button>

              <button
                onClick={openDemo}
                className="flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-6 py-4 text-sm font-black text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:text-blue-700"
              >
                Explore demo
                <Play size={15} />
              </button>
            </div>

            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-2">
                <CheckCircle2
                  size={15}
                  className="text-emerald-600"
                />
                Official-source verification
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2
                  size={15}
                  className="text-emerald-600"
                />
                Deadline intelligence
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2
                  size={15}
                  className="text-emerald-600"
                />
                Personal fit scoring
              </span>
            </div>
          </div>

          <div className="relative mt-14 lg:mt-0">
            <div className="absolute -inset-16 -z-10 rounded-full bg-blue-100/60 blur-3xl" />

            <div className="rounded-[30px] border border-slate-200 bg-white p-4 shadow-2xl shadow-slate-950/10 sm:p-6">
              <div className="flex items-center justify-between border-b border-slate-100 pb-5">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                    Your Opportunity Radar
                  </p>

                  <p className="mt-1 text-xl font-black">
                    37 high-fit matches
                  </p>
                </div>

                <div className="grid h-11 w-11 place-items-center rounded-2xl bg-blue-50 text-blue-600">
                  <Radar size={20} />
                </div>
              </div>

              <div className="mt-4 space-y-3">
                {examples.map((item) => (
                  <div
                    key={item.title}
                    className="flex items-center gap-4 rounded-2xl border border-slate-200 p-4"
                  >
                    <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-950 text-sm font-black text-white">
                      {item.score}%
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="font-black">
                        {item.title}
                      </div>

                      <div className="mt-1 truncate text-xs text-slate-500">
                        {item.meta}
                      </div>
                    </div>

                    <ArrowUpRight
                      size={17}
                      className="text-slate-400"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-4 rounded-2xl bg-slate-950 p-5 text-white">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-blue-300">
                  <Zap size={14} />
                  Orbit discovered this
                </div>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  A new remote AI fellowship matches your
                  Python + ML profile and closes in 21
                  days.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="border-y border-slate-200 bg-white">
          <div className="mx-auto grid max-w-7xl gap-px bg-slate-200 sm:grid-cols-3">
            {[
              [
                Search,
                "Discover",
                "Search public sources, feeds and listings for opportunities you may never think to query.",
              ],
              [
                ShieldCheck,
                "Verify",
                "Separate primary sources from stale aggregators and track when each record was last checked.",
              ],
              [
                Target,
                "Match",
                "Rank by your skills, eligibility, education, location preference and deadline usefulness.",
              ],
            ].map(([Icon, title, text]) => (
              <div
                key={title}
                className="bg-white p-8"
              >
                <Icon
                  size={23}
                  className="text-blue-600"
                />

                <h3 className="mt-5 text-xl font-black">
                  {title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {text}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
          <div className="grid gap-8 rounded-[32px] bg-slate-950 p-8 text-white sm:p-12 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-blue-300">
                The idea behind Orbit
              </p>

              <h2 className="mt-4 max-w-3xl text-3xl font-black tracking-tight sm:text-4xl">
                You can't search for an opportunity you
                don't know exists.
              </h2>

              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400">
                Stop repeating the same searches. Build
                your profile once and let the radar
                surface what is new, relevant and still
                actionable.
              </p>
            </div>

            <button
              onClick={() => navigate("/register")}
              className="rounded-2xl bg-white px-6 py-4 text-sm font-black text-slate-950"
            >
              Start building
              <ArrowRight
                size={15}
                className="ml-2 inline"
              />
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

function AuthPage({ mode }) {
  const navigate = useNavigate();
  const { login, profile } = useOrbit();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const isRegister = mode === "register";

  const submit = (e) => {
    e.preventDefault();

    if (
      !email ||
      !password ||
      (isRegister && !name)
    ) {
      return setError(
        "Complete the required fields to continue."
      );
    }

    login();

    if (isRegister || !profile?.fullName) {
      navigate("/onboarding", {
        state: { name },
      });
    } else {
      navigate("/dashboard");
    }
  };

  return (
    <div className="grid min-h-screen bg-[#f6f7f9] lg:grid-cols-[.9fr_1.1fr]">
      <div className="flex min-h-screen flex-col px-5 py-6 sm:px-10 lg:px-14">
        <Link to="/">
          <OrbitLogo />
        </Link>

        <div className="my-auto w-full max-w-md self-center py-12">
          <div className="text-xs font-bold uppercase tracking-[0.14em] text-blue-600">
            {isRegister
              ? "Create your radar"
              : "Welcome back"}
          </div>

          <h1 className="mt-3 text-4xl font-black tracking-tight">
            {isRegister
              ? "Find the opportunities meant for you."
              : "Your radar is still running."}
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-500">
            {isRegister
              ? "Start with an account, then tell Orbit what you study, build and care about."
              : "Sign in to review your newest matches and deadlines."}
          </p>

          <form
            onSubmit={submit}
            className="mt-8 space-y-4"
          >
            {isRegister && (
              <Field
                label="Full name"
                value={name}
                onChange={setName}
                placeholder="Your full name"
              />
            )}

            <Field
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              placeholder="you@example.com"
            />

            <Field
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="At least 8 characters"
            />

            {error && (
              <div className="flex items-center gap-2 rounded-xl border border-red-100 bg-red-50 px-3 py-2.5 text-xs font-semibold text-red-700">
                <AlertCircle size={14} />
                {error}
              </div>
            )}

            <button className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3.5 text-sm font-black text-white">
              {isRegister
                ? "Create account"
                : "Sign in"}

              <ArrowRight size={15} />
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-slate-500">
            {isRegister
              ? "Already have an account?"
              : "New to Orbit?"}{" "}
            <Link
              className="font-bold text-slate-950"
              to={
                isRegister
                  ? "/login"
                  : "/register"
              }
            >
              {isRegister
                ? "Sign in"
                : "Create account"}
            </Link>
          </p>

          <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 px-3 py-2.5 text-xs leading-5 text-blue-800">
            <strong>Frontend preview:</strong>{" "}
            authentication is local-only until the
            FastAPI backend is connected.
          </div>
        </div>
      </div>

      <div className="relative hidden overflow-hidden bg-slate-950 p-12 text-white lg:block">
        <div className="absolute inset-0 opacity-40 [background-image:radial-gradient(circle_at_30%_20%,#2563eb_0,transparent_26%),radial-gradient(circle_at_80%_70%,#0ea5e9_0,transparent_20%)]" />

        <div className="relative flex h-full flex-col justify-between">
          <div className="max-w-lg">
            <div className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-blue-200">
              Opportunity intelligence, not another job
              board
            </div>

            <h2 className="mt-8 text-5xl font-black leading-[1.02] tracking-tight">
              From scattered links to one ranked radar.
            </h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {[
              [Radar, "Continuous discovery"],
              [ShieldCheck, "Source verification"],
              [Target, "Personal matching"],
              [CalendarClock, "Deadline tracking"],
            ].map(([Icon, label]) => (
              <div
                key={label}
                className="rounded-2xl border border-white/10 bg-white/[0.05] p-4"
              >
                <Icon
                  size={18}
                  className="text-blue-300"
                />

                <div className="mt-3 text-sm font-bold">
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold text-slate-700">
        {label}
      </span>

      <input
        type={type}
        value={value}
        onChange={(e) =>
          onChange(e.target.value)
        }
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
      />
    </label>
  );
}

function CustomValueInput({
  placeholder,
  onAdd,
  buttonLabel = "Add",
}) {
  const [value, setValue] = useState("");

  const submit = () => {
    const clean = value.trim();

    if (!clean) return;

    onAdd(clean);
    setValue("");
  };

  return (
    <div className="mt-4 flex flex-col gap-2 sm:flex-row">
      <input
        value={value}
        onChange={(e) =>
          setValue(e.target.value)
        }
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            submit();
          }
        }}
        placeholder={placeholder}
        className="min-w-0 flex-1 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-50"
      />

      <button
        type="button"
        onClick={submit}
        className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs font-black text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
      >
        + {buttonLabel}
      </button>
    </div>
  );
}

function ResumeUpload({ onProfile }) {
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const educationMap = {
    high_school: "High School",
    undergraduate: "Undergraduate",
    graduate: "Graduate",
    postgraduate: "Postgraduate",
    recent_graduate: "Recent Graduate",
  };

  const uploadResume = async (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    setError("");
    setSuccess("");
    setFileName(file.name);

    const allowed =
      file.name.toLowerCase().endsWith(".pdf") ||
      file.name.toLowerCase().endsWith(".docx");

    if (!allowed) {
      setError("Please upload a PDF or DOCX CV.");
      return;
    }

    if (file.size > 6 * 1024 * 1024) {
      setError("CV must be smaller than 6 MB.");
      return;
    }

    const body = new FormData();
    body.append("file", file);

    try {
      setLoading(true);

      const API =
        process.env.REACT_APP_BACKEND_URL ||
        "http://localhost:8000";

      const response = await fetch(
        `${API}/api/profile/parse-resume`,
        {
          method: "POST",
          body,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Could not read this CV."
        );
      }

      const parsed = data?.profile || {};

      onProfile({
        fullName: parsed.fullName || undefined,
        country: parsed.country || undefined,

        education: parsed.educationLevel
          ? educationMap[parsed.educationLevel] ||
          parsed.educationLevel
          : undefined,

        field: parsed.fieldOfStudy || undefined,

        graduationYear:
          parsed.graduationYear !== null &&
            parsed.graduationYear !== undefined
            ? String(parsed.graduationYear)
            : undefined,

        skills: Array.isArray(parsed.skills)
          ? parsed.skills
          : undefined,

        interests: Array.isArray(parsed.interests)
          ? parsed.interests
          : undefined,

        institution: parsed.institution || undefined,

        experienceLevel:
          parsed.experienceLevel || undefined,
      });

      setSuccess(
        "CV read successfully — your profile has been pre-filled. Review it before continuing."
      );
    } catch (err) {
      setError(
        err?.message || "Unable to process CV."
      );
    } finally {
      setLoading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="rounded-[22px] border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-5">
      <div className="flex gap-4">
        <div className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-blue-600 text-white">
          <UploadCloud size={19} />
        </div>

        <div className="min-w-0 flex-1">
          <div className="text-sm font-black text-slate-950">
            Upload your CV
          </div>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Let Orbit read your CV and pre-fill your
            skills, education and background automatically.
          </p>

          <label className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-xs font-black text-white transition hover:bg-slate-800">
            {loading ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <FileText size={15} />
            )}

            {loading ? "Reading CV..." : "Choose CV"}

            <input
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={uploadResume}
              disabled={loading}
              className="hidden"
            />
          </label>

          <span className="ml-3 text-[11px] font-semibold text-slate-400">
            PDF or DOCX · max 6 MB
          </span>

          {fileName && (
            <div className="mt-3 text-xs font-bold text-slate-600">
              {fileName}
            </div>
          )}

          {loading && (
            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-blue-100">
              <div className="h-full w-2/3 animate-pulse rounded-full bg-blue-600" />
            </div>
          )}

          {success && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-3 text-xs font-semibold leading-5 text-emerald-800">
              <CheckCircle2
                size={15}
                className="mt-0.5 shrink-0"
              />
              {success}
            </div>
          )}

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-xl border border-red-100 bg-red-50 px-3 py-3 text-xs font-semibold leading-5 text-red-700">
              <AlertCircle
                size={15}
                className="mt-0.5 shrink-0"
              />
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function OnboardingPage() {
  const { profile, saveProfile } = useOrbit();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState(1);

  const [form, setForm] = useState({
    ...defaultProfile,
    ...profile,
    fullName:
      profile.fullName ||
      location.state?.name ||
      "",
  });

  const baseSkills = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "AI",
    "Machine Learning",
    "Data Science",
    "Cybersecurity",
    "UI/UX",
    "Open Source",
    "Rust",
    "Java",
    "C++",
    "Cloud",
    "DevOps",
  ];

  const baseInterests = [
    "Scholarship",
    "Internship",
    "Fellowship",
    "Hackathon",
    "Open Source",
    "Research",
    "Competition",
  ];

  const baseRegions = [
    "Global",
    "Europe",
    "North America",
    "Asia",
    "Middle East",
  ];

  const skills = [
    ...new Set([
      ...baseSkills,
      ...(form.skills || []),
    ]),
  ];

  const interests = [
    ...new Set([
      ...baseInterests,
      ...(form.interests || []),
    ]),
  ];

  const regions = [
    ...new Set([
      ...baseRegions,
      ...(form.preferredRegions || []),
    ]),
  ];

  const toggle = (key, value) =>
    setForm((f) => ({
      ...f,
      [key]: f[key].includes(value)
        ? f[key].filter(
          (x) => x !== value
        )
        : [...f[key], value],
    }));

  const addCustom = (key, value) =>
    setForm((f) => {
      const current = f[key] || [];

      if (
        current.some(
          (x) =>
            x.toLowerCase() ===
            value.toLowerCase()
        )
      ) {
        return f;
      }

      return {
        ...f,
        [key]: [...current, value],
      };
    });

  const complete = () => {
    saveProfile(form);
    navigate("/dashboard");
  };

  return (
    <Protected>
      <div className="min-h-screen bg-[#f6f7f9] px-5 py-6 sm:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center justify-between">
            <OrbitLogo />

            <div className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-slate-500 shadow-sm">
              Step {step} of 4
            </div>
          </div>

          <div className="mt-8 h-1.5 overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-blue-600 transition-all duration-300"
              style={{
                width: `${step * 25}%`,
              }}
            />
          </div>

          <div className="mt-8 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-9">
            {step === 1 && (
              <>
                <StepHeading
                  icon={UserRound}
                  eyebrow="About you"
                  title="Start with the context that changes eligibility."
                  text="A few details help Orbit understand which opportunities actually fit you. You can change everything later."
                />

                <div className="mt-8">
                  <div className="mt-8">
                    <ResumeUpload
                      onProfile={(parsed) =>
                        setForm((current) => ({
                          ...current,
                          ...Object.fromEntries(
                            Object.entries(parsed).filter(
                              ([, value]) =>
                                value !== undefined &&
                                value !== null &&
                                value !== ""
                            )
                          ),
                        }))
                      }
                    />
                  </div>

                  <div className="my-7 flex items-center gap-4">
                    <div className="h-px flex-1 bg-slate-100" />

                    <span className="text-[10px] font-black uppercase tracking-[0.14em] text-slate-400">
                      or enter manually
                    </span>

                    <div className="h-px flex-1 bg-slate-100" />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <Field
                      label="Full name"
                      value={form.fullName}
                      onChange={(v) =>
                        setForm({
                          ...form,
                          fullName: v,
                        })
                      }
                      placeholder="Your name"
                    />

                    <Field
                      label="Country"
                      value={form.country}
                      onChange={(v) =>
                        setForm({
                          ...form,
                          country: v,
                        })
                      }
                      placeholder="Pakistan"
                    />

                    <SelectField
                      label="Education level"
                      value={form.education}
                      onChange={(v) =>
                        setForm({
                          ...form,
                          education: v,
                        })
                      }
                      options={[
                        "High School",
                        "Undergraduate",
                        "Graduate",
                        "Postgraduate",
                        "Recent Graduate",
                      ]}
                    />

                    <Field
                      label="Field of study"
                      value={form.field}
                      onChange={(v) =>
                        setForm({
                          ...form,
                          field: v,
                        })
                      }
                      placeholder="Computer Science"
                    />

                    <Field
                      label="Graduation year"
                      value={form.graduationYear}
                      onChange={(v) =>
                        setForm({
                          ...form,
                          graduationYear: v,
                        })
                      }
                      placeholder="2027"
                    />
                  </div>
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <StepHeading
                  icon={Zap}
                  eyebrow="Skills"
                  title="What can you already build with?"
                  text="Choose the skills Orbit should use for matching. If yours is missing, type it below."
                />

                <div className="mt-8 flex flex-wrap gap-2.5">
                  {skills.map((s) => (
                    <Choice
                      key={s}
                      active={form.skills.includes(s)}
                      onClick={() =>
                        toggle("skills", s)
                      }
                    >
                      {s}
                    </Choice>
                  ))}
                </div>

                <CustomValueInput
                  placeholder="Type another skill, e.g. Flutter, Figma, Go..."
                  buttonLabel="Add skill"
                  onAdd={(value) =>
                    addCustom(
                      "skills",
                      value
                    )
                  }
                />
              </>
            )}

            {step === 3 && (
              <>
                <StepHeading
                  icon={Compass}
                  eyebrow="Opportunity interests"
                  title="What should Orbit keep on your radar?"
                  text="Pick the tracks you care about, or add any opportunity type that is not listed."
                />

                <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {interests.map((s) => (
                    <Choice
                      key={s}
                      active={form.interests.includes(
                        s
                      )}
                      onClick={() =>
                        toggle(
                          "interests",
                          s
                        )
                      }
                      block
                    >
                      {s}
                    </Choice>
                  ))}
                </div>

                <CustomValueInput
                  placeholder="Type another opportunity type..."
                  buttonLabel="Add type"
                  onAdd={(value) =>
                    addCustom(
                      "interests",
                      value
                    )
                  }
                />
              </>
            )}

            {step === 4 && (
              <>
                <StepHeading
                  icon={Globe2}
                  eyebrow="Preferences"
                  title="Define what a useful opportunity looks like."
                  text="These preferences help Orbit rank the strongest opportunities first."
                />

                <div className="mt-8 grid gap-5 sm:grid-cols-2">
                  <SelectField
                    label="Work mode"
                    value={form.workMode}
                    onChange={(v) =>
                      setForm({
                        ...form,
                        workMode: v,
                      })
                    }
                    options={[
                      "Remote",
                      "Hybrid",
                      "On-site",
                      "Any",
                    ]}
                  />

                  <SelectField
                    label="Funding preference"
                    value={
                      form.fundingPreference
                    }
                    onChange={(v) =>
                      setForm({
                        ...form,
                        fundingPreference: v,
                      })
                    }
                    options={[
                      "Fully funded or paid",
                      "Any funding",
                      "Prize opportunities",
                      "Unpaid is okay",
                    ]}
                  />

                  <div className="sm:col-span-2">
                    <div className="mb-2 text-xs font-bold text-slate-700">
                      Preferred regions
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {regions.map((r) => (
                        <Choice
                          key={r}
                          active={form.preferredRegions.includes(
                            r
                          )}
                          onClick={() =>
                            toggle(
                              "preferredRegions",
                              r
                            )
                          }
                        >
                          {r}
                        </Choice>
                      ))}
                    </div>

                    <CustomValueInput
                      placeholder="Type another country or region..."
                      buttonLabel="Add region"
                      onAdd={(value) =>
                        addCustom(
                          "preferredRegions",
                          value
                        )
                      }
                    />
                  </div>
                </div>
              </>
            )}

            <div className="mt-10 flex items-center justify-between border-t border-slate-100 pt-6">
              <button
                disabled={step === 1}
                onClick={() =>
                  setStep((s) =>
                    Math.max(1, s - 1)
                  )
                }
                className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold text-slate-500 transition hover:bg-slate-50 disabled:opacity-30"
              >
                <ArrowLeft size={15} />
                Back
              </button>

              {step < 4 ? (
                <button
                  onClick={() =>
                    setStep(
                      (s) => s + 1
                    )
                  }
                  className="flex items-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
                >
                  Continue
                  <ArrowRight size={15} />
                </button>
              ) : (
                <button
                  onClick={complete}
                  className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-black text-white transition hover:-translate-y-0.5 hover:bg-blue-700"
                >
                  Build my radar
                  <Radar size={15} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </Protected>
  );
}

function StepHeading({
  icon: Icon,
  eyebrow,
  title,
  text,
}) {
  return (
    <div className="flex gap-4">
      <div className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-slate-950 text-white">
        <Icon size={18} />
      </div>

      <div>
        <div className="text-[10px] font-bold uppercase tracking-[0.15em] text-blue-600">
          {eyebrow}
        </div>

        <h1 className="mt-1 text-2xl font-black tracking-tight sm:text-3xl">
          {title}
        </h1>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          {text}
        </p>
      </div>
    </div>
  );
}

function Choice({
  active,
  onClick,
  children,
  block = false,
}) {
  return (
    <button
      onClick={onClick}
      className={`${block
        ? "w-full justify-between"
        : ""
        } flex items-center gap-2 rounded-xl border px-4 py-3 text-sm font-bold transition ${active
          ? "border-slate-950 bg-slate-950 text-white"
          : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
        }`}
    >
      {children}

      {active && <Check size={14} />}
    </button>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold text-slate-700">
        {label}
      </span>

      <div className="relative">
        <select
          value={value}
          onChange={(e) =>
            onChange(e.target.value)
          }
          className="w-full appearance-none rounded-xl border border-slate-200 bg-white px-4 py-3 pr-10 text-sm font-medium outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
        >
          {options.map((o) => (
            <option key={o}>
              {o}
            </option>
          ))}
        </select>

        <ChevronDown
          size={15}
          className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
      </div>
    </label>
  );
}

function DashboardPage() {
  const {
    profile,
    opportunities,
    saved,
    toggleSave,
  } = useOrbit();

  const top = [...opportunities]
    .sort((a, b) => b.match - a.match)
    .slice(0, 4);

  const closing = opportunities.filter(
    (x) => x.daysRemaining <= 30
  ).length;

  const fresh = opportunities.filter(
    (x) => x.isNew
  ).length;

  const savedCount =
    Object.keys(saved).length;

  return (
    <ShellRoute>
      <section className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.15em] text-blue-600">
            Your Opportunity Radar
          </div>

          <h1 className="mt-2 text-3xl font-black tracking-tight sm:text-4xl">
            Good afternoon
            {profile.fullName
              ? `, ${profile.fullName.split(
                " "
              )[0]
              }`
              : ""}
            .
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Orbit found{" "}
            {opportunities.length}{" "}
            opportunities worth ranking
            against your current profile.
          </p>
        </div>

        <Link
          to="/discover"
          className="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white"
        >
          Explore all matches
          <ArrowRight size={15} />
        </Link>
      </section>

      <section className="mt-7 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Recommended"
          value={
            opportunities.filter(
              (x) => x.match >= 80
            ).length
          }
          hint="80%+ profile fit"
          icon={Target}
          tone="slate"
        />

        <MetricCard
          label="Closing soon"
          value={closing}
          hint="Within 30 days"
          icon={CalendarClock}
          tone="white"
        />

        <MetricCard
          label="New today"
          value={fresh}
          hint="Recently discovered"
          icon={Zap}
          tone="blue"
        />

        <MetricCard
          label="Saved"
          value={savedCount}
          hint="Your shortlist"
          icon={Bookmark}
          tone="white"
        />
      </section>

      <section className="mt-8 grid gap-6 xl:grid-cols-[1fr_330px]">
        <div>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-black">
                Top matches
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Ranked from your profile and
                opportunity metadata.
              </p>
            </div>

            <Link
              to="/discover"
              className="text-xs font-bold text-blue-600"
            >
              View all
            </Link>
          </div>

          <div className="space-y-3">
            {top.map((opp) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                saved={Boolean(
                  saved[opp.id]
                )}
                onToggleSave={
                  toggleSave
                }
              />
            ))}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-[24px] bg-slate-950 p-6 text-white shadow-sm">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-blue-300">
              <WandSparkles size={15} />
              Match intelligence
            </div>

            <div className="mt-5 text-4xl font-black">
              96%
            </div>

            <p className="mt-2 text-sm font-bold">
              Your strongest current fit
            </p>

            <p className="mt-3 text-xs leading-6 text-slate-400">
              Open-source programs are
              ranking highest because your
              profile combines Python,
              React and an explicit Open
              Source interest.
            </p>

            <Link
              to="/discover"
              className="mt-5 flex items-center gap-2 text-xs font-bold text-white"
            >
              See why
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="rounded-[24px] border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black">
                Profile signal
              </h3>

              <span className="rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold text-emerald-700">
                Strong
              </span>
            </div>

            <div className="mt-5 space-y-4">
              <Signal
                label="Skills"
                value={Math.min(
                  100,
                  profile.skills.length *
                  16 +
                  20
                )}
              />

              <Signal
                label="Preferences"
                value={82}
              />

              <Signal
                label="Eligibility data"
                value={76}
              />
            </div>

            <Link
              to="/profile"
              className="mt-5 inline-flex text-xs font-bold text-blue-600"
            >
              Improve profile →
            </Link>
          </div>

          <div className="rounded-[24px] border border-blue-100 bg-blue-50 p-6">
            <div className="flex items-center gap-2 text-xs font-black text-blue-800">
              <Radar size={15} />
              Radar health
            </div>

            <p className="mt-3 text-sm leading-6 text-blue-950">
              Last discovery run
              succeeded. New data is ready
              for ranking.
            </p>

            <Link
              to="/ingestion"
              className="mt-4 inline-flex text-xs font-black text-blue-700"
            >
              Open Radar Status →
            </Link>
          </div>
        </aside>
      </section>
    </ShellRoute>
  );
}

function Signal({ label, value }) {
  return (
    <div>
      <div className="flex justify-between text-xs font-bold">
        <span>{label}</span>

        <span className="text-slate-400">
          {value}%
        </span>
      </div>

      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-slate-950"
          style={{
            width: `${value}%`,
          }}
        />
      </div>
    </div>
  );
}

function DiscoverPage() {
  const {
    opportunities,
    setOpportunities,
    saved,
    toggleSave,
  } = useOrbit();

  const [q, setQ] = useState("");
  const [category, setCategory] =
    useState("All");
  const [workMode, setWorkMode] =
    useState("Any");
  const [funding, setFunding] =
    useState("Any");
  const [deadline, setDeadline] =
    useState("Any");
  const [minMatch, setMinMatch] =
    useState(0);
  const [sort, setSort] =
    useState("Best match");

  const [aiQuery, setAiQuery] =
    useState("");

  const [aiAnswer, setAiAnswer] =
    useState(null);

  const [discovering, setDiscovering] =
    useState(false);

  const [phase, setPhase] =
    useState("");

  const filtered = useMemo(() => {
    let data = opportunities.filter(
      (o) => {
        const hay =
          `${o.title} ${o.organization} ${o.category} ${o.matchedSkills.join(
            " "
          )}`.toLowerCase();

        const matchesQ =
          !q ||
          hay.includes(
            q.toLowerCase()
          );

        const matchesCategory =
          category === "All" ||
          o.category === category;

        const matchesMode =
          workMode === "Any" ||
          o.workMode === workMode ||
          (workMode === "Remote" &&
            o.remote);

        const matchesFunding =
          funding === "Any" ||
          (funding ===
            "Funded/Paid" &&
            [
              "Paid",
              "Fully funded",
            ].includes(
              o.fundingType
            )) ||
          o.fundingType === funding;

        const matchesDeadline =
          deadline === "Any" ||
          (deadline === "≤ 14 days" &&
            o.daysRemaining <= 14) ||
          (deadline === "≤ 30 days" &&
            o.daysRemaining <= 30) ||
          (deadline === "≤ 60 days" &&
            o.daysRemaining <= 60);

        return (
          matchesQ &&
          matchesCategory &&
          matchesMode &&
          matchesFunding &&
          matchesDeadline &&
          o.match >=
          Number(minMatch)
        );
      }
    );

    if (sort === "Best match") {
      data = [...data].sort(
        (a, b) =>
          b.match - a.match
      );
    }

    if (sort === "Newest") {
      data = [...data].sort(
        (a, b) =>
          Number(b.isNew) -
          Number(a.isNew)
      );
    }

    if (sort === "Deadline soon") {
      data = [...data].sort(
        (a, b) =>
          a.daysRemaining -
          b.daysRemaining
      );
    }

    return data;
  }, [
    opportunities,
    q,
    category,
    workMode,
    funding,
    deadline,
    minMatch,
    sort,
  ]);

  const askOrbit = () => {
    if (!aiQuery.trim()) return;

    const lower =
      aiQuery.toLowerCase();

    let result = [
      ...opportunities,
    ];

    if (
      lower.includes("funded") ||
      lower.includes("paid")
    ) {
      result = result.filter((o) =>
        [
          "Paid",
          "Fully funded",
        ].includes(o.fundingType)
      );
    }

    if (lower.includes("ai")) {
      result = result.filter(
        (o) =>
          o.matchedSkills.some(
            (s) =>
              [
                "AI",
                "Machine Learning",
                "Python",
              ].includes(s)
          ) ||
          o.title
            .toLowerCase()
            .includes("ai")
      );
    }

    if (lower.includes("remote")) {
      result = result.filter(
        (o) => o.remote
      );
    }

    if (
      lower.includes("hackathon")
    ) {
      result = result.filter(
        (o) =>
          o.category === "Hackathon"
      );
    }

    if (
      lower.includes("fellowship")
    ) {
      result = result.filter(
        (o) =>
          o.category ===
          "Fellowship" ||
          o.category === "Research"
      );
    }

    result = result
      .sort(
        (a, b) =>
          b.match - a.match
      )
      .slice(0, 4);

    setAiAnswer({
      text: `I found ${result.length} strong local-preview matches for that request. In the backend build, Groq will translate this query into validated filters and explain the evidence behind each match.`,
      results: result,
    });
  };

  const liveSearch = () => {
    if (discovering) return;

    setDiscovering(true);
    setPhase(
      "Searching public sources…"
    );

    setTimeout(() => {
      setPhase(
        "Checking candidate pages…"
      );
    }, 700);

    setTimeout(() => {
      setPhase(
        "Normalizing and deduplicating…"
      );
    }, 1400);

    setTimeout(() => {
      const id =
        "demo-new-radar";

      if (
        !opportunities.some(
          (o) => o.id === id
        )
      ) {
        setOpportunities(
          (prev) => [
            {
              id,
              title:
                "Responsible AI Builders Program",
              organization:
                "Open Technology Collective",
              category: "Fellowship",
              match: 91,
              deadline:
                "2026-09-12",
              daysRemaining: 35,
              location: "Global",
              remote: true,
              workMode: "Remote",
              funding:
                "Funded cohort",
              fundingType:
                "Fully funded",
              verified: true,
              isNew: true,
              lastChecked:
                "just now",
              sourceUrl:
                "https://example.org/responsible-ai-builders",
              applicationUrl:
                "https://example.org/responsible-ai-builders/apply",
              shortDescription:
                "A newly discovered remote program for technical students building responsible AI prototypes with mentor support.",
              description:
                "A cohort-based technical program focused on practical responsible AI systems.",
              eligibility: [
                "Technical student or early-career builder",
                "Global applications",
              ],
              requirements: [
                "Python or JavaScript",
                "Short project idea",
              ],
              benefits: [
                "Funded cohort",
                "Mentorship",
              ],
              matchedSkills: [
                "AI",
                "Python",
                "React",
              ],
              gaps: [
                "Prepare a concise project proposal",
              ],
            },
            ...prev,
          ]
        );
      }

      setPhase(
        "1 new opportunity discovered"
      );

      setDiscovering(false);
    }, 2200);
  };

  return (
    <ShellRoute>
      <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.15em] text-blue-600">
            Discover
          </div>

          <h1 className="mt-2 text-3xl font-black tracking-tight">
            Find what deserves your
            attention.
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Search the current radar,
            ask Orbit in natural
            language, or trigger a live
            discovery preview.
          </p>
        </div>

        <button
          onClick={liveSearch}
          className="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white disabled:opacity-60"
          disabled={discovering}
        >
          {discovering ? (
            <Loader2
              size={15}
              className="animate-spin"
            />
          ) : (
            <Globe2 size={15} />
          )}

          Search live web
        </button>
      </div>

      {phase && (
        <div
          className={`mt-5 flex items-center gap-2 rounded-xl border px-4 py-3 text-xs font-bold ${discovering
            ? "border-blue-100 bg-blue-50 text-blue-800"
            : "border-emerald-100 bg-emerald-50 text-emerald-800"
            }`}
        >
          {discovering ? (
            <Loader2
              size={14}
              className="animate-spin"
            />
          ) : (
            <CheckCircle2 size={14} />
          )}

          {phase}

          <span className="ml-auto font-medium opacity-70">
            Frontend preview
          </span>
        </div>
      )}

      <section className="mt-6 rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.14em] text-blue-600">
          <WandSparkles size={15} />
          Ask Orbit
        </div>

        <div className="mt-3 flex flex-col gap-3 lg:flex-row">
          <div className="relative flex-1">
            <Sparkles
              size={17}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
            />

            <input
              value={aiQuery}
              onChange={(e) =>
                setAiQuery(
                  e.target.value
                )
              }
              onKeyDown={(e) =>
                e.key === "Enter" &&
                askOrbit()
              }
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-4 pl-11 pr-4 text-sm outline-none focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-50"
              placeholder="Find fully funded AI opportunities for Pakistani undergraduates closing soon…"
            />
          </div>

          <button
            onClick={askOrbit}
            className="rounded-2xl bg-blue-600 px-6 py-4 text-sm font-black text-white"
          >
            Ask Orbit
          </button>
        </div>

        {aiAnswer && (
          <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/70 p-4">
            <p className="text-sm leading-6 text-blue-950">
              {aiAnswer.text}
            </p>

            <div className="mt-3 flex flex-wrap gap-2">
              {aiAnswer.results.map(
                (o) => (
                  <Link
                    key={o.id}
                    to={`/opportunities/${o.id}`}
                    className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-blue-700 shadow-sm"
                  >
                    {o.match}% ·{" "}
                    {o.title}
                  </Link>
                )
              )}
            </div>
          </div>
        )}
      </section>

      <section className="mt-5 rounded-[24px] border border-slate-200 bg-white p-4 shadow-sm">
        <div className="relative">
          <Search
            size={17}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            value={q}
            onChange={(e) =>
              setQ(e.target.value)
            }
            className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-4 text-sm outline-none focus:border-blue-400"
            placeholder="Search opportunities, organizations or skills…"
          />
        </div>

        <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-6">
          <FilterSelect
            value={category}
            onChange={setCategory}
            options={[
              "All",
              "Fellowship",
              "Internship",
              "Scholarship",
              "Hackathon",
              "Open Source",
              "Research",
              "Competition",
            ]}
          />

          <FilterSelect
            value={workMode}
            onChange={setWorkMode}
            options={[
              "Any",
              "Remote",
              "Hybrid",
              "On-site",
            ]}
          />

          <FilterSelect
            value={funding}
            onChange={setFunding}
            options={[
              "Any",
              "Funded/Paid",
              "Fully funded",
              "Paid",
              "Prize",
            ]}
          />

          <FilterSelect
            value={deadline}
            onChange={setDeadline}
            options={[
              "Any",
              "≤ 14 days",
              "≤ 30 days",
              "≤ 60 days",
            ]}
          />

          <FilterSelect
            value={String(
              minMatch
            )}
            onChange={setMinMatch}
            options={[
              "0",
              "70",
              "80",
              "90",
            ]}
            labels={{
              0: "Any match",
              70: "70%+",
              80: "80%+",
              90: "90%+",
            }}
          />

          <FilterSelect
            value={sort}
            onChange={setSort}
            options={[
              "Best match",
              "Newest",
              "Deadline soon",
            ]}
          />
        </div>
      </section>

      <div className="mt-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black">
            {filtered.length} opportunities
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Showing results from the
            current local radar.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <Filter size={14} />
          Filters active
        </div>
      </div>

      <div className="mt-4 grid gap-3 xl:grid-cols-2">
        {filtered.map((o) => (
          <OpportunityCard
            key={o.id}
            opportunity={o}
            saved={Boolean(
              saved[o.id]
            )}
            onToggleSave={
              toggleSave
            }
          />
        ))}

        {filtered.length === 0 && (
          <Empty
            title="No matches in this view"
            text="Relax a filter or search for a different keyword."
          />
        )}
      </div>
    </ShellRoute>
  );
}

function FilterSelect({
  value,
  onChange,
  options,
  labels = {},
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) =>
          onChange(e.target.value)
        }
        className="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-xs font-bold text-slate-600 outline-none"
      >
        {options.map((o) => (
          <option
            key={o}
            value={o}
          >
            {labels[o] || o}
          </option>
        ))}
      </select>

      <ChevronDown
        size={13}
        className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400"
      />
    </div>
  );
}

function OpportunityDetailPage() {
  const { id } = useParams();

  const {
    opportunities,
    saved,
    toggleSave,
    setSavedStatus,
  } = useOrbit();

  const navigate = useNavigate();

  const opp =
    opportunities.find(
      (x) => x.id === id
    ) || saved[id]?.snapshot;

  if (!opp) {
    return (
      <ShellRoute>
        <Empty
          title="Opportunity not found"
          text="It may have expired or been removed from the active radar."
          action={
            <button
              onClick={() =>
                navigate(
                  "/discover"
                )
              }
              className="rounded-xl bg-slate-950 px-4 py-2.5 text-xs font-bold text-white"
            >
              Back to discover
            </button>
          }
        />
      </ShellRoute>
    );
  }

  const isSaved = Boolean(
    saved[opp.id]
  );

  return (
    <ShellRoute>
      <button
        onClick={() => navigate(-1)}
        className="mb-5 flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-slate-950"
      >
        <ArrowLeft size={14} />
        Back
      </button>

      <div className="grid gap-6 xl:grid-cols-[1fr_330px]">
        <div className="space-y-5">
          <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-blue-50 px-3 py-1 text-[10px] font-black uppercase tracking-[0.12em] text-blue-700">
                    {opp.category}
                  </span>

                  {opp.verified && (
                    <span className="flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-[10px] font-black uppercase tracking-[0.12em] text-emerald-700">
                      <CheckCircle2
                        size={12}
                      />
                      Verified source
                    </span>
                  )}
                </div>

                <h1 className="mt-4 max-w-3xl text-3xl font-black tracking-tight sm:text-4xl">
                  {opp.title}
                </h1>

                <p className="mt-2 text-sm font-semibold text-slate-500">
                  {opp.organization}
                </p>
              </div>

              <div className="rounded-2xl bg-slate-950 px-5 py-4 text-center text-white">
                <div className="text-3xl font-black">
                  {opp.match}%
                </div>

                <div className="mt-1 text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Profile match
                </div>
              </div>
            </div>

            <p className="mt-6 max-w-3xl text-sm leading-7 text-slate-600">
              {opp.description}
            </p>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <MiniStat
                icon={CalendarClock}
                label="Deadline"
                value={`${opp.daysRemaining} days left`}
              />

              <MiniStat
                icon={MapPin}
                label="Location"
                value={opp.location}
              />

              <MiniStat
                icon={Globe2}
                label="Work mode"
                value={opp.workMode}
              />

              <MiniStat
                icon={Sparkles}
                label="Funding"
                value={opp.funding}
              />
            </div>

            <div className="mt-7 flex flex-col gap-3 border-t border-slate-100 pt-6 sm:flex-row">
              <button
                onClick={() =>
                  toggleSave(opp)
                }
                className={`flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-black ${isSaved
                  ? "border border-blue-200 bg-blue-50 text-blue-700"
                  : "border border-slate-200 bg-white text-slate-700"
                  }`}
              >
                <Bookmark size={16} />

                {isSaved
                  ? "Saved"
                  : "Save opportunity"}
              </button>

              <a
                href={
                  opp.applicationUrl
                }
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white"
              >
                Apply on official site
                <ExternalLink
                  size={15}
                />
              </a>
            </div>
          </section>

          <section className="grid gap-5 lg:grid-cols-2">
            <InfoPanel
              icon={Target}
              title="Why this matches you"
              tone="blue"
            >
              {opp.matchedSkills.map(
                (s) => (
                  <CheckLine key={s}>
                    {s} aligns with your
                    current profile
                  </CheckLine>
                )
              )}

              <p className="mt-4 text-xs leading-6 text-slate-500">
                Orbit will replace this
                preview logic with
                deterministic backend
                scoring plus optional AI
                explanation.
              </p>
            </InfoPanel>

            <InfoPanel
              icon={ShieldCheck}
              title="Eligibility"
              tone="green"
            >
              {opp.eligibility.map(
                (x) => (
                  <CheckLine key={x}>
                    {x}
                  </CheckLine>
                )
              )}
            </InfoPanel>

            <InfoPanel
              icon={FileCheck2}
              title="Requirements"
            >
              {opp.requirements.map(
                (x) => (
                  <CheckLine key={x}>
                    {x}
                  </CheckLine>
                )
              )}
            </InfoPanel>

            <InfoPanel
              icon={Trophy}
              title="Benefits"
            >
              {opp.benefits.map(
                (x) => (
                  <CheckLine key={x}>
                    {x}
                  </CheckLine>
                )
              )}
            </InfoPanel>
          </section>

          <section className="rounded-[24px] border border-amber-100 bg-amber-50 p-6">
            <div className="flex items-center gap-2 text-sm font-black text-amber-950">
              <AlertCircle size={17} />
              Potential gaps
            </div>

            <div className="mt-4 space-y-2">
              {opp.gaps.map((g) => (
                <div
                  key={g}
                  className="rounded-xl bg-white/70 px-4 py-3 text-sm text-amber-950"
                >
                  {g}
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="space-y-4">
          <div className="rounded-[24px] border border-slate-200 bg-white p-6">
            <h3 className="text-sm font-black">
              Source confidence
            </h3>

            <div className="mt-5 flex items-center gap-3">
              <div
                className={`grid h-10 w-10 place-items-center rounded-xl ${opp.verified
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-amber-50 text-amber-700"
                  }`}
              >
                {opp.verified ? (
                  <ShieldCheck
                    size={19}
                  />
                ) : (
                  <AlertCircle
                    size={19}
                  />
                )}
              </div>

              <div>
                <p className="text-xs font-black">
                  {opp.verified
                    ? "Official / primary source"
                    : "Needs verification"}
                </p>

                <p className="mt-1 text-[11px] text-slate-400">
                  Last checked{" "}
                  {opp.lastChecked}
                </p>
              </div>
            </div>

            <a
              href={opp.sourceUrl}
              target="_blank"
              rel="noreferrer"
              className="mt-5 flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 text-xs font-bold text-slate-700"
            >
              View original source
              <ArrowUpRight
                size={14}
              />
            </a>
          </div>

          {isSaved && (
            <div className="rounded-[24px] border border-slate-200 bg-white p-6">
              <h3 className="text-sm font-black">
                Application status
              </h3>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                Saved snapshots remain
                available even if the
                master opportunity later
                expires.
              </p>

              <div className="mt-4 grid gap-2">
                {[
                  ["saved", "Saved"],
                  [
                    "planning",
                    "Planning to apply",
                  ],
                  [
                    "applied",
                    "Applied",
                  ],
                  [
                    "expired",
                    "Expired / closed",
                  ],
                ].map(
                  ([
                    value,
                    label,
                  ]) => (
                    <button
                      key={value}
                      onClick={() =>
                        setSavedStatus(
                          opp.id,
                          value
                        )
                      }
                      className={`flex items-center justify-between rounded-xl border px-3 py-2.5 text-xs font-bold ${saved[
                        opp.id
                      ]?.status ===
                        value
                        ? "border-slate-950 bg-slate-950 text-white"
                        : "border-slate-200 text-slate-600"
                        }`}
                    >
                      {label}

                      {saved[
                        opp.id
                      ]?.status ===
                        value && (
                          <Check
                            size={13}
                          />
                        )}
                    </button>
                  )
                )}
              </div>
            </div>
          )}
        </aside>
      </div>
    </ShellRoute>
  );
}

function MiniStat({
  icon: Icon,
  label,
  value,
}) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <Icon
        size={16}
        className="text-slate-500"
      />

      <div className="mt-3 text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">
        {label}
      </div>

      <div className="mt-1 text-xs font-black text-slate-800">
        {value}
      </div>
    </div>
  );
}

function InfoPanel({
  icon: Icon,
  title,
  children,
  tone,
}) {
  return (
    <div
      className={`rounded-[24px] border p-6 ${tone === "blue"
        ? "border-blue-100 bg-blue-50/50"
        : tone === "green"
          ? "border-emerald-100 bg-emerald-50/50"
          : "border-slate-200 bg-white"
        }`}
    >
      <div className="flex items-center gap-2 text-sm font-black">
        <Icon size={17} />
        {title}
      </div>

      <div className="mt-4 space-y-3">
        {children}
      </div>
    </div>
  );
}

function CheckLine({ children }) {
  return (
    <div className="flex gap-2.5 text-sm leading-6 text-slate-700">
      <CheckCircle2
        size={15}
        className="mt-1 shrink-0 text-emerald-600"
      />

      {children}
    </div>
  );
}

function SavedPage() {
  const {
    saved,
    toggleSave,
    setSavedStatus,
  } = useOrbit();

  const [tab, setTab] =
    useState("saved");

  const records = Object.values(
    saved
  ).filter(
    (r) => r.status === tab
  );

  const tabs = [
    ["saved", "Saved"],
    ["planning", "Planning"],
    ["applied", "Applied"],
    ["expired", "Expired"],
  ];

  return (
    <ShellRoute>
      <div>
        <div className="text-xs font-bold uppercase tracking-[0.15em] text-blue-600">
          Saved
        </div>

        <h1 className="mt-2 text-3xl font-black tracking-tight">
          Your opportunity shortlist.
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Track intent without turning
          Orbit into a heavyweight
          application CRM.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {tabs.map(
          ([value, label]) => (
            <button
              key={value}
              onClick={() =>
                setTab(value)
              }
              className={`rounded-xl px-4 py-2.5 text-xs font-black ${tab === value
                ? "bg-slate-950 text-white"
                : "border border-slate-200 bg-white text-slate-600"
                }`}
            >
              {label}

              <span className="ml-1 opacity-60">
                {
                  Object.values(
                    saved
                  ).filter(
                    (r) =>
                      r.status ===
                      value
                  ).length
                }
              </span>
            </button>
          )
        )}
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-2">
        {records.map((r) => (
          <div
            key={r.snapshot.id}
            className="space-y-2"
          >
            <OpportunityCard
              opportunity={
                r.snapshot
              }
              saved
              onToggleSave={
                toggleSave
              }
            />

            {tab !== "expired" && (
              <div className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-2">
                {tab !==
                  "planning" && (
                    <button
                      onClick={() =>
                        setSavedStatus(
                          r.snapshot
                            .id,
                          "planning"
                        )
                      }
                      className="rounded-lg px-3 py-2 text-[11px] font-bold text-slate-600 hover:bg-slate-50"
                    >
                      Planning
                    </button>
                  )}

                {tab !==
                  "applied" && (
                    <button
                      onClick={() =>
                        setSavedStatus(
                          r.snapshot
                            .id,
                          "applied"
                        )
                      }
                      className="rounded-lg px-3 py-2 text-[11px] font-bold text-slate-600 hover:bg-slate-50"
                    >
                      Mark applied
                    </button>
                  )}

                <button
                  onClick={() =>
                    setSavedStatus(
                      r.snapshot.id,
                      "expired"
                    )
                  }
                  className="rounded-lg px-3 py-2 text-[11px] font-bold text-slate-400 hover:bg-slate-50"
                >
                  Archive
                </button>
              </div>
            )}
          </div>
        ))}

        {records.length === 0 && (
          <Empty
            title={`No ${tabs
              .find(
                (x) =>
                  x[0] === tab
              )?.[1]
              .toLowerCase()
              } opportunities`}
            text="Save a strong match or move an existing item into this status."
          />
        )}
      </div>
    </ShellRoute>
  );
}

function IngestionPage() {
  const {
    runs,
    addRun,
    opportunities,
    setOpportunities,
  } = useOrbit();

  const [running, setRunning] =
    useState(false);

  const [progress, setProgress] =
    useState(0);

  const [message, setMessage] =
    useState("");

  const latest = runs[0];

  const runNow = () => {
    if (running) return;

    setRunning(true);
    setProgress(12);
    setMessage(
      "Loading source registry…"
    );

    const steps = [
      [
        500,
        30,
        "Discovering RSS, sitemap and listing URLs…",
      ],
      [
        1100,
        54,
        "Fetching new and changed candidate pages…",
      ],
      [
        1700,
        76,
        "Normalizing, deduplicating and scoring…",
      ],
      [
        2300,
        94,
        "Expiring stale records and saving run metrics…",
      ],
    ];

    steps.forEach(
      ([ms, p, m]) =>
        setTimeout(() => {
          setProgress(p);
          setMessage(m);
        }, ms)
    );

    setTimeout(() => {
      const run = {
        id: Date.now(),
        started: "Just now",
        status: "Success",
        sources: 14,
        urls: 86,
        newCount: 7,
        updated: 3,
        expired: 2,
        aiCalls: 9,
      };

      addRun(run);

      if (
        !opportunities.some(
          (o) =>
            o.id ===
            "radar-status-demo"
        )
      ) {
        setOpportunities(
          (prev) => [
            {
              ...opportunitySeed[2],
              id: "radar-status-demo",
              title:
                "Applied AI Student Fellowship",
              organization:
                "Open Research Collective",
              match: 93,
              isNew: true,
              lastChecked:
                "just now",
            },
            ...prev,
          ]
        );
      }

      setProgress(100);

      setMessage(
        "Discovery completed — 7 new opportunities normalized."
      );

      setRunning(false);
    }, 3000);
  };

  const sources = [
    {
      name:
        "Official program feeds",
      type: "RSS / listing",
      status: "Healthy",
      last: "8 min ago",
    },
    {
      name:
        "Public opportunity sitemaps",
      type: "Sitemap",
      status: "Healthy",
      last: "9 min ago",
    },
    {
      name:
        "University opportunity pages",
      type: "HTTP",
      status: "Healthy",
      last: "10 min ago",
    },
    {
      name:
        "Optional SearXNG discovery",
      type: "Search",
      status: "Not configured",
      last: "—",
    },
  ];

  return (
    <ShellRoute>
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.15em] text-blue-600">
            Radar Status
          </div>

          <h1 className="mt-2 text-3xl font-black tracking-tight">
            Discovery engine visibility.
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            A judge-friendly view of
            what the recurring opportunity
            pipeline is doing.
          </p>
        </div>

        <button
          onClick={runNow}
          disabled={running}
          className="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white disabled:opacity-60"
        >
          {running ? (
            <Loader2
              size={15}
              className="animate-spin"
            />
          ) : (
            <Play size={15} />
          )}

          Run Discovery now
        </button>
      </div>

      <div className="mt-5 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-xs leading-5 text-amber-900">
        <strong>
          Frontend preview:
        </strong>{" "}
        these controls simulate the
        final interaction. Once FastAPI
        is connected, every metric and
        run row must come from real
        ingestion records.
      </div>

      {(running || message) && (
        <div className="mt-4 rounded-2xl border border-blue-100 bg-white p-4">
          <div className="flex items-center justify-between text-xs font-bold">
            <span>{message}</span>
            <span>{progress}%</span>
          </div>

          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-600 transition-all"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>
        </div>
      )}

      <section className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Sources scanned"
          value={
            latest?.sources || 0
          }
          hint="Latest discovery run"
          icon={Globe2}
          tone="slate"
        />

        <MetricCard
          label="URLs discovered"
          value={latest?.urls || 0}
          hint="Candidate pages"
          icon={Search}
          tone="white"
        />

        <MetricCard
          label="New opportunities"
          value={
            latest?.newCount || 0
          }
          hint="Normalized records"
          icon={Zap}
          tone="blue"
        />

        <MetricCard
          label="Expired"
          value={
            latest?.expired || 0
          }
          hint="Removed from active feed"
          icon={Clock3}
          tone="white"
        />
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-black">
                Recent runs
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Cron and manual
                ingestion history.
              </p>
            </div>

            <RefreshCw
              size={16}
              className="text-slate-400"
            />
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  <th className="pb-3">
                    Started
                  </th>

                  <th className="pb-3">
                    Status
                  </th>

                  <th className="pb-3">
                    URLs
                  </th>

                  <th className="pb-3">
                    New
                  </th>

                  <th className="pb-3">
                    Updated
                  </th>

                  <th className="pb-3">
                    AI calls
                  </th>
                </tr>
              </thead>

              <tbody>
                {runs.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-slate-50"
                  >
                    <td className="py-4 font-bold">
                      {r.started}
                    </td>

                    <td>
                      <span
                        className={`rounded-full px-2 py-1 text-[10px] font-black ${r.status ===
                          "Success"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-amber-50 text-amber-700"
                          }`}
                      >
                        {r.status}
                      </span>
                    </td>

                    <td>{r.urls}</td>

                    <td>
                      {r.newCount}
                    </td>

                    <td>
                      {r.updated}
                    </td>

                    <td>
                      {r.aiCalls}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-200 bg-white p-5">
          <div>
            <h2 className="text-lg font-black">
              Source health
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Primary discovery
              adapters and optional
              search layer.
            </p>
          </div>

          <div className="mt-5 space-y-3">
            {sources.map((s) => (
              <div
                key={s.name}
                className="flex items-center gap-3 rounded-2xl border border-slate-100 p-4"
              >
                <div
                  className={`grid h-9 w-9 place-items-center rounded-xl ${s.status ===
                    "Healthy"
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-slate-100 text-slate-500"
                    }`}
                >
                  <Database size={16} />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="truncate text-xs font-black">
                    {s.name}
                  </div>

                  <div className="mt-1 text-[10px] text-slate-400">
                    {s.type} · {s.last}
                  </div>
                </div>

                <div
                  className={`text-[10px] font-black ${s.status ===
                    "Healthy"
                    ? "text-emerald-700"
                    : "text-slate-400"
                    }`}
                >
                  {s.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </ShellRoute>
  );
}

function ProfilePage() {
  const {
    profile,
    saveProfile,
  } = useOrbit();

  const [form, setForm] =
    useState(profile);

  const [
    savedMsg,
    setSavedMsg,
  ] = useState(false);

  const baseSkills = [
    "Python",
    "JavaScript",
    "React",
    "AI",
    "Machine Learning",
    "Data Science",
    "Open Source",
    "Cloud",
    "DevOps",
    "UI/UX",
  ];

  const baseInterests = [
    "Scholarship",
    "Internship",
    "Fellowship",
    "Hackathon",
    "Open Source",
    "Research",
    "Competition",
  ];

  const baseRegions = [
    "Global",
    "Europe",
    "North America",
    "Asia",
    "Middle East",
  ];

  const skills = [
    ...new Set([
      ...baseSkills,
      ...(form.skills || []),
    ]),
  ];

  const interests = [
    ...new Set([
      ...baseInterests,
      ...(form.interests || []),
    ]),
  ];

  const regions = [
    ...new Set([
      ...baseRegions,
      ...(form.preferredRegions ||
        []),
    ]),
  ];

  const toggle = (key, value) =>
    setForm((f) => ({
      ...f,
      [key]: f[key].includes(value)
        ? f[key].filter(
          (x) => x !== value
        )
        : [...f[key], value],
    }));

  const addCustom = (key, value) =>
    setForm((f) => {
      const current = f[key] || [];

      if (
        current.some(
          (x) =>
            x.toLowerCase() ===
            value.toLowerCase()
        )
      ) {
        return f;
      }

      return {
        ...f,
        [key]: [...current, value],
      };
    });

  const save = () => {
    saveProfile(form);

    setSavedMsg(true);

    setTimeout(
      () => setSavedMsg(false),
      1800
    );
  };

  return (
    <ShellRoute>
      <div>
        <div className="text-xs font-bold uppercase tracking-[0.15em] text-blue-600">
          Profile
        </div>

        <h1 className="mt-2 text-3xl font-black tracking-tight">
          Tune your recommendation
          signal.
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Add as much context as you
          want. Orbit uses it to improve
          eligibility and ranking.
        </p>
      </div>

      <div className="mt-6 grid gap-5 xl:grid-cols-[1fr_330px]">
        <section className="rounded-[24px] border border-slate-200 bg-white p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label="Full name"
              value={form.fullName}
              onChange={(v) =>
                setForm({
                  ...form,
                  fullName: v,
                })
              }
            />

            <Field
              label="Country"
              value={form.country}
              onChange={(v) =>
                setForm({
                  ...form,
                  country: v,
                })
              }
            />

            <SelectField
              label="Education"
              value={form.education}
              onChange={(v) =>
                setForm({
                  ...form,
                  education: v,
                })
              }
              options={[
                "High School",
                "Undergraduate",
                "Graduate",
                "Postgraduate",
                "Recent Graduate",
              ]}
            />

            <Field
              label="Field of study"
              value={form.field}
              onChange={(v) =>
                setForm({
                  ...form,
                  field: v,
                })
              }
            />

            <Field
              label="Graduation year"
              value={
                form.graduationYear
              }
              onChange={(v) =>
                setForm({
                  ...form,
                  graduationYear: v,
                })
              }
            />

            <SelectField
              label="Work mode"
              value={form.workMode}
              onChange={(v) =>
                setForm({
                  ...form,
                  workMode: v,
                })
              }
              options={[
                "Remote",
                "Hybrid",
                "On-site",
                "Any",
              ]}
            />

            <SelectField
              label="Funding preference"
              value={
                form.fundingPreference
              }
              onChange={(v) =>
                setForm({
                  ...form,
                  fundingPreference: v,
                })
              }
              options={[
                "Fully funded or paid",
                "Any funding",
                "Prize opportunities",
                "Unpaid is okay",
              ]}
            />
          </div>

          <div className="mt-7 border-t border-slate-100 pt-6">
            <div className="text-xs font-black">
              Skills
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {skills.map((s) => (
                <Choice
                  key={s}
                  active={form.skills.includes(
                    s
                  )}
                  onClick={() =>
                    toggle(
                      "skills",
                      s
                    )
                  }
                >
                  {s}
                </Choice>
              ))}
            </div>

            <CustomValueInput
              placeholder="Add another skill..."
              buttonLabel="Add skill"
              onAdd={(value) =>
                addCustom(
                  "skills",
                  value
                )
              }
            />
          </div>

          <div className="mt-7 border-t border-slate-100 pt-6">
            <div className="text-xs font-black">
              Opportunity interests
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {interests.map((s) => (
                <Choice
                  key={s}
                  active={form.interests.includes(
                    s
                  )}
                  onClick={() =>
                    toggle(
                      "interests",
                      s
                    )
                  }
                >
                  {s}
                </Choice>
              ))}
            </div>

            <CustomValueInput
              placeholder="Add another opportunity type..."
              buttonLabel="Add type"
              onAdd={(value) =>
                addCustom(
                  "interests",
                  value
                )
              }
            />
          </div>

          <div className="mt-7 border-t border-slate-100 pt-6">
            <div className="text-xs font-black">
              Preferred regions
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {regions.map((r) => (
                <Choice
                  key={r}
                  active={form.preferredRegions.includes(
                    r
                  )}
                  onClick={() =>
                    toggle(
                      "preferredRegions",
                      r
                    )
                  }
                >
                  {r}
                </Choice>
              ))}
            </div>

            <CustomValueInput
              placeholder="Add another country or region..."
              buttonLabel="Add region"
              onAdd={(value) =>
                addCustom(
                  "preferredRegions",
                  value
                )
              }
            />
          </div>

          <div className="mt-7 flex items-center justify-between border-t border-slate-100 pt-6">
            <div className="text-xs font-semibold text-emerald-700">
              {savedMsg
                ? "Profile saved ✓"
                : ""}
            </div>

            <button
              onClick={save}
              className="rounded-xl bg-slate-950 px-5 py-3 text-sm font-black text-white transition hover:-translate-y-0.5 hover:bg-slate-800"
            >
              Save profile
            </button>
          </div>
        </section>

        <aside className="space-y-4">
          <div className="rounded-[24px] bg-slate-950 p-6 text-white">
            <GraduationCap
              size={20}
              className="text-blue-300"
            />

            <h3 className="mt-4 text-lg font-black">
              Profile completeness
            </h3>

            <div className="mt-4 text-4xl font-black">
              84%
            </div>

            <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full w-[84%] rounded-full bg-blue-500" />
            </div>

            <p className="mt-4 text-xs leading-6 text-slate-400">
              More context gives Orbit
              stronger evidence for
              eligibility and matching.
            </p>
          </div>

          <div className="rounded-[24px] border border-slate-200 bg-white p-6">
            <h3 className="text-sm font-black">
              Current signals
            </h3>

            <div className="mt-4 space-y-3 text-xs">
              {[
                [
                  "Country",
                  form.country,
                ],
                [
                  "Education",
                  form.education,
                ],
                [
                  "Skills",
                  `${form.skills.length} selected`,
                ],
                [
                  "Interests",
                  `${form.interests.length} selected`,
                ],
                [
                  "Regions",
                  `${form.preferredRegions.length} selected`,
                ],
              ].map(([k, v]) => (
                <div
                  key={k}
                  className="flex justify-between gap-3"
                >
                  <span className="text-slate-400">
                    {k}
                  </span>

                  <span className="text-right font-bold">
                    {v}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </ShellRoute>
  );
}

function Empty({
  title,
  text,
  action,
}) {
  return (
    <div className="col-span-full rounded-[24px] border border-dashed border-slate-300 bg-white p-10 text-center">
      <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-500">
        <Compass size={20} />
      </div>

      <h3 className="mt-4 text-lg font-black">
        {title}
      </h3>

      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
        {text}
      </p>

      {action && (
        <div className="mt-5">
          {action}
        </div>
      )}
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={<LandingPage />}
      />

      <Route
        path="/login"
        element={
          <AuthPage mode="login" />
        }
      />

      <Route
        path="/register"
        element={
          <AuthPage mode="register" />
        }
      />

      <Route
        path="/onboarding"
        element={<OnboardingPage />}
      />

      <Route
        path="/dashboard"
        element={<DashboardPage />}
      />

      <Route
        path="/discover"
        element={<DiscoverPage />}
      />

      <Route
        path="/opportunities/:id"
        element={
          <OpportunityDetailPage />
        }
      />

      <Route
        path="/saved"
        element={<SavedPage />}
      />

      <Route
        path="/ingestion"
        element={<IngestionPage />}
      />

      <Route
        path="/profile"
        element={<ProfilePage />}
      />

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <OrbitProvider>
        <AppRoutes />
      </OrbitProvider>
    </BrowserRouter>
  );
}