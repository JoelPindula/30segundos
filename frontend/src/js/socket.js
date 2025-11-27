/**
 * socket.js - Gerenciador de conexão Socket.IO
 * 30 Segundos v2.0
 */

const socketManager = {
    socket: null,
    gameId: null,
    role: null,
    connected: false,
    
    /**
     * Conecta ao servidor Socket.IO
     */
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                console.log('[Socket] Conectando ao servidor...');
                
                this.socket = io({
                    transports: ['websocket', 'polling'],
                    timeout: 10000,
                    reconnection: true,
                    reconnectionAttempts: 5,
                    reconnectionDelay: 1000
                });
                
                this.socket.on('connect', () => {
                    console.log('[Socket] Conectado! ID:', this.socket.id);
                    this.connected = true;
                    resolve();
                });
                
                this.socket.on('connect_error', (error) => {
                    console.error('[Socket] Erro de conexão:', error.message);
                    this.connected = false;
                    reject(error);
                });
                
                this.socket.on('disconnect', (reason) => {
                    console.log('[Socket] Desconectado:', reason);
                    this.connected = false;
                });
                
                this.socket.on('reconnect', (attemptNumber) => {
                    console.log('[Socket] Reconectado após', attemptNumber, 'tentativas');
                    this.connected = true;
                    // Re-entra no jogo se estava em um
                    if (this.gameId && this.role) {
                        this.joinGame(this.gameId, this.role);
                    }
                });
                
            } catch (error) {
                console.error('[Socket] Erro ao criar conexão:', error);
                reject(error);
            }
        });
    },
    
    /**
     * Registra um listener de evento
     */
    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);
        } else {
            console.warn('[Socket] Socket não inicializado');
        }
    },
    
    /**
     * Remove um listener de evento
     */
    off(event, callback) {
        if (this.socket) {
            this.socket.off(event, callback);
        }
    },
    
    /**
     * Emite um evento para o servidor
     */
    emit(event, data = {}) {
        if (this.socket && this.connected) {
            console.log('[Socket] Emitindo:', event, data);
            this.socket.emit(event, data);
        } else {
            console.warn('[Socket] Não conectado, não foi possível emitir:', event);
        }
    },
    
    /**
     * Entra em uma partida
     */
    joinGame(gameId, role = 'player') {
        this.gameId = gameId;
        this.role = role;
        this.emit('join_game', {
            game_id: gameId,
            role: role
        });
    },
    
    /**
     * Entra como Board (TV/Projetor)
     */
    joinAsBoard(gameId) {
        this.joinGame(gameId, 'board');
    },
    
    /**
     * Entra como Player (Celular)
     */
    joinAsPlayer(gameId) {
        this.joinGame(gameId, 'player');
    },
    
    /**
     * Inicia a partida
     */
    startGame() {
        this.emit('start_game', { game_id: this.gameId });
    },
    
    /**
     * Jogador está pronto - inicia rodada
     */
    playerReady() {
        this.emit('player_ready', { game_id: this.gameId });
    },
    
    /**
     * Vira a carta
     */
    flipCard() {
        this.emit('flip_card', { game_id: this.gameId });
    },
    
    /**
     * Finaliza rodada com acertos
     */
    endRound(guessedWords = []) {
        this.emit('end_round', {
            game_id: this.gameId,
            guessed_words: guessedWords
        });
    },
    
    /**
     * Reseta a partida (nova partida, mantém placar global)
     */
    resetGame() {
        this.emit('reset_game', { game_id: this.gameId });
    },
    
    /**
     * Reseta o placar global
     */
    resetGlobalScore() {
        this.emit('reset_global_score', { game_id: this.gameId });
    }
};