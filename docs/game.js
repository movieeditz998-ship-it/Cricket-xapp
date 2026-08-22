// Very small quick-match cricket prototype
const oversLimit = 2; // 2 overs = 12 balls (quick)
let ballsPerOver = 6;
let currentOver = 0, currentBall = 0, score = 0, wickets = 0;
let running = false;
let ballTimer = null;
let lastTouch = null;

const oversEl = document.getElementById('overs');
const ballsEl = document.getElementById('balls');
const scoreEl = document.getElementById('score');
const startBtn = document.getElementById('startBtn');
const saveBtn = document.getElementById('saveBtn');
const showLeagueBtn = document.getElementById('showLeagueBtn');
const logEl = document.getElementById('log');
const leagueDiv = document.getElementById('league');
const leagueTable = document.getElementById('leagueTable');
const playArea = document.getElementById('play-area');
const ballEl = document.getElementById('ball');

function log(s){
  logEl.textContent = s + '\n' + logEl.textContent;
}

function resetMatch(){
  currentOver = 0; currentBall = 0; score = 0; wickets = 0;
  updateHUD();
  running = false;
  clearInterval(ballTimer);
}

function updateHUD(){
  oversEl.textContent = currentOver + '/' + oversLimit;
  ballsEl.textContent = currentBall + '/' + ballsPerOver;
  scoreEl.textContent = score + '/' + wickets;
}

function startMatch(){
  resetMatch();
  running = true;
  log('Match started — 2 overs. Get ready!');
  // start ball loop
  ballTimer = setInterval(nextBall, 1400);
  nextBall();
}

function endMatch(){
  running = false;
  clearInterval(ballTimer);
  log('Match finished. Score: ' + score + '/' + wickets);
  alert('Match finished. Score: ' + score + '/' + wickets);
}

function nextBall(){
  if(!running) return;
  if(currentOver >= oversLimit){
    endMatch();
    return;
  }
  // ball animation
  ballEl.style.transform = 'translateY(80px)';
  setTimeout(()=>{ ballEl.style.transform = 'translateY(-120px)'; }, 600);

  // random 'good' shot direction allowed this ball
  const allowed = ['up','left','right'];
  const allowedShot = allowed[Math.floor(Math.random()*allowed.length)];
  log('Ball incoming — try a swipe. (Prefer ' + allowedShot + ')');

  // wait 1.2s for user input. If no input, dot ball
  lastTouch = null;
  const ballIndex = currentBall;
  setTimeout(()=>{
    // resolve this ball only if still the same ball index
    if(ballIndex !== currentBall) return; // already handled
    // check lastTouch
    let result = 'Dot';
    if(lastTouch){
      // if swipe direction equals allowedShot, score runs
      if(lastTouch === allowedShot){
        const runs = [4,6,1,2,3][Math.floor(Math.random()*5)];
        score += runs;
        result = runs + ' runs! ('+lastTouch+')';
      } else {
        // 8% chance of wicket on wrong shot
        if(Math.random() < 0.08){ wickets += 1; result = 'OUT!'; }
        else { result = 'Mistimed - Dot'; }
      }
    }
    log('Ball result: ' + result);
    // increment ball
    currentBall += 1;
    if(currentBall >= ballsPerOver){ currentBall = 0; currentOver += 1; }
    updateHUD();
    if(currentOver >= oversLimit) endMatch();
  }, 900);
}

// Input handling for swipe detection (simple)
let touchStart = null;
function getDirection(dx,dy){
  if(Math.abs(dx) > Math.abs(dy)){
    return dx > 0 ? 'right' : 'left';
  } else {
    return dy < 0 ? 'up' : 'down';
  }
}

playArea.addEventListener('pointerdown', (e)=>{
  touchStart = {x:e.clientX, y:e.clientY};
});
playArea.addEventListener('pointerup', (e)=>{
  if(!touchStart) return;
  const dx = e.clientX - touchStart.x;
  const dy = e.clientY - touchStart.y;
  if(Math.hypot(dx,dy) < 20) return; // ignore tiny taps
  const dir = getDirection(dx,dy);
  lastTouch = dir;
  log('You swiped: ' + dir);
  touchStart = null;
});

startBtn.addEventListener('click', ()=>{ startMatch(); });

// League storage (very minimal)
function loadLeague(){
  const raw = localStorage.getItem('quick_cricket_league');
  if(!raw) return [];
  try{ return JSON.parse(raw); }catch(e){ return []; }
}
function saveLeague(standing){
  const data = loadLeague();
  data.push(standing);
  localStorage.setItem('quick_cricket_league', JSON.stringify(data));
}

saveBtn.addEventListener('click', ()=>{
  if(running){ alert('Finish the match first.'); return; }
  const name = prompt('Enter team name to save result for (e.g., Mumbai Titans):','My Team');
  if(!name) return;
  const standing = {team:name, score:score, wickets:wickets, overs:currentOver+"/"+oversLimit, when: new Date().toISOString()};
  saveLeague(standing);
  alert('Result saved to localStorage. Click Show League to view.');
});

showLeagueBtn.addEventListener('click', ()=>{
  const data = loadLeague();
  if(data.length===0){ alert('No league results yet. Save a result first.'); return; }
  leagueDiv.classList.remove('hidden');
  // build table
  leagueTable.innerHTML = '';
  const header = document.createElement('tr');
  header.innerHTML = '<th>Team</th><th>Score</th><th>W</th><th>Overs</th><th>When</th>';
  leagueTable.appendChild(header);
  data.slice().reverse().forEach(r=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.team}</td><td>${r.score}</td><td>${r.wickets}</td><td>${r.overs}</td><td>${new Date(r.when).toLocaleString()}</td>`;
    leagueTable.appendChild(tr);
  });
});

// initialize HUD
updateHUD();
log('Prototype ready. Press Start.');
