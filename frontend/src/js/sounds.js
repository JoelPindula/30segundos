/**
 * 30 Segundos v3.0 - Gerenciador de Sons
 */

class SoundManager {
    constructor() {
        this.sounds = {};
        this.enabled = true;
        this.volume = 0.5;
        this.initialized = false;
    }
    
    init() {
        if (this.initialized) return;
        
        const soundFiles = {
            'hit': '/sounds/hit.mp3',
            'miss': '/sounds/miss.mp3',
            'tick': '/sounds/tick.mp3',
            'timeout': '/sounds/timeout.mp3',
            'victory': '/sounds/victory.mp3',
            'challenge': '/sounds/challenge.mp3'
        };
        
        for (const [name, path] of Object.entries(soundFiles)) {
            try {
                const audio = new Audio();
                audio.src = path;
                audio.volume = this.volume;
                audio.preload = 'auto';
                this.sounds[name] = audio;
            } catch (e) {
                console.warn(`[Sound] Não foi possível carregar: ${name}`);
            }
        }
        
        this.initialized = true;
    }
    
    play(soundName) {
        if (!this.enabled) return;
        if (!this.initialized) this.init();
        
        const sound = this.sounds[soundName];
        if (sound) {
            try {
                sound.currentTime = 0;
                sound.play().catch(() => {
                    // Ignora erros de autoplay
                });
            } catch (e) {
                // Ignora erros
            }
        }
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        for (const sound of Object.values(this.sounds)) {
            if (sound) sound.volume = this.volume;
        }
    }
    
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
    
    enable() {
        this.enabled = true;
    }
    
    disable() {
        this.enabled = false;
    }
}

// Instância global
window.soundManager = new SoundManager();

// Inicializa no primeiro toque (necessário para mobile)
document.addEventListener('touchstart', () => {
    if (window.soundManager) {
        window.soundManager.init();
    }
}, { once: true });

document.addEventListener('click', () => {
    if (window.soundManager) {
        window.soundManager.init();
    }
}, { once: true });