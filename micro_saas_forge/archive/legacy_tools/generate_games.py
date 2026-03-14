"""
ShipMicro Arcade — Quality Game Generator v2
All games are responsive, full-viewport, touch-friendly, with polished visuals.
"""
import os, json

OUT = r"d:\Project\1\micro_saas_forge\shipmicro_site\public\games"
os.makedirs(OUT, exist_ok=True)
registry = []

COLORS = [
    ("#06b6d4","#0891b2"), ("#ec4899","#db2777"), ("#8b5cf6","#7c3aed"),
    ("#f59e0b","#d97706"), ("#10b981","#059669"), ("#ef4444","#dc2626"),
    ("#3b82f6","#2563eb"), ("#f97316","#ea580c"),
]

def pick(i):
    return COLORS[i % len(COLORS)]

def responsive_game(title, accent, extra_css, body, script):
    """Base template: full viewport, responsive, dark theme, touch ready"""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title} | ShipMicro Arcade</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0f172a;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;
min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;overflow:hidden;
touch-action:manipulation;-webkit-tap-highlight-color:transparent;user-select:none}}
.bar{{display:flex;align-items:center;justify-content:space-between;padding:8px 16px;
background:#0f172a;border-bottom:1px solid #1e293b;flex-shrink:0}}
.bar .title{{font-size:14px;font-weight:700;color:{accent};letter-spacing:1px}}
.bar .score{{font-size:14px;color:#94a3b8;font-variant-numeric:tabular-nums}}
.bar .score b{{color:{accent};font-size:18px}}
.game-area{{flex:1;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}}
canvas{{display:block;max-width:100%;max-height:100%}}
.btn{{padding:12px 32px;border:2px solid {accent};background:{accent}22;color:{accent};
font-size:16px;font-weight:700;border-radius:12px;cursor:pointer;letter-spacing:1px;
transition:all .2s;font-family:inherit}}
.btn:hover,.btn:active{{background:{accent};color:#0f172a}}
.overlay{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
justify-content:center;background:rgba(15,23,42,.9);z-index:10;text-align:center;padding:20px}}
.overlay h2{{font-size:clamp(24px,5vw,48px);font-weight:900;color:{accent};margin-bottom:8px}}
.overlay p{{color:#94a3b8;margin-bottom:24px;font-size:clamp(14px,3vw,18px)}}
{extra_css}
</style></head><body>
<div class="bar"><span class="title">{title}</span><span class="score">SCORE: <b id="sc">0</b></span></div>
<div class="game-area" id="area">{body}</div>
<script>
const SC=document.getElementById('sc');
let score=0;
function addScore(n){{score+=n;SC.textContent=score}}
{script}
</script></body></html>"""

# ============================================================
# GAME TYPE 1: TAP/CLICK GAMES (Responsive grid-based)
# ============================================================
def make_tap_game(slug, title, emoji, accent, spawn_rate=1200, lifetime=2500):
    return responsive_game(title, accent, f"""
.target{{position:absolute;font-size:clamp(36px,8vw,56px);cursor:pointer;
transition:transform .15s,opacity .15s;animation:pop .2s ease-out}}
.target:active{{transform:scale(.8)}}
@keyframes pop{{from{{transform:scale(0);opacity:0}}to{{transform:scale(1);opacity:1}}}}
""", "", f"""
const area=document.getElementById('area');
let gameOver=false;
function spawn(){{
  if(gameOver)return;
  const t=document.createElement('div');
  t.className='target';t.textContent='{emoji}';
  const aw=area.clientWidth,ah=area.clientHeight;
  t.style.left=Math.random()*(aw-60)+'px';
  t.style.top=Math.random()*(ah-60)+'px';
  const handleClick=(e)=>{{e.preventDefault();addScore(10);t.style.transform='scale(0)';t.style.opacity='0';
    setTimeout(()=>t.remove(),150);spawn()}};
  t.addEventListener('pointerdown',handleClick);
  area.appendChild(t);
  setTimeout(()=>{{if(t.parentNode){{t.style.opacity='0';setTimeout(()=>t.remove(),150);}}}},{lifetime});
}}
setInterval(()=>{{if(!gameOver)spawn()}},{spawn_rate});spawn();spawn();
""")

# ============================================================
# GAME TYPE 2: CANVAS DODGE GAMES (Full viewport canvas)
# ============================================================
def make_dodge_game(slug, title, player, enemy, accent):
    return responsive_game(title, accent, "", '<canvas id="c"></canvas>', f"""
const c=document.getElementById('c'),ctx=c.getContext('2d'),area=document.getElementById('area');
let W,H,px,py,enemies=[],spd=2.5,frame=0,gameOver=false,best=0;

function resize(){{W=area.clientWidth;H=area.clientHeight;c.width=W;c.height=H;px=W/2;py=H-60}}
resize();window.addEventListener('resize',resize);

area.addEventListener('pointermove',e=>{{const r=area.getBoundingClientRect();px=e.clientX-r.left;py=e.clientY-r.top}});
area.addEventListener('touchmove',e=>{{e.preventDefault();const r=area.getBoundingClientRect();
px=e.touches[0].clientX-r.left;py=e.touches[0].clientY-r.top}},{{passive:false}});

function restart(){{enemies=[];score=0;spd=2.5;frame=0;gameOver=false;SC.textContent='0';loop()}}

function loop(){{
  if(gameOver)return;
  ctx.fillStyle='rgba(15,23,42,0.25)';ctx.fillRect(0,0,W,H);
  if(frame%15===0)enemies.push({{x:Math.random()*W,y:-30,s:1+Math.random()*2}});
  ctx.font=Math.min(W/12,40)+'px serif';
  ctx.fillText('{player}',px-15,py);
  for(let i=enemies.length-1;i>=0;i--){{
    enemies[i].y+=spd*enemies[i].s;
    ctx.font=Math.min(W/14,32)+'px serif';
    ctx.fillText('{enemy}',enemies[i].x,enemies[i].y);
    if(enemies[i].y>H){{enemies.splice(i,1);addScore(1)}}
    else if(Math.abs(enemies[i].x-px)<30&&Math.abs(enemies[i].y-py)<30){{
      gameOver=true;best=Math.max(best,score);
      const ov=document.createElement('div');ov.className='overlay';
      ov.innerHTML='<h2>Game Over</h2><p>Score: '+score+' | Best: '+best+'</p><button class=btn onclick=\\"this.parentNode.remove();restart()\\">Play Again</button>';
      area.appendChild(ov);return;
    }}
  }}
  spd=2.5+score*0.03;frame++;requestAnimationFrame(loop);
}}
loop();
""")

# ============================================================
# GAME TYPE 3: MEMORY CARD GAMES (Responsive grid)
# ============================================================
def make_memory_game(slug, title, accent, emojis="🚀,🎯,💎,🔥,⚡,🎮,🌟,🎲"):
    return responsive_game(title, accent, f"""
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(6px,1.5vw,12px);
padding:clamp(8px,2vw,20px);max-width:500px;width:100%}}
.card{{aspect-ratio:1;background:#1e293b;border:2px solid #334155;border-radius:clamp(8px,2vw,16px);
display:flex;align-items:center;justify-content:center;font-size:clamp(28px,6vw,48px);
cursor:pointer;transition:all .3s;-webkit-backface-visibility:hidden}}
.card:active{{transform:scale(.95)}}
.card.flip{{background:{accent}33;border-color:{accent}}}
.card.matched{{opacity:.3;pointer-events:none;border-color:#059669}}
.card .face{{opacity:0;transition:opacity .2s}}
.card.flip .face,.card.matched .face{{opacity:1}}
""", '<div class="grid" id="grid"></div>', f"""
const emojis='{emojis}'.split(',');
let cards=[...emojis,...emojis].sort(()=>Math.random()-.5);
const grid=document.getElementById('grid');
let flipped=[],moves=0;

cards.forEach((e,i)=>{{
  const c=document.createElement('div');c.className='card';c.dataset.v=e;
  c.innerHTML='<span class="face">'+e+'</span>';
  c.addEventListener('pointerdown',(ev)=>{{
    ev.preventDefault();
    if(flipped.length>=2||c.classList.contains('flip')||c.classList.contains('matched'))return;
    c.classList.add('flip');flipped.push(c);
    if(flipped.length===2){{
      moves++;
      if(flipped[0].dataset.v===flipped[1].dataset.v){{
        flipped.forEach(f=>f.classList.add('matched'));addScore(20);flipped=[];
        if(grid.querySelectorAll('.matched').length===cards.length){{
          setTimeout(()=>{{
            const ov=document.createElement('div');ov.className='overlay';
            ov.innerHTML='<h2>🎉 You Win!</h2><p>Completed in '+moves+' moves</p><button class=btn onclick=location.reload()>Play Again</button>';
            area.appendChild(ov);
          }},400);
        }}
      }}else{{
        setTimeout(()=>{{flipped.forEach(f=>f.classList.remove('flip'));flipped=[]}},700);
      }}
    }}
  }});
  grid.appendChild(c);
}});
""")

# ============================================================
# GAME TYPE 4: SIMON PATTERN GAMES (Big colored buttons)
# ============================================================
def make_simon_game(slug, title, accent):
    return responsive_game(title, accent, f"""
.pads{{display:grid;grid-template-columns:1fr 1fr;gap:clamp(8px,2vw,16px);
max-width:400px;width:90%;padding:20px}}
.pad{{height:clamp(80px,20vw,140px);border-radius:clamp(12px,3vw,24px);cursor:pointer;
opacity:.35;transition:all .15s;border:3px solid transparent}}
.pad:active,.pad.lit{{opacity:1;transform:scale(.97);
box-shadow:0 0 30px currentColor}}
.pad:nth-child(1){{background:#ef4444;color:#ef4444}}
.pad:nth-child(2){{background:#22c55e;color:#22c55e}}
.pad:nth-child(3){{background:#3b82f6;color:#3b82f6}}
.pad:nth-child(4){{background:#eab308;color:#eab308}}
#info{{text-align:center;color:#94a3b8;font-size:clamp(14px,3vw,18px);margin-top:16px}}
""", '<div class="pads" id="pads"><div class="pad"></div><div class="pad"></div><div class="pad"></div><div class="pad"></div></div><div id="info">Watch the pattern...</div>', f"""
const pads=document.querySelectorAll('.pad'),info=document.getElementById('info');
let seq=[],userSeq=[],playing=false;

function flash(i,dur){{pads[i].classList.add('lit');setTimeout(()=>pads[i].classList.remove('lit'),dur)}}

function playSeq(){{
  playing=true;info.textContent='Watch...';
  seq.push(Math.floor(Math.random()*4));
  let i=0;
  const iv=setInterval(()=>{{flash(seq[i],450);i++;
    if(i>=seq.length){{clearInterval(iv);playing=false;info.textContent='Your turn! ('+seq.length+' notes)';userSeq=[]}}
  }},650);
}}

pads.forEach((b,i)=>{{
  b.addEventListener('pointerdown',(e)=>{{
    e.preventDefault();
    if(playing)return;
    flash(i,250);userSeq.push(i);
    if(userSeq[userSeq.length-1]!==seq[userSeq.length-1]){{
      info.textContent='❌ Wrong! Score: '+score+' — Tap to restart';
      seq=[];score=0;SC.textContent=0;
      area.addEventListener('pointerdown',()=>{{info.textContent='Watch...';setTimeout(playSeq,500)}},{{once:true}});
      return;
    }}
    if(userSeq.length===seq.length){{addScore(10);info.textContent='✅ Correct!';setTimeout(playSeq,800)}}
  }});
}});
setTimeout(playSeq,800);
""")

# ============================================================
# GAME TYPE 5: MATH QUIZ GAMES (Responsive buttons)
# ============================================================
def make_math_game(slug, title, accent):
    return responsive_game(title, accent, f"""
#problem{{font-size:clamp(36px,8vw,64px);font-weight:900;color:{accent};
text-shadow:0 0 20px {accent}44;text-align:center;margin:clamp(12px,3vw,24px) 0}}
.opts{{display:grid;grid-template-columns:1fr 1fr;gap:clamp(8px,2vw,16px);
max-width:400px;width:90%;margin:0 auto}}
.opt{{padding:clamp(12px,3vw,20px);font-size:clamp(20px,4vw,32px);font-weight:700;
background:#1e293b;border:2px solid #334155;color:#e2e8f0;cursor:pointer;
border-radius:clamp(8px,2vw,16px);transition:all .15s;font-family:inherit}}
.opt:active{{transform:scale(.95);background:{accent}33;border-color:{accent}}}
#timer{{height:6px;background:{accent};border-radius:3px;margin:16px auto 0;
max-width:400px;width:90%;transition:width .1s linear}}
.correct{{background:#05966922!important;border-color:#059669!important}}
.wrong{{background:#dc262622!important;border-color:#dc2626!important}}
""", '<div id="problem"></div><div class="opts" id="opts"></div><div id="timer" style="width:100%"></div>', f"""
const probE=document.getElementById('problem'),optsE=document.getElementById('opts'),timerE=document.getElementById('timer');
let timeLeft=100,gameRunning=true;

function gen(){{
  if(!gameRunning)return;
  let a=Math.floor(Math.random()*20)+1,b=Math.floor(Math.random()*20)+1;
  const ops=['+','-','×'],op=ops[Math.floor(Math.random()*3)];
  let ans=op==='+'?a+b:op==='-'?a-b:a*b;
  probE.textContent=a+' '+op+' '+b+' = ?';
  let choices=new Set([ans]);
  while(choices.size<4)choices.add(ans+Math.floor(Math.random()*11)-5);
  let arr=[...choices].sort(()=>Math.random()-.5);
  optsE.innerHTML='';
  arr.forEach(c=>{{
    const b=document.createElement('button');b.className='opt';b.textContent=c;
    b.addEventListener('pointerdown',(e)=>{{
      e.preventDefault();
      if(c===ans){{b.classList.add('correct');addScore(10);timeLeft=Math.min(timeLeft+10,100);setTimeout(gen,250)}}
      else{{b.classList.add('wrong');gameRunning=false;
        probE.textContent='Game Over! Score: '+score;
        optsE.innerHTML='<button class=btn onclick=location.reload()>Play Again</button>'}}
    }});
    optsE.appendChild(b);
  }});
}}

setInterval(()=>{{
  if(!gameRunning)return;
  timeLeft-=0.5;timerE.style.width=timeLeft+'%';
  if(timeLeft<=0){{gameRunning=false;probE.textContent='Time Up! Score: '+score;
    optsE.innerHTML='<button class=btn onclick=location.reload()>Play Again</button>'}}
}},50);
gen();
""")

# ============================================================
# GAME TYPE 6: TYPING SPEED GAMES
# ============================================================
def make_typing_game(slug, title, accent):
    words = "code ship micro forge deploy build stack push pull merge react next node edge cloud data sync byte pixel grid loop hash salt key port host pipe flow rust swift dart go ruby python java"
    return responsive_game(title, accent, f"""
#word{{font-size:clamp(32px,7vw,56px);font-weight:900;color:{accent};text-align:center;
text-shadow:0 0 20px {accent}44;margin:clamp(16px,4vw,32px) 0}}
#inp{{width:90%;max-width:400px;padding:clamp(10px,2vw,16px);font-size:clamp(18px,4vw,28px);
background:#1e293b;border:2px solid #334155;color:#e2e8f0;text-align:center;
border-radius:12px;outline:none;font-family:inherit}}
#inp:focus{{border-color:{accent}}}
#wpm{{text-align:center;color:#64748b;margin-top:12px;font-size:clamp(12px,2.5vw,16px)}}
""", '<div id="word"></div><input id="inp" autocomplete="off" placeholder="Type the word...">', f"""
const words="{words}".split(' ');
const wordE=document.getElementById('word'),inp=document.getElementById('inp');
let current='',startTime=Date.now(),wordsTyped=0;

function next(){{current=words[Math.floor(Math.random()*words.length)];wordE.textContent=current;inp.value='';inp.focus()}}

inp.addEventListener('input',()=>{{
  if(inp.value.trim().toLowerCase()===current){{
    addScore(10);wordsTyped++;next();
  }}
}});

// Auto-focus on touch
area.addEventListener('pointerdown',()=>inp.focus());
next();
""")

# ============================================================
# GAME TYPE 7: REACTION TIMER
# ============================================================
def make_reaction_game(slug, title, accent):
    return responsive_game(title, accent, f"""
#board{{width:100%;height:100%;display:flex;align-items:center;justify-content:center;cursor:pointer}}
#msg{{font-size:clamp(20px,5vw,36px);text-align:center;color:#94a3b8;font-weight:700;padding:20px;line-height:1.5}}
""", '<div id="board"><div id="msg">Tap to Start</div></div>', f"""
const board=document.getElementById('board'),msg=document.getElementById('msg');
let state='idle',startTime,best=Infinity;

board.addEventListener('pointerdown',(e)=>{{
  e.preventDefault();
  if(state==='idle'){{
    state='wait';msg.textContent='Wait for GREEN...';msg.style.color='#ef4444';
    board.style.background='#0f172a';
    const delay=1500+Math.random()*3000;
    setTimeout(()=>{{
      if(state!=='wait')return;
      board.style.background='#059669';msg.textContent='TAP NOW!';msg.style.color='#fff';
      state='go';startTime=Date.now();
    }},delay);
  }}
  else if(state==='wait'){{
    msg.textContent='Too early! 😅\\nTap to retry';msg.style.color='#ef4444';
    board.style.background='#0f172a';state='idle';
  }}
  else if(state==='go'){{
    const ms=Date.now()-startTime;
    if(ms<best)best=ms;
    addScore(Math.max(0,500-ms));
    msg.textContent=ms+'ms\\nBest: '+best+'ms\\n\\nTap to retry';
    msg.style.color='{accent}';board.style.background='#0f172a';state='idle';
  }}
}});
""")

# ============================================================
# BUILD ALL GAMES
# ============================================================
games = [
    # Tap games
    ("whack-a-mole", "Whack-a-Mole", "🐹", "tap", 1000, 2200),
    ("emoji-catcher", "Emoji Catcher", "⭐", "tap", 1200, 2500),
    ("bug-squasher", "Bug Squasher", "🐛", "tap", 900, 2000),
    ("balloon-pop", "Balloon Pop", "🎈", "tap", 1100, 2300),
    ("gem-hunter", "Gem Hunter", "💎", "tap", 800, 1800),
    ("ufo-spotter", "UFO Spotter", "🛸", "tap", 1000, 2000),
    ("fruit-ninja", "Fruit Slicer", "🍉", "tap", 900, 2000),
    ("star-tap", "Star Tap", "✨", "tap", 1100, 2200),
    ("ghost-hunt", "Ghost Hunt", "👻", "tap", 800, 1600),
    ("rocket-catch", "Rocket Catch", "🚀", "tap", 1000, 2100),
    ("fish-tap", "Fish Tap", "🐟", "tap", 950, 2000),
    ("coin-grab", "Coin Grab", "🪙", "tap", 1100, 2400),
    ("diamond-rush", "Diamond Rush", "💠", "tap", 800, 1700),
    ("fire-fly", "Firefly Chase", "🪲", "tap", 900, 1900),
    ("planet-pop", "Planet Pop", "🪐", "tap", 1000, 2200),
    # Dodge games
    ("meteor-dodge", "Meteor Dodge", "dodge", "🚀", "☄️"),
    ("rain-runner", "Rain Runner", "dodge", "🏃", "💧"),
    ("fire-escape", "Fire Escape", "dodge", "🧑", "🔥"),
    ("virus-dodge", "Virus Dodge", "dodge", "🛡️", "🦠"),
    ("candy-fall", "Candy Fall", "dodge", "🧺", "🍬"),
    ("snowfall", "Snow Drift", "dodge", "⛷️", "❄️"),
    ("space-junk", "Space Junk", "dodge", "🛰️", "🪨"),
    ("leaf-catcher", "Leaf Catcher", "dodge", "🧤", "🍂"),
    ("arrow-dodge", "Arrow Dodge", "dodge", "🏹", "⬇️"),
    ("lava-run", "Lava Run", "dodge", "🏃", "🌋"),
    ("thunder-dodge", "Thunder Dodge", "dodge", "⚡", "🌩️"),
    # Memory games
    ("cyber-memory", "Cyber Memory", "memory"),
    ("neon-match", "Neon Match", "memory"),
    ("pixel-pairs", "Pixel Pairs", "memory"),
    ("astro-memory", "Astro Memory", "memory"),
    ("deep-recall", "Deep Recall", "memory"),
    ("mind-link", "Mind Link", "memory"),
    ("brain-grid", "Brain Grid", "memory"),
    ("flash-match", "Flash Match", "memory"),
    # Simon games
    ("simon-neon", "Simon Neon", "simon"),
    ("pattern-pro", "Pattern Pro", "simon"),
    ("beat-memory", "Beat Memory", "simon"),
    # Math games
    ("math-blitz", "Math Blitz", "math"),
    ("number-rush", "Number Rush", "math"),
    ("calc-attack", "Calc Attack", "math"),
    ("digit-duel", "Digit Duel", "math"),
    # Typing games
    ("code-typer", "Code Typer", "typing"),
    ("hacker-keys", "Hacker Keys", "typing"),
    ("speed-words", "Speed Words", "typing"),
    # Reaction games
    ("reflex-test", "Reflex Test", "reaction"),
    ("speed-click", "Speed Click", "reaction"),
    ("nerve-check", "Nerve Check", "reaction"),
]

EMOJIS_SETS = [
    "🚀,🎯,💎,🔥,⚡,🎮,🌟,🎲",
    "🐱,🐶,🦊,🐸,🦁,🐼,🐧,🦄",
    "🍎,🍊,🍋,🍇,🍓,🍑,🥝,🍒",
    "🌍,🌙,⭐,☀️,🌈,💫,🪐,🌊",
    "🏀,⚽,🎾,🏈,⚾,🎱,🏓,🥊",
    "🎸,🎹,🎺,🥁,🎻,🎵,🎤,🎼",
    "🚗,✈️,🚀,🚢,🚂,🚁,🏍️,🛸",
    "💻,📱,⌨️,🖥️,🎧,📷,🔋,💡",
]

print(f"Generating {len(games)} premium games...")

for i, g in enumerate(games):
    slug = g[0]
    title = g[1]
    c1, c2 = pick(i)
    
    # Detect game type from tuple
    if len(g) == 6 and g[3] == "tap":
        gtype = "tap"
    elif len(g) == 5 and g[2] == "dodge":
        gtype = "dodge"
    elif len(g) == 3:
        gtype = g[2]  # memory, simon, math, typing, reaction
    elif len(g) == 6:
        gtype = g[3]
    else:
        gtype = g[2]

    if gtype == "tap":
        emoji = g[2]
        rate = g[4] if len(g) > 4 else 1000
        life = g[5] if len(g) > 5 else 2200
        html = make_tap_game(slug, title, emoji, c1, rate, life)
    elif gtype == "dodge":
        player = g[3]
        enemy = g[4]
        html = make_dodge_game(slug, title, player, enemy, c1)
    elif gtype == "memory":
        emset = EMOJIS_SETS[i % len(EMOJIS_SETS)]
        html = make_memory_game(slug, title, c1, emset)
    elif gtype == "simon":
        html = make_simon_game(slug, title, c1)
    elif gtype == "math":
        html = make_math_game(slug, title, c1)
    elif gtype == "typing":
        html = make_typing_game(slug, title, c1)
    elif gtype == "reaction":
        html = make_reaction_game(slug, title, c1)
    else:
        print(f"  ⚠️ [{i+1}/{len(games)}] {title} — unknown type '{gtype}'")
        continue

    with open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(html)

    icon = g[2] if gtype == "tap" else (g[3] if gtype == "dodge" else "🎮")
    registry.append({
        "slug": slug, "title": title, "category": "Game",
        "icon": icon,
        "url": f"/games/{slug}.html", "isPremium": False
    })
    print(f"  ✅ [{i+1}/{len(games)}] {title}")

with open(os.path.join(OUT, "..", "..", "game_registry.json"), "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
print(f"\n🎉 Generated {len(registry)} premium-quality games!")
