"""
IRIS v2.1 - Mécanisme de Prix Explicites (Log-Prices)
======================================================

Module de gestion des prix explicites dans le système IRIS utilisant
des log-prices pour garantir la stabilité numérique.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Principes :
-----------
1. LOG-PRICES : Prix stockés en log pour éviter overflow/underflow
2. DRIFT THERMOMÉTRIQUE : θ influence les prix
3. BRUIT BORNÉ : Variations aléatoires contrôlées
4. SÉCURITÉ : Pas de NaN, Inf ou prix ≤ 0

Formule clé :
------------
log(P_t) = log(P_{t-1}) + drift + noise + shock

où :
- drift = α × (θ - 1.0)  # tendance liée au thermomètre
- noise = random ∈ [-β, +β]  # variation aléatoire bornée
- shock = choc externe (catastrophe, etc.)

Prix physique :
P_t = max(ε, exp(log(P_t)))
"""

import numpy as np
import math
from typing import Dict, Optional
from enum import Enum


class GoodType(Enum):
    """Types de biens dans l'économie"""
    ALIMENTATION = "alimentation"
    LOGEMENT = "logement"
    TRANSPORT = "transport"
    ENERGIE = "energie"
    SERVICES = "services"
    BIENS_DURABLES = "biens_durables"
    CULTURE = "culture"
    AUTRE = "autre"


