import time
from pathlib import Path
from playwright.sync_api import sync_playwright
D={l.split()[0]:float(l.split()[1]) for l in open("durations.txt")}
TXT={l.split("|")[0]:l.split("|")[1].strip() for l in open("segments.txt")}
PAD=0.6
CAP="""(t)=>{let c=document.getElementById('cap'); if(!c){c=document.createElement('div');c.id='cap';
 c.style.cssText='position:fixed;left:0;right:0;bottom:0;padding:22px 40px 26px;background:linear-gradient(transparent,rgba(0,0,0,.92) 35%);color:#fff;font:700 34px/1.25 -apple-system,system-ui;text-align:center;z-index:99;text-shadow:0 2px 8px #000';document.body.appendChild(c);} c.textContent=t;}"""
HOOK="""(t)=>{let h=document.getElementById('hook'); if(!h){h=document.createElement('div');h.id='hook';
 h.style.cssText='position:fixed;inset:0;background:radial-gradient(900px 500px at 50% 30%,#12324a,#05070b 70%);color:#fff;display:flex;align-items:center;justify-content:center;text-align:center;font:800 64px/1.1 -apple-system,system-ui;letter-spacing:-.02em;padding:60px;z-index:98;transition:opacity .4s';document.body.appendChild(h);} h.innerHTML=t; h.style.opacity=t?1:0; h.style.pointerEvents='none';}"""
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome")
    ctx=b.new_context(viewport={"width":1280,"height":720}, record_video_dir="raw", record_video_size={"width":1280,"height":720})
    pg=ctx.new_page(); pg.goto("http://localhost:8790"); pg.wait_for_timeout(1500)
    pg.evaluate("document.body.style.zoom='1.12'")
    t0=time.time(); marks={}
    def seg(k, act=None):
        marks[k]=time.time()-t0
        pg.evaluate(CAP, "" if k=="hook" else TXT[k])
        if act: act()
        left=D[k]+PAD-(time.time()-t0-marks[k])
        if left>0: pg.wait_for_timeout(int(left*1000))
    seg("hook", lambda: pg.evaluate(HOOK, "<div>Your AI agent just took a screenshot.<br><span style='color:#7dd3fc'>What did it see?</span></div>"))
    def prob():
        pg.evaluate(HOOK, ""); pg.locator("button.sample:has-text('chat personal')").click(); pg.wait_for_timeout(300)
        pg.evaluate("window.scrollTo({top: document.getElementById('orig').getBoundingClientRect().top+scrollY-90, behavior:'smooth'})")
    seg("problem", prob)
    seg("gate")
    seg("purpose", lambda: pg.locator("button:has-text('training')").first.click())
    def ask():
        pg.locator("button:has-text('assistant')").first.click(); pg.wait_for_timeout(1400)
        pg.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); pg.wait_for_timeout(1200)
        pg.locator("button:has-text('Send it as')").first.click()
    seg("ask", ask)
    def inj():
        pg.locator("button.sample:has-text('agent inbox')").click(); pg.wait_for_timeout(300)
        pg.evaluate("window.scrollTo({top: document.getElementById('orig').getBoundingClientRect().top+scrollY-90, behavior:'smooth'})")
    seg("inject", inj)
    def cta():
        pg.evaluate("document.body.style.zoom='1'"); pg.evaluate("pitch(0)"); pg.wait_for_timeout(100)
        n=pg.evaluate("document.querySelectorAll('.slide').length")
        pg.evaluate(f"(()=>{{S={n-1};show();}})()")
    seg("cta", cta)
    marks["end"]=time.time()-t0
    vid=pg.video.path(); ctx.close(); b.close()
    Path("marks.txt").write_text("\n".join(f"{k} {v:.3f}" for k,v in marks.items()))
    print(vid, marks)
