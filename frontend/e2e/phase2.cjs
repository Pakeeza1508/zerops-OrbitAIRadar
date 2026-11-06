// Seven isolated end-to-end acceptance cases, real browser + FastAPI + MongoDB.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const WEB = "http://127.0.0.1:3000";
const API = "http://127.0.0.1:8000";
const suffix = crypto.randomUUID().slice(0, 12);
const emails = ["phase2-a-" + suffix + "@example.com", "phase2-b-" + suffix + "@example.com"];
const password = "Only-Test-Phase2-Strong-Password-8491";
const education = "Postgraduate";
const field = "Computer Science and Applied Mathematics";
const results = [];
let browser, first, second, tokenA, userA, pageA, snapshot;

async function request(path, opts = {}) {
  const res = await fetch(API + path, {
    method: opts.method || "GET",
    headers: { "Content-Type": "application/json", ...(opts.token ? {Authorization: "Bearer " + opts.token} : {}) },
    ...(opts.body === undefined ? {} : {body: JSON.stringify(opts.body)}),
  });
  return { status: res.status, body: await res.json().catch(() => ({})) };
}

async function check(n, title, fn) {
  try {
    await fn();
    results.push({ number:n, title, result:"PASS" });
    console.log("CASE " + n + " PASS: " + title);
  } catch(err) {
    results.push({ number:n, title, result:"FAIL", reason:String(err.message || err) });
    console.error("CASE " + n + " FAIL: " + title + ": " + String(err.stack || err));
  }
}

async function browserRegister(context, fullName, email) {
  const page = await context.newPage();
  await page.goto(WEB + "/register");
  await page.getByPlaceholder("Your full name").fill(fullName);
  await page.getByPlaceholder("you@example.com").fill(email);
  await page.getByPlaceholder("At least 8 characters").fill(password);
  await page.getByRole("button", {name:"Create account"}).click();
  await page.waitForURL(/\/onboarding$/, {timeout:20000});
  const token = await page.evaluate(() => sessionStorage.getItem("orbit_access_token"));
  assert.ok(token, "No JWT after registration");
  const me = await request("/api/auth/me", {token});
  assert.equal(me.status,200);
  assert.equal(me.body.email,email);
  return {page,token,id:me.body.id};
}