class PriceManager:
    """
    Gestionnaire de prix pour l'économie IRIS

    Utilise des log-prices pour la stabilité numérique :
    - Stockage : log(P) au lieu de P
    - Mise à jour : log(P_new) = log(P_old) + delta
    - Extraction : P = max(epsilon, exp(log(P)))

    API minimale :
    - register_good(good_id, initial_price, weight) : enregistrer un bien
    - step(signals) : mettre à jour les prix selon θ, chocs, etc.
    - get_price(good_id) : obtenir le prix physique d'un bien
    - mean_price() : prix moyen pondéré
    - inflation(prev_mean_price) : taux d'inflation
    """

    def __init__(self, epsilon: float = 1e-6, max_step_change: float = 0.05):
        """
        Initialise le gestionnaire de prix

        Args:
            epsilon: Valeur minimale pour éviter prix ≤ 0
            max_step_change: Variation maximale de log(P) par step (5% par défaut)
        """
        self.epsilon = epsilon
        self.max_step_change = max_step_change

        # Stockage en log-prices
        self.log_prices: Dict[str, float] = {}  # good_id -> log(P)

        # Poids pour prix moyen pondéré
        self.weights: Dict[str, float] = {}  # good_id -> poids

        # Historique (optionnel)
        self.history_log_prices: Dict[str, list] = {}
        self.history_mean_price: list = []
        self.history_inflation: list = []

    def _normalize_good_id(self, good_id) -> str:
        """
        Normalise un identifiant de bien (accepte GoodType ou str)

        Args:
            good_id: Identifiant brut (GoodType, str, ou autre)

        Returns:
            Identifiant normalisé en str
        """
        if isinstance(good_id, GoodType):
            return good_id.value
        return str(good_id)

    def register_good(self, good_id, initial_price: float, weight: float = 1.0):
        """
        Enregistre un bien avec son prix initial

        Args:
            good_id: Identifiant du bien (str ou GoodType, ex: "food", GoodType.ALIMENTATION)
            initial_price: Prix initial (en U, monnaie d'usage)
            weight: Poids dans le calcul du prix moyen (défaut: 1.0)
        """
        # Normalise l'identifiant (accepte GoodType ou str)
        gid = self._normalize_good_id(good_id)

        # Sécurité : prix initial > 0
        price_safe = max(initial_price, self.epsilon)

        # Stockage en log
        self.log_prices[gid] = np.log(price_safe)
        self.weights[gid] = weight

        # Initialise historique
        self.history_log_prices[gid] = [self.log_prices[gid]]

    def step(self, signals: dict) -> None:
        """
        Met à jour les prix en fonction des signaux économiques

        Args:
            signals: Dictionnaire de signaux :
                - 'theta' (float) : thermomètre θ = D/V_on (défaut: 1.0)
                - 'shock' (float) : choc externe (catastrophe, etc.) (défaut: 0.0)
                - 'noise_amplitude' (float) : amplitude du bruit (défaut: 0.01)
                - 'drift_coeff' (float) : coefficient drift lié à θ (défaut: 0.02)
        """
        # Extraction des signaux
        theta = signals.get("theta", 1.0)
        shock = signals.get("shock", 0.0)
        noise_amplitude = signals.get("noise_amplitude", 0.01)
        drift_coeff = signals.get("drift_coeff", 0.02)

        # Sécurité : theta valide
        if not (0.01 <= theta <= 100.0):
            theta = 1.0  # fallback sécurisé

        for gid, logP in self.log_prices.items():
            # Drift lié au thermomètre θ
            # Si θ > 1 → tendance inflation
            # Si θ < 1 → tendance déflation
            drift = drift_coeff * (theta - 1.0)

            # Bruit borné (variation aléatoire)
            noise = np.random.uniform(-noise_amplitude, noise_amplitude)

            # Choc externe
            # (ex: catastrophe → shock < 0, relance → shock > 0)

            # Variation totale
            delta = drift + noise + shock

            # Borne la variation pour stabilité
            delta = np.clip(delta, -self.max_step_change, self.max_step_change)

            # Mise à jour du log-price
            new_logP = logP + delta
            self.log_prices[gid] = new_logP

            # Historique (optionnel, limite à 100 valeurs)
            self.history_log_prices[gid].append(new_logP)
            if len(self.history_log_prices[gid]) > 100:
                self.history_log_prices[gid].pop(0)

    def get_price(self, good_id) -> float:
        """
        Retourne le prix physique d'un bien

        Args:
            good_id: Identifiant du bien (str ou GoodType)

        Returns:
            Prix en U (monnaie d'usage), garanti > epsilon
        """
        # Normalise l'identifiant (accepte GoodType ou str)
        gid = self._normalize_good_id(good_id)

        if gid not in self.log_prices:
            return self.epsilon

        logP = self.log_prices[gid]

        # Conversion log → prix physique
        # Sécurité : borne à ±100 pour éviter overflow
        logP_safe = np.clip(logP, -100, 100)
        price = float(np.exp(logP_safe))

        # Sécurité : prix minimum
        return max(self.epsilon, price)

    def get_prix(self, good_id) -> float:
        """
        Alias de get_price() pour compatibilité

        Args:
            good_id: Identifiant du bien (str ou GoodType)

        Returns:
            Prix en U (monnaie d'usage), garanti > epsilon
        """
        return self.get_price(good_id)

    def mean_price(self) -> float:
        """
        Calcule le prix moyen pondéré de tous les biens

        Returns:
            Prix moyen (moyenne pondérée)
        """
        if not self.log_prices:
            return 1.0

        numerator = 0.0
        denominator = 0.0

        for gid, logP in self.log_prices.items():
            w = self.weights.get(gid, 1.0)
            p = self.get_price(gid)

            numerator += w * p
            denominator += w

        if denominator <= 0:
            return 1.0

        mean = numerator / denominator

        # Historique
        self.history_mean_price.append(mean)
        if len(self.history_mean_price) > 100:
            self.history_mean_price.pop(0)

        return mean

    def inflation(self, prev_mean_price: float) -> float:
        """
        Calcule le taux d'inflation depuis le prix moyen précédent

        Args:
            prev_mean_price: Prix moyen au cycle précédent

        Returns:
            Taux d'inflation (0.02 = 2% d'inflation)
        """
        current = self.mean_price()

        if prev_mean_price <= 0:
            return 0.0

        infl = (current - prev_mean_price) / prev_mean_price

        # Historique
        self.history_inflation.append(infl)
        if len(self.history_inflation) > 100:
            self.history_inflation.pop(0)

        return infl

    def get_statistics(self) -> dict:
        """
        Retourne des statistiques sur les prix

        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'nb_goods': len(self.log_prices),
            'mean_price': self.mean_price(),
            'prices': {}
        }

        for gid in self.log_prices.keys():
            stats['prices'][gid] = self.get_price(gid)

        if self.history_mean_price:
            stats['mean_price_history_length'] = len(self.history_mean_price)

        if self.history_inflation:
            stats['latest_inflation'] = self.history_inflation[-1] if self.history_inflation else 0.0
            stats['avg_inflation'] = np.mean(self.history_inflation) if self.history_inflation else 0.0

        return stats

    def validate(self) -> tuple[bool, list]:
        """
        Valide l'état du gestionnaire de prix

        Returns:
            (is_valid, errors) : (True si valide, liste des erreurs)
        """
        errors = []

        for gid, logP in self.log_prices.items():
            # Vérif NaN/Inf
            if math.isnan(logP) or math.isinf(logP):
                errors.append(f"Prix invalide pour {gid}: log(P)={logP}")

            # Vérif prix physique > 0
            p = self.get_price(gid)
            if p <= 0:
                errors.append(f"Prix négatif/nul pour {gid}: P={p}")

        # Vérif prix moyen
        mean = self.mean_price()
        if math.isnan(mean) or math.isinf(mean) or mean <= 0:
            errors.append(f"Prix moyen invalide: {mean}")

        return (len(errors) == 0, errors)
