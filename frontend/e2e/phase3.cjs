// Phase 3 acceptance: real browser, unmodified FastAPI routes, isolated MongoDB.
// This script creates ONLY guarded CI fixtures via ../backend/tests/phase3_seed.py.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const crypto = require("node:crypto");
const BASE = "http://127.0.0.1:8000";
const WEB = "http://127.0.0.1:3000";
const suff = crypto.randomUUID().slice(0, 12);
const results = [];
let browser, userA, userB, pageA, pageB, oppId;
async function req(path, { token, method="GET", body }={}) {
  const response = await fetch(BASE + path, {method,
    headers: {"Content-Type":"application/json",...(token?{Authorization:"Bearer "+token}:{})},
    ...(body===undefined?{}:{body:JSON.stringify(body)})
  });
  return {status:response.status, data:await response.json().catch(()=>({}))};
}
async function register(name,email) {
  const r=await req("/api/auth/register",{method:"POST",body:{email,password:"Phase3-Only-Test-Passphrase-8491",fullName:name}});
  assert.equal(r.status,200,JSON.stringify(r.data));
  assert.ok(r.data.accessToken);
  return r.data.accessToken;
}
async function test(n,label,fn) {
  try {await fn();results.push({n,label,status:"PASS"});console.log("PHASE3 CASE "+n+" PASS "+label);}
  catch(e){results.push({n,label,status:"FAIL",error:String(e.message||e)});console.error("PHASE3 CASE "+n+" FAIL "+label,e.stack||e);}
}
async function browserFor(token) {
  const context=await browser.newContext();
  await context.addInitScript(jwt=>sessionStorage.setItem("orbit_access_token",jwt),token);
  const page=await context.newPage();
  return page;
}
function seed() {
  const r=spawnSync("python",["../backend/tests/phase3_seed.py"],{encoding:"utf8",env:process.env});
  if(r.status!==0)throw Error("Isolated seed failed: "+r.stdout+" "+r.stderr);
}
(async()=>{
  browser=await chromium.launch({headless:true});
  userA=await register("Phase Three Alice","phase3-a-"+suff+"@example.com");
  userB=await register("Phase Three Bob","phase3-b-"+suff+"@example.com");
  pageA=await browserFor(userA);pageB=await browserFor(userB);
  await test(1,"Dashboard/Discover show backend-only data and empty states",async()=>{
    let initial=await req("/api/opportunities",{token:userA});
    assert.equal(initial.status,200);
    assert.equal(initial.data.total,0,"Test database must initially contain zero opportunities");
    await pageA.goto(WEB+"/dashboard");
    await pageA.getByText("No active opportunities are available yet.").waitFor({timeout:25000});
    await pageA.goto(WEB+"/discover");
    await pageA.getByText("No matches in this view").waitFor({timeout:25000});
    seed(); // Test only. Never production Atlas.
    await pageA.reload();
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:25000});
    await pageA.getByText("Orbit Phase3 Test Internship 2027").waitFor({timeout:25000});
    assert.equal(await pageA.getByText("Google Summer of Code 2027").count(),0);
    const r=await req("/api/opportunities?sort=best_match&pageSize=100",{token:userA});
    assert.equal(r.status,200);assert.equal(r.data.total,2);
    oppId=r.data.items.find(x=>x.title==="Orbit Phase3 Test Fellowship 2027").id;
    assert.ok(oppId);
    await pageA.goto(WEB+"/dashboard");
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:25000});
  });
  await test(2,"Server-driven category/remote/funded filters and sorting",async()=>{
    await pageA.goto(WEB+"/discover");
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:25000});
    const selects=pageA.locator('select');
    await selects.nth(0).selectOption({label:"Fellowship"});
    await pageA.getByText("Orbit Phase3 Test Internship 2027").waitFor({state:"detached",timeout:25000});
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor();
    await selects.nth(0).selectOption({label:"All"});
    await selects.nth(1).selectOption({label:"Remote"});
    await pageA.getByText("Orbit Phase3 Test Internship 2027").waitFor({state:"detached",timeout:25000});
    await selects.nth(1).selectOption({label:"Any"});
    await selects.nth(2).selectOption({label:"Funded/Paid"});
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor();
    await pageA.getByText("Orbit Phase3 Test Internship 2027").waitFor({state:"detached",timeout:25000});
    await selects.nth(2).selectOption({label:"Any"});
    await selects.nth(5).selectOption({label:"Deadline soon"});
    await pageA.getByText("Orbit Phase3 Test Internship 2027").waitFor({timeout:25000});
    const api=await req("/api/opportunities?sort=deadline&pageSize=100",{token:userA});
    assert.equal(api.status,200);
    assert.deepEqual(api.data.items.map(x=>x.title),["Orbit Phase3 Test Fellowship 2027","Orbit Phase3 Test Internship 2027"]);
  });
  await test(3,"Two users isolated; save/status/unsave persist through reload",async()=>{
    assert.ok(oppId,"Opportunity prerequisite failed");
    await pageA.goto(WEB+"/discover");
    const article=pageA.locator("article").filter({hasText:"Orbit Phase3 Test Fellowship 2027"});
    await article.getByRole("button",{name:"Save opportunity"}).click();
    await article.getByRole("button",{name:"Remove saved opportunity"}).waitFor({timeout:20000});
    const records=await req("/api/saved",{token:userA});
    assert.equal(records.status,200);assert.equal(records.data.total,1);
    const other=await req("/api/saved",{token:userB});
    assert.equal(other.status,200);assert.equal(other.data.total,0);
    await pageA.goto(WEB+"/saved");
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:25000});
    await pageA.getByRole("button",{name:"Planning",exact:true}).last().click();
    await pageA.getByRole("button",{name:/Planning/}).first().click();
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:20000});
    await pageA.reload();
    await pageA.getByRole("button",{name:/Planning/}).first().click();
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:25000});
    const after=await req("/api/saved",{token:userA});
    assert.equal(after.data.items[0].applicationStatus,"planning");
    await pageA.getByRole("button",{name:"Mark applied",exact:true}).click();
    await pageA.getByRole("button",{name:/Applied/}).first().click();
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:20000});
    await pageA.reload();
    await pageA.getByRole("button",{name:/Applied/}).first().click();
    await pageA.getByText("Orbit Phase3 Test Fellowship 2027").waitFor({timeout:20000});
    const applied=await req("/api/saved",{token:userA});
    assert.equal(applied.data.items[0].applicationStatus,"applied");
    await pageA.goto(WEB+"/discover");
    const savedCard=pageA.locator("article").filter({hasText:"Orbit Phase3 Test Fellowship 2027"});
    await savedCard.getByRole("button",{name:"Remove saved opportunity"}).click();
    await savedCard.getByRole("button",{name:"Save opportunity"}).waitFor({timeout:20000});
    await pageA.reload();
    const afterRemove=await req("/api/saved",{token:userA});
    assert.equal(afterRemove.data.total,0);
    const otherStill=await req("/api/saved",{token:userB});
    assert.equal(otherStill.data.total,0);
  });
  await test(4,"Detail loads by API id; invalid id has clean not-found",async()=>{
    assert.ok(oppId,"Opportunity prerequisite failed");
    await pageA.goto(WEB+"/opportunities/"+oppId);
    await pageA.getByRole("heading",{name:"Orbit Phase3 Test Fellowship 2027"}).waitFor({timeout:25000});
    await pageA.getByRole("link",{name:"Apply on official site"}).waitFor({timeout:25000});
    await pageA.goto(WEB+"/opportunities/not-a-real-object-id");
    await pageA.getByRole("heading",{name:"Opportunity not found"}).waitFor({timeout:25000});
  });
  await test(5,"Ask Orbit shows actual backend response",async()=>{
    await pageA.goto(WEB+"/discover");
    const prompt="remote fellowship Python";
    const api=await req("/api/search/ai",{token:userA,method:"POST",body:{query:prompt}});
    assert.equal(api.status,200);
    await pageA.getByPlaceholder(/Find fully funded AI opportunities/).fill(prompt);
    await pageA.getByRole("button",{name:"Ask Orbit",exact:true}).click();
    await pageA.getByText(api.data.answer,{exact:true}).waitFor({timeout:30000});
    if(api.data.items.length){
      await pageA.getByText(api.data.items[0].title).first().waitFor();
    }
    assert.equal(await pageA.getByText("strong local-preview matches").count(),0);
  });
  await test(6,"No seed/localStorage opportunity paths; pipeline untouched by UI",async()=>{
    const source=fs.readFileSync("src/App.js","utf8");
    assert.equal(source.includes("opportunitySeed"),false);
    assert.equal(source.includes("orbit_saved"),false);
    assert.equal(source.includes("demo-new-radar"),false);
    const saved=await pageA.evaluate(()=>localStorage.getItem("orbit_saved"));
    assert.equal(saved,null);
    assert.equal(source.includes('"/api/search/live"'),false,"Frontend must not trigger ingestion");
  });
})().catch(e=>console.error("HARNESS FAILURE",e)).finally(async()=>{
  if(browser)await browser.close();
  for(let n=1;n<=6;n++)if(!results.some(r=>r.n===n))results.push({n,label:"Harness not reached",status:"FAIL"});
  results.sort((a,b)=>a.n-b.n);
  fs.mkdirSync("test-results",{recursive:true});
  fs.writeFileSync("test-results/phase3-results.json",JSON.stringify(results,null,2));
  if(process.env.GITHUB_STEP_SUMMARY){
    fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,"## Phase 3 isolated E2E results\n\n| # | Acceptance | Result |\n|---|---|---|\n"+results.map(r=>`| ${r.n} | ${r.label} | **${r.status}** |`).join("\n")+"\n");
  }
  console.log("=== PHASE 3 RESULTS ===");
  for(const r of results)console.log(r.n+" "+r.status+" "+r.label+(r.error?" "+r.error:""));
  process.exitCode=results.some(r=>r.status!=="PASS")?1:0;
});