(async()=>{
  browser = await chromium.launch({headless:true});
  first = await browser.newContext();
  second = await browser.newContext();
  await check(1, "Two independent users register successfully", async()=>{
    const a = await browserRegister(first,"Phase Two Alice",emails[0]);
    const b = await browserRegister(second,"Phase Two Bob",emails[1]);
    pageA=a.page;tokenA=a.token;userA=a.id;
    assert.notEqual(a.id,b.id);
    assert.notEqual(a.token,b.token);
  });
  await check(2, "Wrong password is rejected", async()=>{
    const r = await request("/api/auth/login",{method:"POST",body:{email:emails[0],password:"wrong-password"}});
    assert.equal(r.status,401);
  });
  await check(3, "Valid session restored after refresh", async()=>{
    assert.ok(pageA,"registration prerequisite failed");
    // Registration lands on onboarding. Refresh that protected route rather
    // than racing a second navigation while React finishes the first one.
    await pageA.getByText("Step 1 of 4").waitFor({timeout:20000});
    await pageA.reload({waitUntil:"load"});
    await pageA.getByText("Step 1 of 4").waitFor({timeout:20000});
    assert.match(pageA.url(),/\/onboarding$/);
    assert.equal(await pageA.evaluate(()=>sessionStorage.getItem("orbit_access_token")),tokenA);
    const r=await request("/api/auth/me",{token:tokenA});
    assert.equal(r.status,200);assert.equal(r.body.id,userA);
  });

  await check(4, "educationLevel exact save and reload", async()=>{
    assert.ok(pageA,"registration prerequisite failed");
    // Case 3 has already restored the session on the onboarding route.
    await pageA.getByText("Step 1 of 4").waitFor({timeout:20000});
    await pageA.getByLabel("Full name").fill("Phase Two Alice");
    await pageA.getByLabel("Country").fill("Pakistan");
    await pageA.getByLabel("Education level").selectOption({label:education});
    await pageA.getByLabel("Field of study").fill(field);
    await pageA.getByLabel("Graduation year").fill("2027");
    await pageA.getByRole("button",{name:"Continue"}).click();
    await pageA.getByRole("button",{name:"Python",exact:true}).click();
    await pageA.getByRole("button",{name:"Continue"}).click();
    await pageA.getByRole("button",{name:"Hackathon",exact:true}).click();
    await pageA.getByRole("button",{name:"Continue"}).click();
    await pageA.getByLabel("Work mode").selectOption({label:"Remote"});
    await pageA.getByRole("button",{name:"Build my radar"}).click();
    await pageA.waitForURL(/\/dashboard$/, {timeout:20000});
    const stored=await request("/api/profile",{token:tokenA});
    assert.equal(stored.status,200);
    assert.equal(stored.body.educationLevel,education);
    await pageA.goto(WEB+"/profile");
    await pageA.reload();
    assert.match(pageA.url(),/\/profile$/);
    assert.equal(await pageA.getByLabel("Education",{exact:true}).inputValue(),education);
    snapshot=stored.body;
  });
  await check(5, "fieldOfStudy exact save and reload", async()=>{
    assert.ok(snapshot,"save/reload prerequisite failed");
    const stored=await request("/api/profile",{token:tokenA});
    assert.equal(stored.status,200);
    assert.equal(stored.body.fieldOfStudy,field);
    await pageA.reload();
    assert.equal(await pageA.getByLabel("Field of study").inputValue(),field);
  });
  await check(6, "Legacy orbit_auth localStorage alone cannot authenticate", async()=>{
    const isolated=await browser.newContext();
    await isolated.addInitScript(()=>{
      localStorage.setItem("orbit_auth","1");
      localStorage.setItem("orbit_demo","1");
    });
    const page=await isolated.newPage();
    await page.goto(WEB+"/dashboard");
    await page.waitForURL(/\/login$/, {timeout:20000});
    assert.equal(await page.evaluate(()=>localStorage.getItem("orbit_auth")),null);
    assert.equal(await page.evaluate(()=>sessionStorage.getItem("orbit_access_token")),null);
    await isolated.close();
  });
  await check(7, "Invalid JWT clears browser session", async()=>{
    const isolated=await browser.newContext();
    await isolated.addInitScript(()=>sessionStorage.setItem("orbit_access_token","invalid.jwt.token"));
    const page=await isolated.newPage();
    const apiResult=await request("/api/auth/me",{token:"invalid.jwt.token"});
    assert.equal(apiResult.status,401);
    await page.goto(WEB+"/dashboard");
    await page.waitForURL(/\/login$/, {timeout:20000});
    assert.equal(await page.evaluate(()=>sessionStorage.getItem("orbit_access_token")),null);
    await isolated.close();
  });
})().catch(e=>console.error("HARNESS ERROR",e)).finally(async()=>{
  if(browser)await browser.close();
  for(let n=1;n<=7;n++)if(!results.some(r=>r.number===n))results.push({number:n,title:"Not reached due to harness error",result:"FAIL"});
  results.sort((a,b)=>a.number-b.number);
  console.log("=== PHASE 2 SUMMARY ===");
  for(const r of results)console.log(r.number+". "+r.result+" "+r.title+(r.reason?": "+r.reason:""));
  fs.mkdirSync("test-results",{recursive:true});
  fs.writeFileSync("test-results/phase2-results.json",JSON.stringify(results,null,2));
  if(process.env.GITHUB_STEP_SUMMARY){
    const rows=results.map(r=>"| "+r.number+" | "+r.title+" | **"+r.result+"** |").join("\n");
    fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,"## Phase 2 isolated E2E\n\n| # | Case | Result |\n|---|---|---|\n"+rows+"\n");
  }
  process.exitCode=results.some(r=>r.result!=="PASS")?1:0;
});
