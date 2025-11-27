/**
 * 30 Segundos v3.1 - Interface do Jogador (Celular)
 */

// ============================================
// ESTADO
// ============================================

let socket = null;
let gameId = null;
let gameState = null;
let currentRound = null;
let timerInterval = null;
let timeRemaining = 30;
let myHits = [];
let yellowWords = [];
let blueWords = [];
let currentSide = 'yellow';

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    gameId = params.get('game');
    
    if (!gameId) {
        alert('Código da partida não fornecido!');
        window.location.href = '/';
        return;
    }
    
    gameId = gameId.toUpperCase();
    document.getElementById('gameCode').textContent = gameId;
    
    connectSocket();
});

// ============================================
// FULLSCREEN
// ============================================

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
    } else {
        document.exitFullscreen();
    }
}

// ============================================
// SOCKET.IO
// ============================================

function connectSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('[Player] Conectado');
        socket.emit('join_game', { game_id: gameId, type: 'player' });
    });
    
    socket.on('game_state', (game) => {
        console.log('[Player] Estado:', game);
        gameState = game;
        
        if (gameState.state === 'waiting') {
            showScreen('screenWaiting');
        } else {
            showScreen('screenWaitingRound');
        }
    });
    
    socket.on('game_started', (game) => {
        console.log('[Player] Jogo iniciou');
        gameState = game;
    });
    
    socket.on('round_ready', (data) => {
        console.log('[Player] Rodada pronta:', data);
        gameState = data.game;
        currentRound = data.round;
        myHits = [];
        
        if (currentRound.is_challenge) {
            showChallengeReady();
        } else if (currentRound.is_cursed) {
            showCursedReady();
        } else {
            showNormalReady();
        }
    });
    
    socket.on('time_up', () => {
        console.log('[Player] Tempo esgotado');
        stopTimer();
        showScreen('screenTimeUp');
        document.getElementById('finalHits').textContent = myHits.length;
    });
    
    socket.on('round_confirmed', (data) => {
        console.log('[Player] Rodada confirmada');
        gameState = data.game;
        showScreen('screenWaitingRound');
    });
    
    socket.on('game_finished', (data) => {
        console.log('[Player] Jogo finalizado');
        stopTimer();
        showVictory(data.winner);
    });
    
    socket.on('error', (data) => {
        console.error('[Player] Erro:', data.message);
        alert(data.message);
    });
}

// ============================================
// TELAS
// ============================================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const screen = document.getElementById(screenId);
    if (screen) screen.classList.add('active');
}

// ============================================
// RODADA NORMAL
// ============================================

function showNormalReady() {
    showScreen('screenYourTurn');
    
    const isTeam1 = gameState.current_team === 1;
    const teamName = isTeam1 ? gameState.team1.name : gameState.team2.name;
    const position = isTeam1 ? gameState.team1.position : gameState.team2.position;
    
    document.getElementById('yourTeamName').textContent = teamName;
    document.getElementById('yourTeamName').className = 'team-name ' + (isTeam1 ? 'yellow' : 'blue');
    
    // Define lado inicial baseado na posição
    currentSide = position % 2 === 0 ? 'yellow' : 'blue';
    document.getElementById('startSide').textContent = currentSide === 'yellow' ? 'AMARELO' : 'AZUL';
    document.getElementById('startSide').className = 'start-side ' + currentSide;
}

function viewCard() {
    if (!currentRound?.card) return;
    
    socket.emit('player_view_card', { game_id: gameId });
    socket.emit('start_timer', { game_id: gameId });
    
    yellowWords = currentRound.card.yellow_words.map(w => ({...w, hit: false}));
    blueWords = currentRound.card.blue_words.map(w => ({...w, hit: false}));
    
    showScreen('screenPlaying');
    renderCurrentSide();
    startTimer();
}

function renderCurrentSide() {
    const indicator = document.getElementById('sideIndicator');
    const container = document.getElementById('wordsContainer');
    const words = currentSide === 'yellow' ? yellowWords : blueWords;
    
    indicator.textContent = currentSide === 'yellow' ? '🟡 AMARELO' : '🔵 AZUL';
    indicator.className = 'side-indicator ' + currentSide;
    
    container.innerHTML = words.map((w, i) => {
        let classes = 'word-btn';
        if (w.is_bonus) classes += ' bonus';
        if (w.hit) classes += ' hit';
        
        return `<button class="${classes}" data-index="${i}" onclick="hitWord(${i})">${w.text}</button>`;
    }).join('');
}

function hitWord(index) {
    const words = currentSide === 'yellow' ? yellowWords : blueWords;
    const word = words[index];
    
    if (word.hit) return;
    
    word.hit = true;
    myHits.push(word.text);
    
    socket.emit('word_hit', {
        game_id: gameId,
        word: word.text,
        is_bonus: word.is_bonus || false
    });
    
    // Vira o lado
    setTimeout(() => {
        currentSide = currentSide === 'yellow' ? 'blue' : 'yellow';
        renderCurrentSide();
    }, 200);
}

// ============================================
// DESAFIO
// ============================================

function showChallengeReady() {
    showScreen('screenChallenge');
    document.getElementById('challengeTextPlayer').textContent = currentRound.challenge_text;
}

function startChallenge() {
    socket.emit('start_timer', { game_id: gameId });
    showScreen('screenChallengeRunning');
    document.getElementById('challengeTextRunning').textContent = currentRound.challenge_text;
    startTimer();
}

// ============================================
// CARTA AMALDIÇOADA
// ============================================

function showCursedReady() {
    showScreen('screenCursed');
    document.getElementById('cursedWordPlayer').textContent = currentRound.cursed_word;
}

function startCursed() {
    socket.emit('start_timer', { game_id: gameId });
    showScreen('screenCursedRunning');
    document.getElementById('cursedWordRunning').textContent = currentRound.cursed_word;
    startTimer();
}

// ============================================
// TIMER
// ============================================

function startTimer() {
    timeRemaining = gameState?.config?.round_time || 30;
    updateTimerDisplay();
    
    timerInterval = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();
        
        if (timeRemaining <= 0) {
            endTimer();
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function endTimer() {
    stopTimer();
    socket.emit('timer_ended', { game_id: gameId });
}

function updateTimerDisplay() {
    const displays = ['timerPlayer', 'timerChallenge', 'timerCursed'];
    
    displays.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = timeRemaining;
            el.classList.remove('warning', 'danger');
            if (timeRemaining <= 5) el.classList.add('danger');
            else if (timeRemaining <= 10) el.classList.add('warning');
        }
    });
}

// ============================================
// VITÓRIA
// ============================================

function showVictory(winner) {
    showScreen('screenVictory');
    document.getElementById('winnerNamePlayer').textContent = winner;
}

function backToMenu() {
    window.location.href = '/';
}