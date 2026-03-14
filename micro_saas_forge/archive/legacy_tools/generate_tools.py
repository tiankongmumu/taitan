"""
ShipMicro Tools — Batch Tool Generator
Generates 50 HTML5 single-file utility tools into public/tools/
"""
import os, json

OUT = r"d:\Project\1\micro_saas_forge\shipmicro_site\public\tools"
os.makedirs(OUT, exist_ok=True)
registry = []

def tool_html(title, accent, body_html, script, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title} | ShipMicro Tools</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0f172a;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;
min-height:100vh;min-height:100dvh;display:flex;align-items:center;justify-content:center;
padding:clamp(12px,3vw,24px)}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:clamp(12px,2vw,20px);
padding:clamp(16px,4vw,32px);width:100%;max-width:600px;box-shadow:0 25px 50px -12px rgba(0,0,0,.5)}}
h1{{font-size:clamp(18px,4vw,24px);color:{accent};margin-bottom:clamp(12px,3vw,20px);
display:flex;align-items:center;gap:8px;font-weight:800}}
textarea,input[type=text],input[type=number],select{{width:100%;
padding:clamp(8px,2vw,12px);background:#0f172a;border:1px solid #374151;
color:#e5e7eb;border-radius:clamp(6px,1.5vw,10px);font-family:inherit;
font-size:clamp(14px,3vw,16px);outline:none;resize:vertical}}
textarea:focus,input:focus,select:focus{{border-color:{accent}}}
input[type=color]{{height:clamp(40px,8vw,50px);padding:2px;border-radius:8px;
background:none;border:1px solid #374151;cursor:pointer}}
input[type=range]{{width:100%;accent-color:{accent}}}
input[type=checkbox]{{accent-color:{accent}}}
input[type=date]{{color-scheme:dark}}
.btn{{padding:clamp(8px,2vw,12px) clamp(16px,3vw,24px);background:{accent};color:#0f172a;
border:none;border-radius:clamp(6px,1.5vw,10px);font-weight:700;cursor:pointer;
font-size:clamp(13px,2.5vw,15px);transition:all .2s;font-family:inherit;
touch-action:manipulation}}
.btn:hover{{opacity:.9;transform:translateY(-1px)}}
.btn:active{{transform:scale(.97)}}
.row{{display:flex;gap:clamp(6px,1.5vw,10px);margin:clamp(8px,2vw,12px) 0;flex-wrap:wrap;align-items:center}}
.output{{background:#0f172a;border:1px solid #1e293b;border-radius:clamp(6px,1.5vw,10px);
padding:clamp(10px,2vw,14px);margin-top:clamp(8px,2vw,14px);
font-family:'SF Mono','Cascadia Code','Courier New',monospace;
font-size:clamp(12px,2.5vw,14px);white-space:pre-wrap;word-break:break-all;
min-height:40px;max-height:50vh;overflow:auto;line-height:1.5}}
label{{font-size:clamp(11px,2vw,13px);color:#94a3b8;display:block;
margin:clamp(6px,1.5vw,10px) 0 4px;text-transform:uppercase;letter-spacing:1px;font-weight:600}}
{extra_css}
</style></head><body>
<div class="card"><h1>{title}</h1>{body_html}</div>
<script>{script}</script>
</body></html>"""

# ============ TOOL DEFINITIONS ============
tools_data = [
  # --- TEXT TOOLS ---
  ("word-counter","Word Counter","📝","#60a5fa",False,"Text",
   '<textarea id="inp" rows="6" placeholder="Paste text here..."></textarea><div class="output" id="out">Words: 0 | Chars: 0 | Lines: 0</div>',
   'document.getElementById("inp").oninput=function(){let t=this.value;document.getElementById("out").textContent="Words: "+(t.trim()?t.trim().split(/\\s+/).length:0)+" | Chars: "+t.length+" | Lines: "+(t?t.split("\\n").length:0)+" | Sentences: "+(t.match(/[.!?]+/g)||[]).length}'),

  ("case-converter","Case Converter","🔤","#34d399",False,"Text",
   '<textarea id="inp" rows="4" placeholder="Type text..."></textarea><div class="row"><button class="btn" onclick="cv(s=>s.toUpperCase())">UPPER</button><button class="btn" onclick="cv(s=>s.toLowerCase())">lower</button><button class="btn" onclick="cv(s=>s.replace(/\\b\\w/g,c=>c.toUpperCase()))">Title</button><button class="btn" onclick="cv(s=>s.split(\' \').join(\'_\'))">snake_case</button><button class="btn" onclick="cv(s=>s.split(\' \').map((w,i)=>i?w[0].toUpperCase()+w.slice(1):w).join(\'\'))">camelCase</button></div><div class="output" id="out"></div>',
   'function cv(fn){let v=document.getElementById("inp").value;document.getElementById("out").textContent=fn(v)}'),

  ("lorem-generator","Lorem Generator","📜","#a78bfa",False,"Text",
   '<label>Paragraphs</label><input type="number" id="n" value="3" min="1" max="20"><button class="btn" onclick="gen()" style="margin-top:10px">Generate</button><div class="output" id="out"></div>',
   'const L="Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur".split(" ");function gen(){let n=+document.getElementById("n").value,o="";for(let i=0;i<n;i++){let p="";for(let j=0;j<40+Math.random()*30;j++)p+=L[Math.floor(Math.random()*L.length)]+" ";o+=p.trim()+".\\n\\n"}document.getElementById("out").textContent=o.trim()}gen()'),

  ("slug-generator","Slug Generator","🔗","#f472b6",False,"Text",
   '<textarea id="inp" rows="2" placeholder="Enter title..."></textarea><div class="output" id="out"></div>',
   'document.getElementById("inp").oninput=function(){document.getElementById("out").textContent=this.value.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")}'),

  ("text-reverser","Text Reverser","🔄","#fbbf24",False,"Text",
   '<textarea id="inp" rows="4" placeholder="Type text to reverse..."></textarea><div class="row"><button class="btn" onclick="r(1)">Reverse All</button><button class="btn" onclick="r(2)">Reverse Words</button><button class="btn" onclick="r(3)">Reverse Lines</button></div><div class="output" id="out"></div>',
   'function r(m){let t=document.getElementById("inp").value;let o=m===1?[...t].reverse().join(""):m===2?t.split(" ").reverse().join(" "):t.split("\\n").reverse().join("\\n");document.getElementById("out").textContent=o}'),

  ("line-sorter","Line Sorter","📊","#38bdf8",True,"Text",
   '<textarea id="inp" rows="6" placeholder="One item per line..."></textarea><div class="row"><button class="btn" onclick="s(1)">Sort A-Z</button><button class="btn" onclick="s(-1)">Sort Z-A</button><button class="btn" onclick="s(0)">Shuffle</button><button class="btn" onclick="dedup()">Deduplicate</button></div><div class="output" id="out"></div>',
   'function s(d){let a=document.getElementById("inp").value.split("\\n").filter(Boolean);if(d===0)a.sort(()=>Math.random()-.5);else a.sort((x,y)=>d*x.localeCompare(y));document.getElementById("out").textContent=a.join("\\n")}function dedup(){let a=[...new Set(document.getElementById("inp").value.split("\\n").filter(Boolean))];document.getElementById("out").textContent=a.join("\\n")}'),

  ("char-frequency","Char Frequency","📈","#e879f9",True,"Text",
   '<textarea id="inp" rows="4" placeholder="Paste text..."></textarea><button class="btn" onclick="analyze()" style="margin-top:8px">Analyze</button><div class="output" id="out"></div>',
   'function analyze(){let t=document.getElementById("inp").value,m={};[...t].forEach(c=>{if(c.trim())m[c]=(m[c]||0)+1});let s=Object.entries(m).sort((a,b)=>b[1]-a[1]).map(([k,v])=>k+" → "+v).join("\\n");document.getElementById("out").textContent=s||"No data"}'),

  ("markdown-preview","Markdown Preview","📝","#6ee7b7",True,"Text",
   '<textarea id="inp" rows="6" placeholder="# Hello\\n**Bold** *Italic*"></textarea><div class="output" id="out" style="color:#e5e7eb"></div>',
   'document.getElementById("inp").oninput=function(){let t=this.value.replace(/^### (.+)/gm,"<h3>$1</h3>").replace(/^## (.+)/gm,"<h2>$1</h2>").replace(/^# (.+)/gm,"<h1 style=\\"font-size:20px;color:#60a5fa\\">$1</h1>").replace(/\\*\\*(.+?)\\*\\*/g,"<strong>$1</strong>").replace(/\\*(.+?)\\*/g,"<em>$1</em>").replace(/`(.+?)`/g,"<code style=\\"background:#1f2937;padding:2px 4px;border-radius:4px\\">$1</code>").replace(/\\n/g,"<br>");document.getElementById("out").innerHTML=t};document.getElementById("inp").dispatchEvent(new Event("input"))'),

  # --- DEV TOOLS ---
  ("json-formatter","JSON Formatter","⚡","#fbbf24",False,"Code",
   '<textarea id="inp" rows="6" placeholder=\'{"key":"value"}\'></textarea><div class="row"><button class="btn" onclick="fmt()">Format</button><button class="btn" onclick="mini()">Minify</button><button class="btn" onclick="cp()">Copy</button></div><div class="output" id="out"></div>',
   'function fmt(){try{document.getElementById("out").textContent=JSON.stringify(JSON.parse(document.getElementById("inp").value),null,2)}catch(e){document.getElementById("out").textContent="Error: "+e.message}}function mini(){try{document.getElementById("out").textContent=JSON.stringify(JSON.parse(document.getElementById("inp").value))}catch(e){document.getElementById("out").textContent="Error: "+e.message}}function cp(){navigator.clipboard.writeText(document.getElementById("out").textContent)}'),

  ("base64-codec","Base64 Codec","🔐","#f472b6",False,"Code",
   '<textarea id="inp" rows="4" placeholder="Text or Base64..."></textarea><div class="row"><button class="btn" onclick="enc()">Encode</button><button class="btn" onclick="dec()">Decode</button></div><div class="output" id="out"></div>',
   'function enc(){document.getElementById("out").textContent=btoa(unescape(encodeURIComponent(document.getElementById("inp").value)))}function dec(){try{document.getElementById("out").textContent=decodeURIComponent(escape(atob(document.getElementById("inp").value)))}catch(e){document.getElementById("out").textContent="Invalid Base64"}}'),

  ("regex-tester","Regex Tester","🔍","#34d399",True,"Code",
   '<label>Pattern</label><input type="text" id="pat" placeholder="/pattern/flags"><label>Test String</label><textarea id="inp" rows="4" placeholder="Text to test..."></textarea><div class="output" id="out"></div>',
   'function test(){let p=document.getElementById("pat").value,t=document.getElementById("inp").value;try{let m=p.match(/^\\/(.+?)\\/([gimsy]*)$/);if(!m)throw"Use /pattern/flags format";let r=new RegExp(m[1],m[2]),res=t.match(r);document.getElementById("out").textContent=res?"Matches: "+JSON.stringify(res,null,2):"No match"}catch(e){document.getElementById("out").textContent="Error: "+e}}document.getElementById("pat").oninput=test;document.getElementById("inp").oninput=test'),

  ("jwt-decoder","JWT Decoder","🎫","#a78bfa",True,"Code",
   '<textarea id="inp" rows="3" placeholder="Paste JWT token..."></textarea><button class="btn" onclick="dec()" style="margin-top:8px">Decode</button><div class="output" id="out"></div>',
   'function dec(){try{let parts=document.getElementById("inp").value.split(".");if(parts.length!==3)throw"Invalid JWT";let h=JSON.parse(atob(parts[0])),p=JSON.parse(atob(parts[1]));document.getElementById("out").textContent="Header:\\n"+JSON.stringify(h,null,2)+"\\n\\nPayload:\\n"+JSON.stringify(p,null,2)}catch(e){document.getElementById("out").textContent="Error: "+e}}'),

  ("url-encoder","URL Encoder","🌐","#38bdf8",False,"Code",
   '<textarea id="inp" rows="3" placeholder="Text or URL..."></textarea><div class="row"><button class="btn" onclick="e()">Encode</button><button class="btn" onclick="d()">Decode</button></div><div class="output" id="out"></div>',
   'function e(){document.getElementById("out").textContent=encodeURIComponent(document.getElementById("inp").value)}function d(){try{document.getElementById("out").textContent=decodeURIComponent(document.getElementById("inp").value)}catch(e){document.getElementById("out").textContent="Error"}}'),

  ("html-escape","HTML Escape","🏷️","#fb923c",False,"Code",
   '<textarea id="inp" rows="4" placeholder="<div>Hello</div>"></textarea><div class="row"><button class="btn" onclick="esc()">Escape</button><button class="btn" onclick="unesc()">Unescape</button></div><div class="output" id="out"></div>',
   'function esc(){document.getElementById("out").textContent=document.getElementById("inp").value.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}function unesc(){let d=document.createElement("div");d.innerHTML=document.getElementById("inp").value;document.getElementById("out").textContent=d.textContent}'),

  ("css-minifier","CSS Minifier","🎨","#e879f9",True,"Code",
   '<textarea id="inp" rows="6" placeholder="body {\\n  color: red;\\n}"></textarea><button class="btn" onclick="mini()" style="margin-top:8px">Minify</button><div class="output" id="out"></div>',
   'function mini(){document.getElementById("out").textContent=document.getElementById("inp").value.replace(/\\/\\*[\\s\\S]*?\\*\\//g,"").replace(/\\s+/g," ").replace(/\\s*([{}:;,])\\s*/g,"$1").trim()}'),

  ("cron-helper","Cron Helper","⏰","#fbbf24",True,"Code",
   '<label>Cron Expression</label><input type="text" id="inp" placeholder="* * * * *" value="0 9 * * 1-5"><div class="output" id="out" style="margin-top:12px"></div>',
   'function parse(){let p=document.getElementById("inp").value.split(" ");if(p.length<5){document.getElementById("out").textContent="Need 5 fields: min hour day month weekday";return}let labels=["Minute","Hour","Day of Month","Month","Day of Week"];let o=p.map((v,i)=>labels[i]+": "+v).join("\\n");document.getElementById("out").textContent=o}document.getElementById("inp").oninput=parse;parse()'),

  ("diff-checker","Diff Checker","📋","#6ee7b7",True,"Code",
   '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><div><label>Original</label><textarea id="a" rows="6"></textarea></div><div><label>Modified</label><textarea id="b" rows="6"></textarea></div></div><button class="btn" onclick="diff()" style="margin-top:8px">Compare</button><div class="output" id="out"></div>',
   'function diff(){let a=document.getElementById("a").value.split("\\n"),b=document.getElementById("b").value.split("\\n"),o=[];let max=Math.max(a.length,b.length);for(let i=0;i<max;i++){if(a[i]===b[i])o.push("  "+a[i]);else{if(a[i]!==undefined)o.push("- "+a[i]);if(b[i]!==undefined)o.push("+ "+b[i])}}document.getElementById("out").textContent=o.join("\\n")}'),

  # --- COLOR/DESIGN TOOLS ---
  ("color-picker","Color Picker","🎨","#f472b6",False,"Design",
   '<input type="color" id="c" value="#ff6b9d" style="width:100%;height:60px;border:none;cursor:pointer;background:none"><div class="output" id="out"></div>',
   'function upd(){let c=document.getElementById("c").value;let r=parseInt(c.slice(1,3),16),g=parseInt(c.slice(3,5),16),b=parseInt(c.slice(5,7),16);document.getElementById("out").textContent="HEX: "+c+"\\nRGB: rgb("+r+","+g+","+b+")\\nHSL: hsl(...)\\nCSS: "+c}document.getElementById("c").oninput=upd;upd()'),

  ("gradient-gen","Gradient Generator","🌈","#a78bfa",False,"Design",
   '<div class="row"><input type="color" id="c1" value="#ff6b9d"><input type="color" id="c2" value="#4f46e5"><select id="dir"><option>to right</option><option>to bottom</option><option>to bottom right</option><option>135deg</option></select></div><div id="preview" style="height:80px;border-radius:8px;margin:10px 0"></div><div class="output" id="out"></div>',
   'function upd(){let c1=document.getElementById("c1").value,c2=document.getElementById("c2").value,d=document.getElementById("dir").value;let css="linear-gradient("+d+", "+c1+", "+c2+")";document.getElementById("preview").style.background=css;document.getElementById("out").textContent="background: "+css+";"}document.querySelectorAll("#c1,#c2,#dir").forEach(e=>e.oninput=upd);upd()'),

  ("contrast-check","Contrast Checker","👁️","#34d399",True,"Design",
   '<div class="row"><div><label>Foreground</label><input type="color" id="fg" value="#ffffff"></div><div><label>Background</label><input type="color" id="bg" value="#1f2937"></div></div><div id="preview" style="padding:20px;border-radius:8px;margin:10px 0;text-align:center;font-size:18px">Sample Text</div><div class="output" id="out"></div>',
   'function lum(hex){let r=parseInt(hex.slice(1,3),16)/255,g=parseInt(hex.slice(3,5),16)/255,b=parseInt(hex.slice(5,7),16)/255;[r,g,b]=[r,g,b].map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));return .2126*r+.7152*g+.0722*b}function upd(){let fg=document.getElementById("fg").value,bg=document.getElementById("bg").value;let l1=lum(fg),l2=lum(bg);let ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);document.getElementById("preview").style.color=fg;document.getElementById("preview").style.background=bg;let pass=ratio>=4.5?"✅ PASS (AA)":"❌ FAIL";document.getElementById("out").textContent="Ratio: "+ratio.toFixed(2)+":1 — "+pass}document.querySelectorAll("#fg,#bg").forEach(e=>e.oninput=upd);upd()'),

  ("shadow-gen","Shadow Generator","🌓","#60a5fa",True,"Design",
   '<label>X Offset</label><input type="range" id="x" min="-50" max="50" value="5"><label>Y Offset</label><input type="range" id="y" min="-50" max="50" value="5"><label>Blur</label><input type="range" id="b" min="0" max="100" value="15"><label>Spread</label><input type="range" id="s" min="-50" max="50" value="0"><label>Color</label><input type="color" id="c" value="#000000"><div id="preview" style="width:120px;height:120px;background:#374151;border-radius:12px;margin:16px auto"></div><div class="output" id="out"></div>',
   'function upd(){let x=document.getElementById("x").value,y=document.getElementById("y").value,b=document.getElementById("b").value,s=document.getElementById("s").value,c=document.getElementById("c").value;let css=x+"px "+y+"px "+b+"px "+s+"px "+c;document.getElementById("preview").style.boxShadow=css;document.getElementById("out").textContent="box-shadow: "+css+";"}document.querySelectorAll("input").forEach(e=>e.oninput=upd);upd()'),

  ("palette-gen","Palette Generator","🎯","#fbbf24",False,"Design",
   '<button class="btn" onclick="gen()">Generate Palette</button><div id="pal" style="display:flex;gap:4px;margin:12px 0;height:80px;border-radius:8px;overflow:hidden"></div><div class="output" id="out"></div>',
   'function hsl2hex(h,s,l){s/=100;l/=100;let a=s*Math.min(l,1-l);let f=n=>{let k=(n+h/30)%12;let c=l-a*Math.max(Math.min(k-3,9-k,1),-1);return Math.round(255*c).toString(16).padStart(2,"0")};return"#"+f(0)+f(8)+f(4)}function gen(){let h=Math.random()*360,colors=[];for(let i=0;i<5;i++){colors.push(hsl2hex((h+i*30)%360,70+Math.random()*20,45+Math.random()*20))}document.getElementById("pal").innerHTML=colors.map(c=>"<div style=\\"flex:1;background:"+c+"\\"></div>").join("");document.getElementById("out").textContent=colors.join("\\n")}gen()'),

  ("glass-gen","Glassmorphism Gen","🪟","#e879f9",True,"Design",
   '<label>Blur</label><input type="range" id="b" min="0" max="30" value="10"><label>Opacity</label><input type="range" id="o" min="0" max="100" value="20"><label>Border Opacity</label><input type="range" id="bo" min="0" max="100" value="30"><div id="preview" style="width:200px;height:120px;border-radius:16px;margin:16px auto;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:bold">Glass Card</div><div class="output" id="out"></div>',
   'function upd(){let b=document.getElementById("b").value,o=document.getElementById("o").value/100,bo=document.getElementById("bo").value/100;let p=document.getElementById("preview");p.style.background="rgba(255,255,255,"+o+")";p.style.backdropFilter="blur("+b+"px)";p.style.border="1px solid rgba(255,255,255,"+bo+")";document.getElementById("out").textContent="background: rgba(255,255,255,"+o+");\\nbackdrop-filter: blur("+b+"px);\\nborder: 1px solid rgba(255,255,255,"+bo+");"}document.querySelectorAll("input").forEach(e=>e.oninput=upd);upd()'),

  ("font-pairing","Font Pairing","✏️","#fb923c",True,"Design",
   '<div id="pairs"></div><button class="btn" onclick="shuffle()">Shuffle Pairs</button>',
   'const pairs=[["Georgia","Verdana"],["Playfair Display","Source Sans Pro"],["Lora","Roboto"],["Merriweather","Open Sans"],["Crimson Text","Work Sans"],["Libre Baskerville","Montserrat"]];function shuffle(){let p=pairs[Math.floor(Math.random()*pairs.length)];document.getElementById("pairs").innerHTML="<div style=font-family:serif;font-size:28px;margin:10px>"+p[0]+"</div><div style=font-size:14px;color:#9ca3af;margin:10px>"+p[1]+" — Body text example paragraph showing the pair.</div>"}shuffle()'),

  # --- MATH TOOLS ---
  ("unit-converter","Unit Converter","📐","#60a5fa",False,"Utility",
   '<select id="cat" style="margin-bottom:8px"><option>Length</option><option>Weight</option><option>Temperature</option></select><input type="number" id="v" value="1" placeholder="Value"><div class="output" id="out" style="margin-top:8px"></div>',
   'function conv(){let c=document.getElementById("cat").value,v=+document.getElementById("v").value,o="";if(c==="Length")o="m: "+v+"\\nft: "+(v*3.281).toFixed(4)+"\\nin: "+(v*39.37).toFixed(2)+"\\ncm: "+(v*100).toFixed(2)+"\\nkm: "+(v/1000).toFixed(6)+"\\nmi: "+(v*0.000621).toFixed(6);else if(c==="Weight")o="kg: "+v+"\\nlb: "+(v*2.205).toFixed(4)+"\\noz: "+(v*35.274).toFixed(2)+"\\ng: "+(v*1000).toFixed(0);else o="°C: "+v+"\\n°F: "+(v*9/5+32).toFixed(2)+"\\nK: "+(v+273.15).toFixed(2);document.getElementById("out").textContent=o}document.querySelectorAll("#cat,#v").forEach(e=>e.oninput=conv);conv()'),

  ("percentage-calc","Percentage Calc","💯","#34d399",False,"Utility",
   '<label>What is <input type="number" id="a" value="25" style="width:80px;display:inline"> % of <input type="number" id="b" value="200" style="width:80px;display:inline"> ?</label><div class="output" id="out" style="font-size:24px;text-align:center"></div>',
   'function calc(){let a=+document.getElementById("a").value,b=+document.getElementById("b").value;document.getElementById("out").textContent=(a/100*b).toFixed(2)}document.querySelectorAll("#a,#b").forEach(e=>e.oninput=calc);calc()'),

  ("bmi-calc","BMI Calculator","⚖️","#f472b6",False,"Utility",
   '<label>Weight (kg)</label><input type="number" id="w" value="70"><label>Height (cm)</label><input type="number" id="h" value="175"><div class="output" id="out" style="font-size:18px;text-align:center;margin-top:12px"></div>',
   'function calc(){let w=+document.getElementById("w").value,h=+document.getElementById("h").value/100;let bmi=(w/(h*h)).toFixed(1);let cat=bmi<18.5?"Underweight":bmi<25?"Normal":bmi<30?"Overweight":"Obese";document.getElementById("out").textContent="BMI: "+bmi+" — "+cat}document.querySelectorAll("#w,#h").forEach(e=>e.oninput=calc);calc()'),

  ("tip-calc","Tip Calculator","💰","#fbbf24",False,"Utility",
   '<label>Bill Amount ($)</label><input type="number" id="b" value="50"><label>Tip %</label><input type="range" id="t" min="0" max="30" value="15"><label>Split</label><input type="number" id="s" value="1" min="1"><div class="output" id="out" style="font-size:16px"></div>',
   'function calc(){let b=+document.getElementById("b").value,t=+document.getElementById("t").value,s=+document.getElementById("s").value;let tip=b*t/100;document.getElementById("out").textContent="Tip: $"+tip.toFixed(2)+"\\nTotal: $"+(b+tip).toFixed(2)+"\\nPer person: $"+((b+tip)/s).toFixed(2)+"\\nTip %: "+t+"%"}document.querySelectorAll("#b,#t,#s").forEach(e=>e.oninput=calc);calc()'),

  ("timestamp-conv","Timestamp Converter","🕐","#a78bfa",True,"Utility",
   '<label>Unix Timestamp</label><input type="number" id="ts" placeholder="1609459200"><button class="btn" onclick="now()" style="margin:8px 0">Use Current Time</button><div class="output" id="out"></div>',
   'function conv(){let ts=+document.getElementById("ts").value;let d=new Date(ts*1000);document.getElementById("out").textContent="ISO: "+d.toISOString()+"\\nLocal: "+d.toLocaleString()+"\\nUTC: "+d.toUTCString()+"\\nUnix: "+ts}function now(){document.getElementById("ts").value=Math.floor(Date.now()/1000);conv()}document.getElementById("ts").oninput=conv'),

  ("number-base","Number Base Converter","🔢","#38bdf8",True,"Utility",
   '<label>Decimal Number</label><input type="number" id="n" value="255"><div class="output" id="out"></div>',
   'function conv(){let n=+document.getElementById("n").value;document.getElementById("out").textContent="Decimal: "+n+"\\nBinary: "+n.toString(2)+"\\nOctal: "+n.toString(8)+"\\nHex: "+n.toString(16).toUpperCase()}document.getElementById("n").oninput=conv;conv()'),

  ("age-calc","Age Calculator","🎂","#e879f9",False,"Utility",
   '<label>Birth Date</label><input type="date" id="bd"><div class="output" id="out" style="font-size:16px"></div>',
   'function calc(){let bd=new Date(document.getElementById("bd").value);let now=new Date();let age=now.getFullYear()-bd.getFullYear();let days=Math.floor((now-bd)/86400000);document.getElementById("out").textContent="Age: ~"+age+" years\\nTotal days: "+days.toLocaleString()+"\\nTotal hours: "+(days*24).toLocaleString()}document.getElementById("bd").oninput=calc'),

  ("loan-calc","Loan Calculator","🏦","#fb923c",True,"Utility",
   '<label>Principal ($)</label><input type="number" id="p" value="10000"><label>Annual Rate (%)</label><input type="number" id="r" value="5"><label>Term (months)</label><input type="number" id="t" value="36"><div class="output" id="out" style="font-size:16px"></div>',
   'function calc(){let p=+document.getElementById("p").value,r=+document.getElementById("r").value/100/12,t=+document.getElementById("t").value;let m=p*r*Math.pow(1+r,t)/(Math.pow(1+r,t)-1);document.getElementById("out").textContent="Monthly: $"+m.toFixed(2)+"\\nTotal: $"+(m*t).toFixed(2)+"\\nInterest: $"+(m*t-p).toFixed(2)}document.querySelectorAll("#p,#r,#t").forEach(e=>e.oninput=calc);calc()'),

  # --- SECURITY TOOLS ---
  ("password-gen","Password Generator","🔒","#f44336",False,"Security",
   '<label>Length</label><input type="range" id="len" min="8" max="64" value="16"><div class="row"><label><input type="checkbox" id="up" checked> Uppercase</label><label><input type="checkbox" id="num" checked> Numbers</label><label><input type="checkbox" id="sym" checked> Symbols</label></div><div class="output" id="out" style="font-size:20px;text-align:center;letter-spacing:2px"></div><button class="btn" onclick="gen()" style="margin-top:8px;width:100%">Generate</button>',
   'function gen(){let l=+document.getElementById("len").value;let c="abcdefghijklmnopqrstuvwxyz";if(document.getElementById("up").checked)c+="ABCDEFGHIJKLMNOPQRSTUVWXYZ";if(document.getElementById("num").checked)c+="0123456789";if(document.getElementById("sym").checked)c+="!@#$%^&*()_+-=[]{}|;:,.<>?";let p="";for(let i=0;i<l;i++)p+=c[Math.floor(Math.random()*c.length)];document.getElementById("out").textContent=p}gen()'),

  ("hash-gen","Hash Generator","#️⃣","#a78bfa",True,"Security",
   '<textarea id="inp" rows="3" placeholder="Text to hash..."></textarea><button class="btn" onclick="hash()" style="margin-top:8px">Generate SHA-256</button><div class="output" id="out"></div>',
   'async function hash(){let t=new TextEncoder().encode(document.getElementById("inp").value);let h=await crypto.subtle.digest("SHA-256",t);let a=Array.from(new Uint8Array(h)).map(b=>b.toString(16).padStart(2,"0")).join("");document.getElementById("out").textContent="SHA-256:\\n"+a}'),

  ("uuid-gen","UUID Generator","🆔","#34d399",False,"Security",
   '<div class="output" id="out" style="font-size:16px;text-align:center"></div><button class="btn" onclick="gen()" style="margin-top:12px;width:100%">Generate UUID v4</button><button class="btn" onclick="batch()" style="margin-top:8px;width:100%;background:#374151;color:#e5e7eb">Generate 10</button>',
   'function uuid(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,c=>{let r=Math.random()*16|0;return(c=="x"?r:r&3|8).toString(16)})}function gen(){document.getElementById("out").textContent=uuid()}function batch(){let o="";for(let i=0;i<10;i++)o+=uuid()+"\\n";document.getElementById("out").textContent=o.trim()}gen()'),

  ("qr-gen","QR Code Generator","📱","#60a5fa",True,"Security",
   '<textarea id="inp" rows="2" placeholder="URL or text...">https://shipmicro.com</textarea><button class="btn" onclick="gen()" style="margin-top:8px">Generate QR</button><div style="text-align:center;margin-top:12px"><img id="qr" style="max-width:200px;border-radius:8px"></div>',
   'function gen(){let t=encodeURIComponent(document.getElementById("inp").value);document.getElementById("qr").src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data="+t}gen()'),

  ("fake-data","Fake Data Generator","🎭","#fbbf24",True,"Security",
   '<label>Count</label><input type="number" id="n" value="5" min="1" max="50"><button class="btn" onclick="gen()" style="margin-top:8px">Generate</button><div class="output" id="out"></div>',
   'const fn=["James","Emma","Liam","Olivia","Noah","Ava","William","Sophia","Benjamin","Isabella"];const ln=["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore"];const dom=["gmail.com","outlook.com","yahoo.com","proton.me"];function gen(){let n=+document.getElementById("n").value,o=[];for(let i=0;i<n;i++){let f=fn[Math.floor(Math.random()*fn.length)],l=ln[Math.floor(Math.random()*ln.length)];o.push({name:f+" "+l,email:(f+"."+l+"@"+dom[Math.floor(Math.random()*dom.length)]).toLowerCase(),phone:"+1-"+Math.floor(Math.random()*900+100)+"-"+Math.floor(Math.random()*900+100)+"-"+Math.floor(Math.random()*9000+1000)})}document.getElementById("out").textContent=JSON.stringify(o,null,2)}gen()'),

  ("ip-info","IP Info Lookup","🌍","#38bdf8",True,"Security",
   '<button class="btn" onclick="lookup()">Lookup My IP</button><div class="output" id="out" style="margin-top:12px">Click to check...</div>',
   'async function lookup(){document.getElementById("out").textContent="Loading...";try{let r=await fetch("https://ipapi.co/json/");let d=await r.json();document.getElementById("out").textContent="IP: "+d.ip+"\\nCity: "+d.city+"\\nRegion: "+d.region+"\\nCountry: "+d.country_name+"\\nISP: "+d.org+"\\nTimezone: "+d.timezone}catch(e){document.getElementById("out").textContent="Error: "+e.message}}'),

  ("encryption","Text Encryptor","🔐","#e879f9",True,"Security",
   '<label>Key</label><input type="text" id="key" placeholder="Secret key"><textarea id="inp" rows="3" placeholder="Text..." style="margin-top:8px"></textarea><div class="row"><button class="btn" onclick="enc()">Encrypt</button><button class="btn" onclick="dec()">Decrypt</button></div><div class="output" id="out"></div>',
   'function enc(){let k=document.getElementById("key").value,t=document.getElementById("inp").value,o="";for(let i=0;i<t.length;i++)o+=String.fromCharCode(t.charCodeAt(i)^k.charCodeAt(i%k.length));document.getElementById("out").textContent=btoa(o)}function dec(){try{let k=document.getElementById("key").value,t=atob(document.getElementById("inp").value),o="";for(let i=0;i<t.length;i++)o+=String.fromCharCode(t.charCodeAt(i)^k.charCodeAt(i%k.length));document.getElementById("out").textContent=o}catch(e){document.getElementById("out").textContent="Error"}}'),

  # --- SEO TOOLS ---
  ("meta-gen","Meta Tag Generator","🏷️","#f472b6",False,"SEO",
   '<label>Title</label><input type="text" id="t" placeholder="Page Title"><label>Description</label><textarea id="d" rows="2" placeholder="Page description..."></textarea><label>Keywords</label><input type="text" id="k" placeholder="keyword1, keyword2"><div class="output" id="out"></div>',
   'function gen(){let t=document.getElementById("t").value,d=document.getElementById("d").value,k=document.getElementById("k").value;document.getElementById("out").textContent=\'<meta charset="UTF-8">\\n<title>\'+t+"</title>\\n"+"<meta name=\\"description\\" content=\\""+d+"\\">\\n"+"<meta name=\\"keywords\\" content=\\""+k+"\\">\\n"+"<meta property=\\"og:title\\" content=\\""+t+"\\">\\n"+"<meta property=\\"og:description\\" content=\\""+d+"\\">"}document.querySelectorAll("input,textarea").forEach(e=>e.oninput=gen)'),

  ("og-preview","Open Graph Preview","👁️","#a78bfa",True,"SEO",
   '<label>og:title</label><input type="text" id="t" value="My Page"><label>og:description</label><input type="text" id="d" value="A great page"><label>og:image URL</label><input type="text" id="img" placeholder="https://..."><div style="background:#fff;color:#333;border-radius:8px;margin-top:12px;overflow:hidden"><img id="preview" style="width:100%;height:150px;object-fit:cover;background:#ddd"><div style="padding:10px"><div id="pt" style="font-weight:700;font-size:14px"></div><div id="pd" style="font-size:12px;color:#666"></div></div></div>',
   'function upd(){document.getElementById("pt").textContent=document.getElementById("t").value;document.getElementById("pd").textContent=document.getElementById("d").value;let img=document.getElementById("img").value;if(img)document.getElementById("preview").src=img}document.querySelectorAll("input").forEach(e=>e.oninput=upd);upd()'),

  ("robots-builder","Robots.txt Builder","🤖","#34d399",True,"SEO",
   '<div class="row"><label><input type="checkbox" id="all" checked> Allow All</label><label><input type="checkbox" id="sitemap" checked> Include Sitemap</label></div><label>Sitemap URL</label><input type="text" id="sm" value="https://shipmicro.com/sitemap.xml"><label>Disallow Paths (one per line)</label><textarea id="dis" rows="3" placeholder="/admin\\n/api"></textarea><div class="output" id="out"></div>',
   'function gen(){let all=document.getElementById("all").checked,sm=document.getElementById("sitemap").checked,smUrl=document.getElementById("sm").value,dis=document.getElementById("dis").value.split("\\n").filter(Boolean);let o="User-agent: *\\n";if(all)o+="Allow: /\\n";dis.forEach(d=>o+="Disallow: "+d+"\\n");if(sm)o+="\\nSitemap: "+smUrl;document.getElementById("out").textContent=o}document.querySelectorAll("input,textarea").forEach(e=>e.oninput=gen);gen()'),

  ("heading-analyzer","Heading Analyzer","📊","#fbbf24",True,"SEO",
   '<textarea id="inp" rows="6" placeholder="Paste HTML or text with headings..."></textarea><button class="btn" onclick="analyze()" style="margin-top:8px">Analyze</button><div class="output" id="out"></div>',
   'function analyze(){let t=document.getElementById("inp").value;let h1=(t.match(/<h1/gi)||[]).length;let h2=(t.match(/<h2/gi)||[]).length;let h3=(t.match(/<h3/gi)||[]).length;let words=t.replace(/<[^>]*>/g," ").trim().split(/\\s+/).length;document.getElementById("out").textContent="H1 tags: "+h1+(h1!==1?" ⚠️ Should be exactly 1":""+" ✅")+"\\nH2 tags: "+h2+"\\nH3 tags: "+h3+"\\nWord count: "+words+"\\nReading time: ~"+Math.ceil(words/200)+" min"}'),

  ("keyword-density","Keyword Density","🔑","#60a5fa",True,"SEO",
   '<label>Content</label><textarea id="inp" rows="5" placeholder="Paste your article..."></textarea><div class="output" id="out"></div>',
   'document.getElementById("inp").oninput=function(){let w=this.value.toLowerCase().replace(/[^a-z0-9\\s]/g,"").split(/\\s+/).filter(Boolean);let m={};w.forEach(x=>m[x]=(m[x]||0)+1);let s=Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([k,v])=>k+" — "+v+" ("+(v/w.length*100).toFixed(1)+"%)").join("\\n");document.getElementById("out").textContent="Total words: "+w.length+"\\n\\n"+s}'),

  # --- PRODUCTIVITY TOOLS ---
  ("pomodoro","Pomodoro Timer","🍅","#f44336",False,"Utility",
   '<div style="text-align:center"><div id="time" style="font-size:64px;font-weight:900;color:#f44336;text-shadow:0 0 20px #f4433644;margin:20px 0">25:00</div><div class="row" style="justify-content:center"><button class="btn" onclick="start()">Start</button><button class="btn" onclick="pause()" style="background:#374151;color:#e5e7eb">Pause</button><button class="btn" onclick="reset()" style="background:#374151;color:#e5e7eb">Reset</button></div><div id="status" style="margin-top:12px;color:#9ca3af">Ready to focus</div></div>',
   'let secs=25*60,iv=null,scE=document.getElementById("sc");scE.textContent="0 sessions";let sessions=0;function fmt(s){return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0")}function start(){if(iv)return;document.getElementById("status").textContent="Focusing...";iv=setInterval(()=>{secs--;document.getElementById("time").textContent=fmt(secs);if(secs<=0){clearInterval(iv);iv=null;sessions++;scE.textContent=sessions+" sessions";secs=25*60;document.getElementById("time").textContent=fmt(secs);document.getElementById("status").textContent="Break time! 🎉"}},1000)}function pause(){clearInterval(iv);iv=null;document.getElementById("status").textContent="Paused"}function reset(){clearInterval(iv);iv=null;secs=25*60;document.getElementById("time").textContent=fmt(secs);document.getElementById("status").textContent="Ready to focus"}'),

  ("habit-tracker","Habit Tracker","✅","#34d399",True,"Utility",
   '<label>Add Habit</label><div class="row"><input type="text" id="newH" placeholder="e.g. Read 30min"><button class="btn" onclick="addH()">Add</button></div><div id="list" style="margin-top:12px"></div>',
   'let habits=JSON.parse(localStorage.getItem("smHabits")||"[]");function render(){let el=document.getElementById("list");el.innerHTML="";habits.forEach((h,i)=>{el.innerHTML+="<div style=\\"display:flex;align-items:center;gap:8px;padding:8px;background:#1f2937;border-radius:8px;margin:4px 0\\"><input type=checkbox "+(h.done?"checked":"")+" onchange=\\"toggle("+i+")\\"><span style=\\""+(h.done?"text-decoration:line-through;opacity:.5":"")+"\\">"+h.name+"</span><button onclick=\\"del("+i+")\\" style=\\"margin-left:auto;background:none;border:none;color:#f55;cursor:pointer\\">×</button></div>"})}function save(){localStorage.setItem("smHabits",JSON.stringify(habits));render()}function addH(){let n=document.getElementById("newH").value.trim();if(n){habits.push({name:n,done:false});document.getElementById("newH").value="";save()}}function toggle(i){habits[i].done=!habits[i].done;save()}function del(i){habits.splice(i,1);save()}render()'),

  ("stopwatch","Stopwatch","⏱️","#fbbf24",False,"Utility",
   '<div style="text-align:center"><div id="time" style="font-size:48px;font-weight:900;color:#fbbf24;margin:20px 0">00:00.00</div><div class="row" style="justify-content:center"><button class="btn" onclick="go()">Start</button><button class="btn" onclick="lap()" style="background:#374151;color:#e5e7eb">Lap</button><button class="btn" onclick="rst()" style="background:#374151;color:#e5e7eb">Reset</button></div><div id="laps" style="margin-top:12px;font-size:13px;color:#9ca3af"></div></div>',
   'let t=0,iv=null,laps=[];function fmt(ms){let m=Math.floor(ms/60000),s=Math.floor(ms%60000/1000),cs=Math.floor(ms%1000/10);return String(m).padStart(2,"0")+":"+String(s).padStart(2,"0")+"."+String(cs).padStart(2,"0")}function go(){if(iv)return;let st=Date.now()-t;iv=setInterval(()=>{t=Date.now()-st;document.getElementById("time").textContent=fmt(t)},10)}function lap(){laps.push(t);document.getElementById("laps").innerHTML=laps.map((l,i)=>"Lap "+(i+1)+": "+fmt(l)).reverse().join("<br>")}function rst(){clearInterval(iv);iv=null;t=0;laps=[];document.getElementById("time").textContent=fmt(0);document.getElementById("laps").innerHTML=""}'),

  ("notes","Quick Notes","📝","#a78bfa",False,"Utility",
   '<textarea id="inp" rows="10" placeholder="Start typing... auto-saved to browser."></textarea><div style="margin-top:8px;font-size:12px;color:#6b7280" id="status">Loaded</div>',
   'let inp=document.getElementById("inp"),st=document.getElementById("status");inp.value=localStorage.getItem("smNotes")||"";inp.oninput=function(){localStorage.setItem("smNotes",this.value);st.textContent="Saved at "+new Date().toLocaleTimeString()}'),

  ("countdown","Countdown Timer","⏳","#e879f9",True,"Utility",
   '<label>Minutes</label><input type="number" id="mins" value="5" min="1"><button class="btn" onclick="go()" style="margin-top:8px">Start Countdown</button><div id="time" style="font-size:48px;font-weight:900;text-align:center;margin:20px 0;color:#e879f9">05:00</div>',
   'let iv;function go(){clearInterval(iv);let s=+document.getElementById("mins").value*60;function upd(){let m=Math.floor(s/60),sec=s%60;document.getElementById("time").textContent=String(m).padStart(2,"0")+":"+String(sec).padStart(2,"0");if(s<=0){clearInterval(iv);document.getElementById("time").textContent="Done! 🎉";return}s--}upd();iv=setInterval(upd,1000)}'),
]

print(f"Generating {len(tools_data)} tools...")

for i, t in enumerate(tools_data):
    slug, title, icon, accent, premium, cat = t[0], t[1], t[2], t[3], t[4], t[5]
    body, script = t[6], t[7]
    html = tool_html(title, accent, body, script)
    fname = slug + ".html"
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)
    registry.append({
        "slug": slug, "title": title, "category": cat,
        "icon": icon, "url": f"/tools/{fname}", "isPremium": False
    })
    print(f"  ✅ [{i+1}/{len(tools_data)}] {title}")

reg_path = os.path.join(OUT, "..", "..", "tool_registry.json")
with open(reg_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
print(f"\n🎉 Generated {len(registry)} tools! Registry → tool_registry.json")
