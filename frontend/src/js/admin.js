/**
 * 30 Segundos v3.1 - Painel Admin
 * IMPORTANTE: Este arquivo substitui completamente o anterior
 */

// ============================================
// ESTADO
// ============================================

let selectedThemes = ['geral'];
let selectedLevels = [1, 2];
let availableThemes = [];
let availableLevels = [];

// ============================================
// INICIALIZAÇÃO
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[Admin] Inicializando v3.1...');
    loadThemesAndLevels();
});

// ============================================
// CARREGAR TEMAS E NÍVEIS (ROTA CORRETA: /api/themes)
// ============================================

async function loadThemesAndLevels() {
    console.log('[Admin] Carregando temas e níveis...');
    
    try {
        const response = await fetch('/api/themes');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[Admin] Dados recebidos:', data);
        
        // Garante que são arrays
        availableThemes = Array.isArray(data.themes) ? data.themes : [];
        availableLevels = Array.isArray(data.levels) ? data.levels : [];
        
        console.log('[Admin] Temas:', availableThemes.length);
        console.log('[Admin] Níveis:', availableLevels.length);
        
        renderThemes();
        renderLevels();
        
    } catch (error) {
        console.error('[Admin] Erro ao carregar:', error);
        
        // Usa valores padrão
        availableThemes = [
            { id: 'geral', name: 'Geral', word_count: 100 }
        ];
        availableLevels = [
            { level: 1, name: 'Fácil', color: '#2ecc71' },
            { level: 2, name: 'Médio', color: '#f39c12' },
            { level: 3, name: 'Difícil', color: '#e74c3c' }
        ];
        
        renderThemes();
        renderLevels();
    }
}

// ============================================
// RENDERIZAR TEMAS
// ============================================

function renderThemes() {
    const container = document.getElementById('themesContainer');
    if (!container) {
        console.error('[Admin] Container de temas não encontrado');
        return;
    }
    
    if (!availableThemes || availableThemes.length === 0) {
        container.innerHTML = '<p class="error-text">Nenhum tema disponível</p>';
        return;
    }
    
    container.innerHTML = availableThemes.map(theme => {
        const isSelected = selectedThemes.includes(theme.id);
        return `
            <label class="checkbox-item ${isSelected ? 'selected' : ''}">
                <input type="checkbox" 
                       value="${theme.id}" 
                       ${isSelected ? 'checked' : ''}
                       onchange="toggleTheme('${theme.id}')">
                <span class="checkbox-label">
                    <span class="theme-name">${theme.name}</span>
                    <span class="theme-count">${theme.word_count} palavras</span>
                </span>
            </label>
        `;
    }).join('');
    
    console.log('[Admin] Temas renderizados');
}

// ============================================
// RENDERIZAR NÍVEIS
// ============================================

function renderLevels() {
    const container = document.getElementById('levelsContainer');
    if (!container) {
        console.error('[Admin] Container de níveis não encontrado');
        return;
    }
    
    if (!availableLevels || availableLevels.length === 0) {
        container.innerHTML = '<p class="error-text">Nenhum nível disponível</p>';
        return;
    }
    
    container.innerHTML = availableLevels.map(level => {
        const isSelected = selectedLevels.includes(level.level);
        return `
            <label class="checkbox-item ${isSelected ? 'selected' : ''}" 
                   style="--level-color: ${level.color}">
                <input type="checkbox" 
                       value="${level.level}" 
                       ${isSelected ? 'checked' : ''}
                       onchange="toggleLevel(${level.level})">
                <span class="checkbox-label">
                    <span class="level-dot" style="background: ${level.color}"></span>
                    <span>${level.name}</span>
                </span>
            </label>
        `;
    }).join('');
    
    console.log('[Admin] Níveis renderizados');
}

// ============================================
// TOGGLE SELEÇÕES
// ============================================

function toggleTheme(themeId) {
    const index = selectedThemes.indexOf(themeId);
    
    if (index > -1) {
        selectedThemes.splice(index, 1);
    } else {
        selectedThemes.push(themeId);
    }
    
    // Garante pelo menos um tema
    if (selectedThemes.length === 0) {
        selectedThemes = ['geral'];
    }
    
    renderThemes();
}

function toggleLevel(level) {
    const index = selectedLevels.indexOf(level);
    
    if (index > -1) {
        selectedLevels.splice(index, 1);
    } else {
        selectedLevels.push(level);
    }
    
    // Garante pelo menos um nível
    if (selectedLevels.length === 0) {
        selectedLevels = [1];
    }
    
    renderLevels();
}

// ============================================
// CRIAR PARTIDA
// ============================================

async function createGame() {
    console.log('[Admin] Criando partida...');
    
    const gameName = document.getElementById('gameName')?.value || 'Partida 30 Segundos';
    const team1Name = document.getElementById('team1Name')?.value || 'Time Amarelo';
    const team2Name = document.getElementById('team2Name')?.value || 'Time Azul';
    const roundTime = parseInt(document.getElementById('roundTime')?.value) || 30;
    const wordsPerSide = parseInt(document.getElementById('wordsPerSide')?.value) || 5;
    
    // Coleta jogadores do time 1
    const team1Players = [];
    document.querySelectorAll('#team1Players .player-input').forEach(input => {
        const name = input.value.trim();
        if (name) team1Players.push(name);
    });
    if (team1Players.length === 0) team1Players.push('Jogador 1');
    
    // Coleta jogadores do time 2
    const team2Players = [];
    document.querySelectorAll('#team2Players .player-input').forEach(input => {
        const name = input.value.trim();
        if (name) team2Players.push(name);
    });
    if (team2Players.length === 0) team2Players.push('Jogador 1');
    
    const gameData = {
        name: gameName,
        team1_name: team1Name,
        team1_players: team1Players,
        team2_name: team2Name,
        team2_players: team2Players,
        themes: selectedThemes,
        levels: selectedLevels,
        round_time: roundTime,
        words_per_side: wordsPerSide,
        challenge_frequency: 3,
        bonus_chance: 0.15,
        cursed_chance: 0.10
    };
    
    console.log('[Admin] Dados da partida:', gameData);
    
    try {
        const response = await fetch('/api/games', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(gameData)
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }
        
        const data = await response.json();
        console.log('[Admin] Partida criada:', data);
        
        const gameId = data.game.id;
        window.location.href = `/board?game=${gameId}`;
        
    } catch (error) {
        console.error('[Admin] Erro ao criar partida:', error);
        alert('Erro ao criar partida: ' + error.message);
    }
}

// ============================================
// GERENCIAR JOGADORES
// ============================================

function addPlayer(teamNumber) {
    const container = document.getElementById(`team${teamNumber}Players`);
    if (!container) return;
    
    const playerCount = container.querySelectorAll('.player-input').length + 1;
    
    const playerDiv = document.createElement('div');
    playerDiv.className = 'player-item';
    playerDiv.innerHTML = `
        <input type="text" class="player-input" placeholder="Jogador ${playerCount}" value="">
        <button type="button" class="btn-remove" onclick="removePlayer(this)">✕</button>
    `;
    
    container.appendChild(playerDiv);
}

function removePlayer(button) {
    const playerItem = button.closest('.player-item');
    const container = playerItem.parentElement;
    
    // Mantém pelo menos 1 jogador
    if (container.querySelectorAll('.player-item').length > 1) {
        playerItem.remove();
    }
}