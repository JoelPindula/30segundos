"""
30 Segundos v3.1 - Serviço de Desafios
"""

import random
from typing import List


class ChallengeService:
    def __init__(self):
        self.challenges: List[str] = [
            "Conte de 1 até 50 em 30 segundos!",
            "Diga 10 países que começam com a letra 'A'",
            "Faça 15 polichinelos em 30 segundos",
            "Diga o alfabeto de trás para frente",
            "Nomeie 10 capitais de países europeus",
            "Diga 15 animais em ordem alfabética",
            "Faça 20 agachamentos em 30 segundos",
            "Diga 10 filmes de ação dos anos 90",
            "Nomeie 12 times de futebol brasileiros",
            "Diga 10 marcas de carros diferentes",
            "Cante o refrão de 3 músicas diferentes",
            "Diga 10 frutas em ordem alfabética",
            "Nomeie 8 presidentes do Brasil",
            "Diga 10 cores em inglês",
            "Faça mímica de 3 profissões para o time adivinhar",
            "Diga 10 verbos no passado em inglês",
            "Nomeie 10 instrumentos musicais",
            "Diga os 12 meses do ano de trás para frente",
            "Nomeie 10 super-heróis da Marvel ou DC",
            "Diga 10 palavras que rimam com 'amor'",
            "Imite 3 animais diferentes (som e gesto)",
            "Diga 10 tipos de comida italiana",
            "Nomeie 8 estados brasileiros e suas capitais",
            "Diga 10 palavras em espanhol",
            "Desenhe algo para o time adivinhar (sem falar)",
            "Diga 10 séries de TV famosas",
            "Nomeie 10 jogadores de futebol famosos",
            "Diga 10 partes do corpo humano em inglês",
            "Cante uma música inteira sem errar a letra",
            "Diga 15 objetos que cabem em uma mochila",
        ]
        self.used_challenges: set = set()

    def get_random_challenge(self) -> str:
        """Retorna um desafio aleatório"""
        available = [
            c for c in self.challenges if c not in self.used_challenges]

        # Se todos foram usados, reseta
        if not available:
            self.used_challenges = set()
            available = self.challenges

        challenge = random.choice(available)
        self.used_challenges.add(challenge)

        return challenge

    def reset(self):
        """Reseta os desafios usados"""
        self.used_challenges = set()


# Instância global
challenge_service = ChallengeService()
