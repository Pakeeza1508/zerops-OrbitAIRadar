// Browser + real backend Phase 4 acceptance, isolated MongoDB; Python handles mocked HTTP ingestion.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const crypto = require("node:crypto");
const BASE = "http://127.0.0.1:8000";
const WEB = "http://127.0.0.1:3000";
const results = [];
const test = async (n, label, fn) => {
  try { await fn(); results.push({n,label,status:"PASS"}); console.log("PHASE4 CASE "+n+" PASS "+label); }
  catch(e) { results.push({n,label,status:"FAIL",error:String(e.message||e)}); console.error("PHASE4 CASE "+n+" FAIL "+label,e.stack||e); }
};
async function request(path,{token,method="GET",body}={}) {
  const r=await fetch(BASE+path,{method,headers:{"Content-Type":"application/json",...(token?{Authorization:"Bearer "+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})});
  return {status:r.status, data:await r.json().catch(()=>({}))};
}
async function browserPage(browser,token){
  const ctx=await browser.newContext();
  await ctx.addInitScript(jwt=>sessionStorage.setItem("orbit_access_token",jwt),token);
  return await ctx.newPage();
}
let browser;
(async()=>{
  browser=await chromium.launch({headless:true});
  const reg=await request("/api/auth/register",{method:"POST",body:{
    email:"phase4-browser-"+crypto.randomUUID().slice(0,12)+"@example.com",
    password:"Phase4-Isolated-Browser-8491",
    fullName:"Phase4 browser user",
  }});
  assert.equal(reg.status,200,JSON.stringify(reg.data));
  const user=reg.data.accessToken;
  const page=await browserPage(browser,user);
  await test(1,"Empty Radar run history and source rows strictly from API",async()=>{
    const api=await request("/api/ingestion/runs",{token:user});
    assert.equal(api.status,200);
    assert.equal(api.data.items.length,0);
    await page.goto(WEB+"/ingestion");
    await page.getByText("No ingestion runs recorded yet.").waitFor({timeout:25000});
    const sources=await request("/api/ingestion/sources",{token:user});
    assert.equal(sources.status,200);
    assert.ok(sources.data.items.length>0);
    for(const item of sources.data.items) await page.getByText(item.name,{exact:true}).first().waitFor();
  });
  await test(2,"Non-admin UI never exposes manual discovery",async()=>{
    await page.getByText("Manual discovery is restricted to administrators.").waitFor();
    assert.equal(await page.getByRole("button",{name:"Run Discovery now"}).count(),0);
    const cap=await request("/api/ingestion/capabilities",{token:user});
    assert.deepEqual(cap.data,{canRunManual:false});
  });
  await test(3,"Controlled ingestion and both endpoint authorization checks",async()=>{
    const run=spawnSync("python",["../backend/tests/phase4_ingestion_ci.py"],{encoding:"utf8",env:process.env,maxBuffer:1024*1024});
    console.log(run.stdout);
    if(run.status!==0)throw Error("Controlled backend test failed: "+run.stderr+" "+run.stdout);
    for(let n=1;n<=4;n++)assert.ok(run.stdout.includes("PHASE4 BACKEND CASE "+n+" PASS"));
  });
  await test(4,"Run history, metrics and source health reflect real API rows",async()=>{
    const api=await request("/api/ingestion/runs",{token:user});
    assert.equal(api.status,200);
    assert.equal(api.data.items.length,1);
    const actual=api.data.items[0];
    assert.equal(actual.newCount,1);
    assert.equal(actual.sourcesAttempted,1);
    await page.reload();
    await page.getByText("Run history",{exact:true}).waitFor({timeout:25000});
    const metrics=page.locator("section").filter({hasText:"Run history"});
    await metrics.getByRole("button",{name:"View run"}).click();
    await page.getByText("Run details",{exact:true}).waitFor();
    await page.getByText(/Discovered: 1/).waitFor();
    const sources=await request("/api/ingestion/sources",{token:user});
    const mock=sources.data.items.find(x=>x.name==="Phase4 mock-only source");
    assert.ok(mock);
    assert.ok(mock.lastSuccessAt);
    const row=page.locator("tr").filter({hasText:mock.name});
    await row.getByText("Healthy",{exact:true}).waitFor();
    assert.equal(await page.locator("tbody tr").filter({hasText:actual.status}).count()>=1,true);
  });
  await test(5,"Discovered opportunity visible on real Discover page",async()=>{
    const resp=await request("/api/opportunities?q=Orbit%20Phase4%20Controlled%20Fellowship%202027",{token:user});
    assert.equal(resp.status,200);
    assert.equal(resp.data.total,1);
    await page.goto(WEB+"/discover");
    await page.getByText("Orbit Phase4 Controlled Fellowship 2027").waitFor({timeout:25000});
  });
  await test(6,"Admin sees Run Now; no fake run persistence/source",async()=>{
    const login=await request("/api/auth/login",{method:"POST",body:{
      email:"phase4-admin-ci@example.com",password:"Phase4-Isolated-Test-Only-Password-8491",
    }});
    assert.equal(login.status,200,JSON.stringify(login.data));
    const admin=await browserPage(browser,login.data.accessToken);
    await admin.goto(WEB+"/ingestion");
    await admin.getByRole("button",{name:"Run Discovery now"}).waitFor({timeout:25000});
    const src=fs.readFileSync("src/App.js","utf8");
    for(const old of ["initialRuns","orbit_runs","addRun","setTimeout(() => { const run"])assert.equal(src.includes(old),false,old);
    assert.equal(await admin.evaluate(()=>localStorage.getItem("orbit_runs")),null);
    await admin.close();
  });
})().catch(e=>console.error("PHASE4 HARNESS FAILURE",e.stack||e)).finally(async()=>{
  if(browser)await browser.close();
  for(let n=1;n<=6;n++)if(!results.some(x=>x.n===n))results.push({n,status:"FAIL",label:"Not reached"});
  results.sort((a,b)=>a.n-b.n);
  fs.mkdirSync("test-results",{recursive:true});
  fs.writeFileSync("test-results/phase4-results.json",JSON.stringify(results,null,2));
  console.log("=== PHASE 4 ACCEPTANCE ===");
  for(const r of results)console.log(r.n+" "+r.status+" "+r.label+(r.error?" "+r.error:""));
  process.exitCode=results.some(r=>r.status!=="PASS")?1:0;
});
