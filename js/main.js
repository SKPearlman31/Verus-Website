// ── Navigation scroll effect
const navbar=document.getElementById('navbar');
window.addEventListener('scroll',()=>{navbar.classList.toggle('scrolled',window.scrollY>50)});

// ── Mobile nav
function toggleNav(){document.getElementById('navLinks').classList.toggle('open')}
function closeNav(){document.getElementById('navLinks').classList.remove('open')}

// ── Talent toggle (4 tabs: nba, gleague, college, intl)
const ROSTER_IDS=['nbaRoster','gleagueRoster','collegeRoster','intlRoster'];
function showTalent(type){
  const btns=document.querySelectorAll('.talent-toggle button');
  btns.forEach(b=>b.classList.remove('active'));
  event.currentTarget.classList.add('active');
  const activeId=type+'Roster';
  ROSTER_IDS.forEach(id=>{
    const el=document.getElementById(id);
    if(el) el.classList.toggle('hidden',id!==activeId);
  });
  document.querySelectorAll(`#${activeId} .reveal`).forEach(el=>el.classList.add('visible'));
}

// ── Scroll reveal
const observer=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target)}})
},{threshold:0.1,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

// ── Instagram link HTML helper
function igLink(handle){
  if(!handle) return '';
  return `<a href="https://www.instagram.com/${handle}/" target="_blank" rel="noopener" class="player-ig"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg> @${handle}</a>`;
}

// ── Build a standard player card (NBA / G-League with stats)
function buildProCard(p){
  const stats=p.stats||{};
  const photo=p.headshot_local
    ? `<img src="${resolveImg(p.headshot_local)}" alt="${p.name}" onerror="this.onerror=null;this.src='${p.headshot_nba||''}';">`
    : `<span class="placeholder">V</span>`;
  const team=p.team||'—';
  const showNbaRow=p.stats||p.gleague_stats;
  const statsHtml=showNbaRow
    ? `<div class="player-stats">
        <div class="stat"><span class="stat-val">${stats.ppg??'—'}</span><span class="stat-label">PPG</span></div>
        <div class="stat"><span class="stat-val">${stats.rpg??'—'}</span><span class="stat-label">RPG</span></div>
        <div class="stat"><span class="stat-val">${stats.apg??'—'}</span><span class="stat-label">APG</span></div>
      </div>`
    : '';
  const gl=p.gleague_stats;
  const glHtml=gl
    ? `<div class="player-stats player-stats-gl">
        <div class="stat-gl-label">G-League</div>
        <div class="stat"><span class="stat-val">${gl.ppg??'—'}</span><span class="stat-label">PPG</span></div>
        <div class="stat"><span class="stat-val">${gl.rpg??'—'}</span><span class="stat-label">RPG</span></div>
        <div class="stat"><span class="stat-val">${gl.apg??'—'}</span><span class="stat-label">APG</span></div>
      </div>`
    : '';
  const card=document.createElement('div');
  card.className='player-card reveal visible';
  card.innerHTML=`
    <div class="player-photo">${photo}</div>
    <div class="player-info">
      <div class="player-name">${p.name}</div>
      <div class="player-detail">${p.position} — ${team}</div>
      ${statsHtml}
      ${glHtml}
      ${igLink(p.ig)}
    </div>`;
  return card;
}

// ── Build a college/NIL player card
function buildCollegeCard(p){
  const stats=p.stats||{};
  const isHS=p.type==='highschool';
  const fallback=p.headshot_espn
    ? `this.onerror=null;this.src='${p.headshot_espn}';`
    : `this.onerror=null;this.parentElement.innerHTML='<span class=\\'placeholder\\'>V</span>';`;
  const imgClass=isHS?' class="photo-contain"':'';
  const photo=p.headshot_local
    ? `<img${imgClass} src="${resolveImg(p.headshot_local)}" alt="${p.name}" onerror="${fallback}">`
    : `<span class="placeholder">V</span>`;
  const detail=isHS
    ? `High School — Class of ${p.class_year||2026}`
    : p.school ? `${p.position} — ${p.school}` : p.position;

  let statsHtml='';
  if(isHS){
    statsHtml=`<div class="player-commit">Committed to ${p.commitment}</div>`;
  } else if(p.stats){
    statsHtml=`<div class="player-stats">
      <div class="stat"><span class="stat-val">${stats.ppg??'—'}</span><span class="stat-label">PPG</span></div>
      <div class="stat"><span class="stat-val">${stats.rpg??'—'}</span><span class="stat-label">RPG</span></div>
      <div class="stat"><span class="stat-val">${stats.apg??'—'}</span><span class="stat-label">APG</span></div>
    </div>`;
  }
  const card=document.createElement('div');
  card.className='player-card reveal visible';
  card.innerHTML=`
    <div class="player-photo">${photo}</div>
    <div class="player-info">
      <div class="player-name">${p.name}</div>
      <div class="player-detail">${detail}</div>
      ${statsHtml}
      ${igLink(p.ig)}
    </div>`;
  return card;
}

// ── Build an international player card
function buildIntlCard(p){
  const stats=p.stats||{};
  const photo=p.headshot_local
    ? `<img src="${resolveImg(p.headshot_local)}" alt="${p.name}" onerror="this.onerror=null;this.parentElement.innerHTML='<span class=\\'placeholder\\'>V</span>';">`
    : `<span class="placeholder">V</span>`;
  const statsHtml=p.stats
    ? `<div class="player-stats">
        <div class="stat"><span class="stat-val">${stats.ppg??'—'}</span><span class="stat-label">PPG</span></div>
        <div class="stat"><span class="stat-val">${stats.rpg??'—'}</span><span class="stat-label">RPG</span></div>
        <div class="stat"><span class="stat-val">${stats.apg??'—'}</span><span class="stat-label">APG</span></div>
      </div>`
    : '';
  const card=document.createElement('div');
  card.className='player-card reveal visible';
  card.innerHTML=`
    <div class="player-photo">${photo}</div>
    <div class="player-info">
      <div class="player-name">${p.name}</div>
      <div class="player-detail">${p.position} — ${p.team}</div>
      ${statsHtml}
      ${igLink(p.ig)}
    </div>`;
  return card;
}

// ── Resolve image paths (prepend themeUrl for WordPress, noop for static)
function resolveImg(path){
  if(!path) return '';
  if(path.startsWith('http')) return path;
  var base=(typeof VERUS_WP!=='undefined' && VERUS_WP.themeUrl)?VERUS_WP.themeUrl+'/':'';
  return base+path;
}

// ── Load roster from ROSTER_DATA (embedded via roster-data.js)
(function loadRoster(){
  var data=typeof VERUS_ROSTER!=='undefined'?VERUS_ROSTER:(typeof ROSTER_DATA!=='undefined'?ROSTER_DATA:null);
  if(!data) return;

  var nbaGrid=document.getElementById('nbaRoster');
  if(nbaGrid && data.nba && data.nba.length){
    nbaGrid.innerHTML='';
    data.nba.forEach(function(p){nbaGrid.appendChild(buildProCard(p))});
  }

  var glGrid=document.getElementById('gleagueRoster');
  if(glGrid && data.gleague && data.gleague.length){
    glGrid.innerHTML='';
    data.gleague.forEach(function(p){glGrid.appendChild(buildProCard(p))});
  }

  var collegeGrid=document.getElementById('collegeRoster');
  if(collegeGrid && data.college && data.college.length){
    collegeGrid.innerHTML='';
    data.college.forEach(function(p){collegeGrid.appendChild(buildCollegeCard(p))});
  }

  var intlGrid=document.getElementById('intlRoster');
  if(intlGrid && data.international && data.international.length){
    intlGrid.innerHTML='';
    data.international.forEach(function(p){intlGrid.appendChild(buildIntlCard(p))});
  }

  if(data.updated){
    var el=document.getElementById('rosterUpdated');
    if(el) el.textContent='Stats updated: '+new Date(data.updated).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
  }
})();

// ── Contact form (client-side feedback)
document.getElementById('contactForm').addEventListener('submit',function(e){
  // If using FormSubmit, it handles the redirect. For local preview:
  // e.preventDefault();
  // document.getElementById('contactForm').style.display='none';
  // document.getElementById('formSuccess').style.display='block';
});
