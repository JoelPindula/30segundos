/**
 * 30 Segundos v3.1 - Tabuleiro (TV/Monitor)
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
let confirmedWords = [];
let playerConnected = false;

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    gameId = params.get('game');
    
    if (!gameId) {
        alert('Código da partida não fornecido!');
        window.location.href = '/admin';
        return;
    }
    
    gameId = gameId.toUpperCase();
    document.getElementById('gameCode').textContent = gameId;
    
    connectSocket();
    generateTracks();
    loadQRCode();
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
        console.log('[Board] Conectado');
        socket.emit('join_game', { game_id: gameId, type: 'board' });
    });
    
    socket.on('game_state', (game) => {
        console.log('[Board] Estado:', game);
        gameState = game;
        updateUI();
        
        if (gameState.state === 'waiting') {
            showState('stateWaiting');
        }
    });
    
    socket.on('player_connected', (data) => {
        console.log('[Board] Jogador conectou:', data);
        playerConnected = true;
        updateWaitingStatus();
    });
    
    socket.on('game_started', (game) => {
        console.log('[Board] Jogo iniciado');
        gameState = game;
        updateUI();
    });
    
    socket.on('round_ready', (data) => {
        console.log('[Board] Rodada pronta:', data);
        gameState = data.game;
        currentRound = data.round;
        
        updateUI();
        
        if (currentRound.is_challenge) {
            showState('stateChallenge');
            document.getElementById('challengeText').textContent = currentRound.challenge_text;
        } else if (currentRound.is_cursed) {
            showState('stateCursed');
            document.getElementById('cursedWord').textContent = currentRound.cursed_word;
        } else {
            showState('statePlayerTurn');
            updateCurrentTeamDisplay();
        }
    });
    
    socket.on('timer_started', (data) => {
        console.log('[Board] Timer iniciado');
        currentRound = data.round;
        gameState = data.game;
        
        if (currentRound.is_challenge) {
            showState('stateChallengeTimer');
            document.getElementById('challengeTextTimer').textContent = currentRound.challenge_text;
        } else if (currentRound.is_cursed) {
            showState('stateCursedTimer');
            document.getElementById('cursedWordTimer').textContent = currentRound.cursed_word;
        } else {
            showState('stateTimerRunning');
            updatePlayingTeamIndicator();
        }
        
        startTimer();
    });
    
    socket.on('player_hit', (data) => {
        console.log('[Board] Hit:', data.word);
    });
    
    socket.on('time_up', (data) => {
        console.log('[Board] Tempo esgotado');
        stopTimer();
        currentRound = data.round;
        gameState = data.game;
        
        updateUI();
        
        if (currentRound.is_challenge) {
            showState('stateChallengeConfirm');
        } else if (currentRound.is_cursed) {
            showState('stateCursedConfirm');
        } else {
            showConfirmation(data.player_hits);
        }
    });
    
    socket.on('round_confirmed', (data) => {
        console.log('[Board] Rodada confirmada');
        gameState = data.game;
        hideConfirmationModal();
        updateUI();
        showRoundResult(data.result);
    });
    
    socket.on('game_finished', (data) => {
        console.log('[Board] Jogo finalizado');
        showVictory(data.winner);
    });
    
    socket.on('error', (data) => {
        console.error('[Board] Erro:', data.message);
        alert(data.message);
    });
}

// ============================================
// ATUALIZAR STATUS DE AGUARDANDO
// ============================================

function updateWaitingStatus() {
    const statusEl = document.getElementById('waitingStatus');
    const btnEl = document.getElementById('btnStartGame');
    
    if (playerConnected) {
        if (statusEl) {
            statusEl.innerHTML = '<span class="status-connected">✅ Jogador Conectado!</span>';
        }
        if (btnEl) {
            btnEl.classList.add('ready');
            btnEl.innerHTML = '▶️ Iniciar Partida';
        }
    }
}

// ============================================
// TRILHAS
// ============================================

function generateTracks() {
    generateTrack('track1Cells', 'yellow');
    generateTrack('track2Cells', 'blue');
}

function generateTrack(containerId, teamColor) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    for (let i = 0; i <= 30; i++) {
        const cell = document.createElement('div');
        cell.className = 'track-cell';
        cell.id = `${teamColor}-cell-${i}`;
        
        if (i === 0) {
            cell.classList.add('start');
            cell.textContent = '🏁';
        } else if (i === 30) {
            cell.classList.add('finish');
            cell.textContent = '🏆';
        } else {
            cell.textContent = i;
        }
        
        container.appendChild(cell);
    }
}

function updateTracks() {
    if (!gameState) return;
    
    const pos1 = Math.min(30, gameState.team1.position);
    const pos2 = Math.min(30, gameState.team2.position);
    
    for (let i = 0; i <= 30; i++) {
        const cell1 = document.getElementById(`yellow-cell-${i}`);
        const cell2 = document.getElementById(`blue-cell-${i}`);
        
        if (cell1) {
            cell1.classList.remove('passed', 'current');
            if (i < pos1) cell1.classList.add('passed');
            else if (i === pos1) cell1.classList.add('current');
        }
        
        if (cell2) {
            cell2.classList.remove('passed', 'current');
            if (i < pos2) cell2.classList.add('passed');
            else if (i === pos2) cell2.classList.add('current');
        }
    }
}

// ============================================
// QR CODE
// ============================================

async function loadQRCode() {
    try {
        const response = await fetch(`/api/games/${gameId}/qrcode`);
        const data = await response.json();
        
        if (data.qr_code) {
            document.getElementById('qrContainer').innerHTML = `<img src="${data.qr_code}" alt="QR Code">`;
        }
        document.getElementById('playerUrl').textContent = data.player_url;
    } catch (error) {
        console.error('Erro QR:', error);
    }
}

// ============================================
// UI
// ============================================

function updateUI() {
    if (!gameState) return;
    
    document.getElementById('gameName').textContent = gameState.name;
    document.getElementById('roundNumber').textContent = gameState.current_round;
    
    document.getElementById('team1Name').textContent = gameState.team1.name;
    document.getElementById('team1Position').textContent = gameState.team1.position;
    document.getElementById('team1Player').textContent = gameState.team1.current_player?.name || '-';
    
    document.getElementById('team2Name').textContent = gameState.team2.name;
    document.getElementById('team2Position').textContent = gameState.team2.position;
    document.getElementById('team2Player').textContent = gameState.team2.current_player?.name || '-';
    
    updateTracks();
}

function updateCurrentTeamDisplay() {
    if (!gameState) return;
    
    const isTeam1 = gameState.current_team === 1;
    const display = document.getElementById('currentTeamDisplay');
    const playerDisplay = document.getElementById('currentPlayerDisplay');
    
    display.textContent = isTeam1 ? gameState.team1.name : gameState.team2.name;
    display.className = 'current-team ' + (isTeam1 ? 'team-yellow' : 'team-blue');
    
    if (playerDisplay) {
        playerDisplay.textContent = isTeam1 
            ? gameState.team1.current_player?.name || '-'
            : gameState.team2.current_player?.name || '-';
    }
}

function updatePlayingTeamIndicator() {
    if (!gameState) return;
    
    const isTeam1 = gameState.current_team === 1;
    const indicator = document.getElementById('playingTeamIndicator');
    
    if (indicator) {
        indicator.textContent = isTeam1 ? gameState.team1.name : gameState.team2.name;
        indicator.className = 'playing-team-indicator ' + (isTeam1 ? 'team-yellow' : 'team-blue');
    }
}

// ============================================
// ESTADOS
// ============================================

function showState(stateId) {
    document.querySelectorAll('.state-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(stateId);
    if (panel) panel.classList.add('active');
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
        if (timeRemaining <= 0) stopTimer();
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay() {
    const displays = ['timerDisplayLarge', 'challengeTimerDisplay', 'cursedTimerDisplay'];
    
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
// CONFIRMAÇÃO RODADA NORMAL
// ============================================

function showConfirmation(playerHits) {
    confirmedWords = [...playerHits];
    
    if (!currentRound?.card) return;
    
    const yellowContainer = document.getElementById('yellowConfirmList');
    const blueContainer = document.getElementById('blueConfirmList');
    
    yellowContainer.innerHTML = currentRound.card.yellow_words.map(w => {
        let classes = 'confirm-word';
        if (w.is_bonus) classes += ' bonus';
        if (playerHits.includes(w.text)) classes += ' pre-selected confirmed';
        
        return `<div class="${classes}" data-word="${w.text}" onclick="toggleConfirmWord(this)">${w.text}</div>`;
    }).join('');
    
    blueContainer.innerHTML = currentRound.card.blue_words.map(w => {
        let classes = 'confirm-word';
        if (w.is_bonus) classes += ' bonus';
        if (playerHits.includes(w.text)) classes += ' pre-selected confirmed';
        
        return `<div class="${classes}" data-word="${w.text}" onclick="toggleConfirmWord(this)">${w.text}</div>`;
    }).join('');
    
    updateConfirmedCount();
    document.getElementById('confirmationModal').classList.add('active');
}

function hideConfirmationModal() {
    document.getElementById('confirmationModal').classList.remove('active');
}

function toggleConfirmWord(element) {
    const word = element.dataset.word;
    
    if (element.classList.contains('confirmed')) {
        element.classList.remove('confirmed');
        confirmedWords = confirmedWords.filter(w => w !== word);
    } else {
        element.classList.add('confirmed');
        if (!confirmedWords.includes(word)) confirmedWords.push(word);
    }
    
    updateConfirmedCount();
}

function updateConfirmedCount() {
    document.getElementById('confirmedCount').textContent = confirmedWords.length;
}

function confirmRound() {
    socket.emit('confirm_round', {
        game_id: gameId,
        confirmed_words: confirmedWords
    });
    confirmedWords = [];
}

// ============================================
// DESAFIO
// ============================================

function challengeSuccess() {
    socket.emit('challenge_result', { game_id: gameId, completed: true });
}

function challengeFail() {
    socket.emit('challenge_result', { game_id: gameId, completed: false });
}

// ============================================
// CARTA AMALDIÇOADA
// ============================================

function cursedSuccess() {
    socket.emit('cursed_result', { game_id: gameId, guessed: true });
}

function cursedFail() {
    socket.emit('cursed_result', { game_id: gameId, guessed: false });
}

// ============================================
// RESULTADO
// ============================================

function showRoundResult(result) {
    showState('stateRoundResult');
    
    const titleEl = document.getElementById('resultTitle');
    const movesEl = document.getElementById('resultMoves');
    
    if (result.was_challenge) {
        if (result.completed) {
            titleEl.textContent = '✅ Desafio Completado!';
            titleEl.className = 'result-title success';
        } else {
            titleEl.textContent = '❌ Desafio Falhou!';
            titleEl.className = 'result-title fail';
        }
    } else if (result.was_cursed) {
        if (result.guessed) {
            titleEl.textContent = '💀 Palavra Adivinhada!';
            titleEl.className = 'result-title success';
        } else {
            titleEl.textContent = '💀 Não Adivinharam!';
            titleEl.className = 'result-title fail';
        }
    } else {
        titleEl.textContent = 'Rodada Finalizada!';
        titleEl.className = 'result-title';
    }
    
    if (result.moves >= 0) {
        movesEl.textContent = '+' + result.moves + ' casas';
        movesEl.className = 'result-moves positive';
    } else {
        movesEl.textContent = result.moves + ' casas';
        movesEl.className = 'result-moves negative';
    }
}

// ============================================
// CONTROLES
// ============================================

function startGame() {
    if (!playerConnected) {
        alert('Aguarde um jogador conectar primeiro!');
        return;
    }
    socket.emit('start_game', { game_id: gameId });
}

function nextRound() {
    socket.emit('request_round', { game_id: gameId });
}

// ============================================
// VITÓRIA
// ============================================

function showVictory(winner) {
    stopTimer();
    hideConfirmationModal();
    updateUI();
    
    document.getElementById('winnerName').textContent = winner;
    document.getElementById('victoryModal').classList.add('active');
}

function backToMenu() {
    window.location.href = '/';
}

function newGame() {
    window.location.href = '/admin';
}