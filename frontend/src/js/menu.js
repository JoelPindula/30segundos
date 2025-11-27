/**
 * 30 Segundos v3.0 - Menu Principal
 */

// ============================================
// FUNÇÕES DO MODAL
// ============================================

function showJoinGame() {
    document.getElementById('joinModal').style.display = 'flex';
    const input = document.getElementById('gameCodeInput');
    input.value = '';
    input.focus();
}

function hideJoinGame() {
    document.getElementById('joinModal').style.display = 'none';
}

function joinGame() {
    const code = document.getElementById('gameCodeInput').value.trim().toUpperCase();
    
    if (!code) {
        alert('Digite o código da partida!');
        return;
    }
    
    if (code.length < 4) {
        alert('Código inválido! O código deve ter 4 caracteres.');
        return;
    }
    
    // Redireciona para a página do jogador
    window.location.href = `/player?game=${code}`;
}

// ============================================
// EVENT LISTENERS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('gameCodeInput');
    
    if (input) {
        // Enter para confirmar
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                joinGame();
            }
        });
        
        // Escape para fechar
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hideJoinGame();
            }
        });
        
        // Auto uppercase
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }
    
    // Fecha modal ao clicar fora
    const modal = document.getElementById('joinModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideJoinGame();
            }
        });
    }
});