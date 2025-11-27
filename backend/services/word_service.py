"""
30 Segundos v3.1 - Serviço de Palavras
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional


class WordService:
    def __init__(self):
        self.word_banks: Dict[str, List[dict]] = {}
        self.used_words: Dict[str, set] = {}
        self.load_word_banks()

    def load_word_banks(self):
        """Carrega todos os bancos de palavras"""
        # Tenta múltiplos caminhos possíveis
        possible_paths = [
            Path(__file__).parent.parent.parent / 'data' / 'word_banks',
            Path(__file__).parent.parent / 'data' / 'word_banks',
            Path('data') / 'word_banks',
        ]

        data_path = None
        for path in possible_paths:
            if path.exists():
                data_path = path
                break

        if not data_path:
            print(
                f"[WordService] Pasta de dados não encontrada, criando banco padrão")
            self._create_default_bank()
            return

        # Carrega cada arquivo JSON
        for file_path in data_path.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    theme_id = file_path.stem

                    # Suporta diferentes formatos de arquivo
                    if isinstance(data, dict) and 'words' in data:
                        words = data['words']
                    elif isinstance(data, list):
                        words = data
                    else:
                        words = []

                    # Normaliza formato das palavras
                    normalized_words = []
                    for item in words:
                        if isinstance(item, str):
                            normalized_words.append({"word": item, "level": 1})
                        elif isinstance(item, dict):
                            word = item.get('word') or item.get(
                                'texto') or item.get('name', '')
                            level = item.get('level') or item.get(
                                'nivel') or item.get('difficulty', 1)
                            if word:
                                normalized_words.append(
                                    {"word": word, "level": int(level)})

                    if normalized_words:
                        self.word_banks[theme_id] = normalized_words
                        print(
                            f"[WordService] Carregado: {theme_id} ({len(normalized_words)} palavras)")

            except Exception as e:
                print(f"[WordService] Erro ao carregar {file_path}: {e}")

        if not self.word_banks:
            self._create_default_bank()

    def _create_default_bank(self):
        """Cria banco padrão se não houver arquivos"""
        self.word_banks['geral'] = [
            {"word": "Casa", "level": 1},
            {"word": "Carro", "level": 1},
            {"word": "Cachorro", "level": 1},
            {"word": "Gato", "level": 1},
            {"word": "Árvore", "level": 1},
            {"word": "Computador", "level": 2},
            {"word": "Telefone", "level": 2},
            {"word": "Televisão", "level": 2},
            {"word": "Geladeira", "level": 2},
            {"word": "Bicicleta", "level": 2},
            {"word": "Fotografia", "level": 3},
            {"word": "Democracia", "level": 3},
            {"word": "Filosofia", "level": 3},
            {"word": "Astronomia", "level": 3},
            {"word": "Arqueologia", "level": 3},
            {"word": "Felicidade", "level": 1},
            {"word": "Amizade", "level": 1},
            {"word": "Futebol", "level": 1},
            {"word": "Praia", "level": 1},
            {"word": "Montanha", "level": 1},
            {"word": "Hospital", "level": 2},
            {"word": "Aeroporto", "level": 2},
            {"word": "Restaurante", "level": 2},
            {"word": "Supermercado", "level": 2},
            {"word": "Biblioteca", "level": 2},
        ]
        print("[WordService] Banco padrão criado com 25 palavras")

    def get_available_themes(self) -> List[dict]:
        """Retorna lista de temas disponíveis"""
        themes = []
        for theme_id, words in self.word_banks.items():
            # Não incluir desafios como tema de palavras
            if theme_id.lower() == 'desafios':
                continue

            themes.append({
                "id": theme_id,
                "name": self._format_theme_name(theme_id),
                "word_count": len(words)
            })

        # Ordena por nome
        themes.sort(key=lambda x: x['name'])
        return themes

    def _format_theme_name(self, theme_id: str) -> str:
        """Formata o nome do tema para exibição"""
        # Mapeamento de nomes especiais
        name_map = {
            'geral': 'Geral',
            'biblia_completa': 'Bíblia',
            'cinema': 'Cinema & Filmes',
            'desenhos_animes': 'Desenhos & Animes',
            'esporte': 'Esportes',
            'geografia': 'Geografia',
            'geracaZ': 'Geração Z',
            'jogos': 'Jogos & Games',
            'musica': 'Música',
            'QI_elevado': 'QI Elevado (Difícil)',
        }

        if theme_id in name_map:
            return name_map[theme_id]

        # Formata automaticamente
        return theme_id.replace('_', ' ').title()

    def get_available_levels(self) -> List[dict]:
        """Retorna níveis de dificuldade"""
        return [
            {"level": 1, "name": "Fácil", "color": "#2ecc71"},
            {"level": 2, "name": "Médio", "color": "#f39c12"},
            {"level": 3, "name": "Difícil", "color": "#e74c3c"},
            {"level": 4, "name": "Muito Difícil", "color": "#9b59b6"},
            {"level": 5, "name": "Impossível", "color": "#1a1a2e"},
        ]

    def init_game_pool(self, game_id: str):
        """Inicializa pool de palavras usadas para um jogo"""
        self.used_words[game_id] = set()

    def clear_game_pool(self, game_id: str):
        """Limpa pool quando o jogo termina"""
        if game_id in self.used_words:
            del self.used_words[game_id]

    def get_card_words(
        self,
        game_id: str,
        themes: List[str],
        levels: List[int],
        words_per_side: int = 5,
        bonus_chance: float = 0.15,
        cursed_chance: float = 0.10
    ) -> Optional[dict]:
        """
        Gera uma carta com palavras para os dois lados
        """

        # Inicializa pool se não existir
        if game_id not in self.used_words:
            self.used_words[game_id] = set()

        # Coleta palavras disponíveis
        available_words = []
        for theme in themes:
            if theme in self.word_banks:
                for word_data in self.word_banks[theme]:
                    word = word_data.get('word', '')
                    level = word_data.get('level', 1)

                    if level in levels and word not in self.used_words[game_id]:
                        available_words.append({
                            "text": word,
                            "level": level
                        })

        # Se não tem palavras suficientes, reseta o pool
        total_needed = words_per_side * 2
        if len(available_words) < total_needed:
            print(
                f"[WordService] Resetando pool de palavras para jogo {game_id}")
            self.used_words[game_id] = set()

            # Recoleta
            available_words = []
            for theme in themes:
                if theme in self.word_banks:
                    for word_data in self.word_banks[theme]:
                        word = word_data.get('word', '')
                        level = word_data.get('level', 1)
                        if level in levels:
                            available_words.append({
                                "text": word,
                                "level": level
                            })

        if len(available_words) < total_needed:
            print(
                f"[WordService] Palavras insuficientes: {len(available_words)} < {total_needed}")
            return None

        # Embaralha e seleciona
        random.shuffle(available_words)
        selected = available_words[:total_needed]

        # Marca como usadas
        for word in selected:
            self.used_words[game_id].add(word["text"])

        # Divide entre amarelo e azul
        yellow_words = selected[:words_per_side]
        blue_words = selected[words_per_side:]

        # Aplica bônus e maldição
        yellow_words = self._apply_special_words(
            yellow_words, bonus_chance, cursed_chance)
        blue_words = self._apply_special_words(
            blue_words, bonus_chance, cursed_chance)

        return {
            "yellow_words": yellow_words,
            "blue_words": blue_words
        }

    def _apply_special_words(
        self,
        words: List[dict],
        bonus_chance: float,
        cursed_chance: float
    ) -> List[dict]:
        """Aplica palavras bônus e malditas"""
        result = []
        has_bonus = False
        has_cursed = False

        for word in words:
            word_data = {
                "text": word["text"],
                "level": word["level"],
                "is_bonus": False,
                "is_cursed": False
            }

            # Tenta aplicar bônus (máximo 1 por lado)
            if not has_bonus and random.random() < bonus_chance:
                word_data["is_bonus"] = True
                has_bonus = True
            # Tenta aplicar maldição (máximo 1 por lado)
            elif not has_cursed and random.random() < cursed_chance:
                word_data["is_cursed"] = True
                has_cursed = True

            result.append(word_data)

        return result


# Instância global
word_service = WordService()
