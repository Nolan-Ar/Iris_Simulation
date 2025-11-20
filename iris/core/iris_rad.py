"""
IRIS Economic System - RAD (Registre Automatique Décentralisé)
================================================================

Registre thermodynamique avec composantes sectorielles de D.

Le RAD est le cœur de la régulation IRIS. Il maintient l'équilibre
thermodynamique via le thermomètre θ = D / V_on et ajuste les paramètres
κ (kappa) et η (eta) selon la tension mesurée.

COMPOSANTES DE D (Miroir Thermométrique):
- D_materielle : Cristallisation (conversions U→V, actifs immobilisés)
- D_contractuelle : NFT financiers (titres productifs entreprises)
- D_consommation : Consommation démographique (D générée par la vie)
- D_catastrophes : Destructions de valeur (événements catastrophiques)

RÉGULATION:
- θ = D / V_on (thermomètre économique)
- κ (kappa) : régule conversion V→U (contracyclique)
- η (eta) : régule combustion S+U→V (contracyclique)

GARANTIES:
- Pas de reset silencieux
- Conservation des flux
- Amortissement conforme théorie IRIS (δ_m ≈ 1.25%/an)

Auteur: Arnault Nolan
Date: 2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import logging
import numpy as np

from iris.utils import safe_divide, validate_non_negative

logger = logging.getLogger(__name__)


@dataclass
class RADState:
    """
    État du Régulateur Automatique Décentralisé (RAD).

    Le RAD maintient l'équilibre thermodynamique du système IRIS via:
    1. Suivi des composantes sectorielles de D (miroir thermométrique)
    2. Calcul du thermomètre θ = D / V_on
    3. Ajustement des paramètres κ (kappa) et η (eta)

    COMPOSANTES DE D:
    - D_materielle : Actifs immobilisés (conversions U→V, cristallisation)
    - D_contractuelle : Titres productifs (NFT financiers entreprises)
    - D_consommation : Consommation démographique (vie des agents)
    - D_catastrophes : Destructions de valeur (catastrophes)

    PARAMÈTRES DE RÉGULATION:
    - kappa (κ) : conversion V→U (bornes: [0.5, 2.0])
    - eta (η) : rendement combustion S+U→V (bornes: [0.5, 2.0])
    - delta_m : amortissement mensuel de D (≈ 0.104%/mois ≈ 1.25%/an)
    """

    # === COMPOSANTES DE D (MIROIR THERMOMÉTRIQUE) ===
    D_materielle: float = 0.0       # Cristallisation (U→V)
    D_contractuelle: float = 0.0    # NFT financiers
    D_consommation: float = 0.0     # Consommation démographique
    D_catastrophes: float = 0.0     # Destructions de valeur

    # === PARAMÈTRES DE RÉGULATION ===
    kappa: float = 1.0              # Coefficient conversion V→U
    eta: float = 1.0                # Coefficient rendement combustion S+U→V

    # Bornes de κ (kappa)
    kappa_min: float = 0.5
    kappa_max: float = 2.0
    kappa_beta: float = 0.5         # Sensibilité à l'indicateur I
    kappa_smoothing: float = 0.1    # Lissage temporel

    # Bornes de η (eta)
    eta_min: float = 0.5
    eta_max: float = 2.0
    eta_alpha: float = 0.5          # Sensibilité à l'indicateur I
    eta_smoothing: float = 0.15     # Lissage temporel

    # Amortissement de D
    delta_m: float = 0.001041666    # Amortissement mensuel ≈ 0.104%/mois ≈ 1.25%/an
    delta_m_annual: float = 0.0125  # Amortissement annuel ≈ 1.25%/an

    # Historique pour calculs et lissage
    theta_history: List[float] = field(default_factory=list)
    kappa_history: List[float] = field(default_factory=list)
    eta_history: List[float] = field(default_factory=list)

    def total_D(self) -> float:
        """
        Calcule la dette thermométrique totale D.

        D = D_materielle + D_contractuelle + D_consommation + D_catastrophes

        D n'est PAS une dette juridique, c'est un indicateur de régulation.
        """
        return (
            self.D_materielle +
            self.D_contractuelle +
            self.D_consommation +
            self.D_catastrophes
        )

    def add_D_materielle(self, amount: float) -> None:
        """
        Ajoute de la dette matérielle (cristallisation U→V).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_materielle")
        self.D_materielle += amount

    def add_D_contractuelle(self, amount: float) -> None:
        """
        Ajoute de la dette contractuelle (NFT financiers).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_contractuelle")
        self.D_contractuelle += amount

    def add_D_consommation(self, amount: float) -> None:
        """
        Ajoute de la dette de consommation (démographie).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_consommation")
        self.D_consommation += amount

    def add_D_catastrophes(self, amount: float) -> None:
        """
        Ajoute de la dette de catastrophes (destructions).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_catastrophes")
        self.D_catastrophes += amount

    def compute_thermometer(self, V_on: float) -> float:
        """
        Calcule le thermomètre θ = D / V_on.

        Le thermomètre mesure la tension économique:
        - θ < 1 : sous-régime (manque de demande)
        - θ = 1 : équilibre
        - θ > 1 : surchauffe (excès de demande)

        Args:
            V_on: Valeur vivante en circulation

        Returns:
            Thermomètre θ
        """
        total_D = self.total_D()
        theta = safe_divide(total_D, V_on, default=1.0)

        # Enregistre dans l'historique
        self.theta_history.append(theta)
        if len(self.theta_history) > 100:
            self.theta_history.pop(0)

        return theta

    def compute_kappa_target(self, indicator: float) -> float:
        """
        Calcule la valeur cible de κ (kappa) selon l'indicateur I = θ - 1.

        PRINCIPE CONTRACYCLIQUE:
        - I > 0 (θ > 1, surchauffe) → κ < 1 → freine conversion V→U
        - I < 0 (θ < 1, sous-régime) → κ > 1 → stimule conversion V→U
        - I = 0 (θ = 1, équilibre) → κ = 1 → neutre

        Formule linéaire : κ = 1.0 - β × I

        Args:
            indicator: Indicateur centré I = θ - 1

        Returns:
            Valeur cible de κ (bornée dans [kappa_min, kappa_max])
        """
        kappa_raw = 1.0 - self.kappa_beta * indicator
        kappa_target = np.clip(kappa_raw, self.kappa_min, self.kappa_max)
        return float(kappa_target)

    def compute_eta_target(self, indicator: float) -> float:
        """
        Calcule la valeur cible de η (eta) selon l'indicateur I = θ - 1.

        PRINCIPE CONTRACYCLIQUE:
        - I > 0 (θ > 1, surchauffe) → η < 1 → freine combustion/production
        - I < 0 (θ < 1, sous-régime) → η > 1 → stimule combustion/production
        - I = 0 (θ = 1, équilibre) → η = 1 → neutre

        Formule linéaire : η = 1.0 - α × I

        Args:
            indicator: Indicateur centré I = θ - 1

        Returns:
            Valeur cible de η (bornée dans [eta_min, eta_max])
        """
        eta_raw = 1.0 - self.eta_alpha * indicator
        eta_target = np.clip(eta_raw, self.eta_min, self.eta_max)
        return float(eta_target)

    def update_kappa(self, thermometer: float, target: float = 1.0) -> None:
        """
        Met à jour κ (kappa) avec lissage temporel.

        Applique un lissage exponentiel (EMA) pour éviter les oscillations:
        κ(t+1) = (1 - α) × κ(t) + α × κ_target

        Args:
            thermometer: Thermomètre actuel θ
            target: Cible du thermomètre (défaut: 1.0)
        """
        # Calcul de l'indicateur centré
        indicator = thermometer - target

        # Calcul de la cible
        kappa_target = self.compute_kappa_target(indicator)

        # Lissage temporel
        smoothing = self.kappa_smoothing
        self.kappa = (1.0 - smoothing) * self.kappa + smoothing * kappa_target

        # Enregistrement historique
        self.kappa_history.append(self.kappa)
        if len(self.kappa_history) > 100:
            self.kappa_history.pop(0)

        # Application des bornes (sécurité)
        self.kappa = float(np.clip(self.kappa, self.kappa_min, self.kappa_max))

    def update_eta(self, thermometer: float, target: float = 1.0) -> None:
        """
        Met à jour η (eta) avec lissage temporel.

        Applique un lissage exponentiel (EMA) pour éviter les oscillations:
        η(t+1) = (1 - α) × η(t) + α × η_target

        Args:
            thermometer: Thermomètre actuel θ
            target: Cible du thermomètre (défaut: 1.0)
        """
        # Calcul de l'indicateur centré
        indicator = thermometer - target

        # Calcul de la cible
        eta_target = self.compute_eta_target(indicator)

        # Lissage temporel
        smoothing = self.eta_smoothing
        self.eta = (1.0 - smoothing) * self.eta + smoothing * eta_target

        # Enregistrement historique
        self.eta_history.append(self.eta)
        if len(self.eta_history) > 100:
            self.eta_history.pop(0)

        # Application des bornes (sécurité)
        self.eta = float(np.clip(self.eta, self.eta_min, self.eta_max))

    def apply_amortization(self, time_scale: str = "months") -> float:
        """
        Applique l'amortissement global de D selon la théorie IRIS.

        Document IRIS impose : δ_m ≈ 0.104%/mois ≈ 1.25%/an

        ÉCHELLE TEMPORELLE : 1 step = 1 mois
        L'amortissement mensuel est appliqué à chaque appel (δ_m = 0.104%/mois).

        L'amortissement est appliqué proportionnellement sur toutes les
        composantes de D pour maintenir leur ratio relatif.

        Args:
            time_scale: DEPRECATED - Toujours "months" (1 step = 1 mois)

        Returns:
            Montant total amorti
        """
        total_D_before = self.total_D()

        if total_D_before < 1e-6:
            return 0.0

        # Amortissement mensuel : δ_m ≈ 0.104%/mois
        delta = self.delta_m

        # Calcul de l'amortissement
        amort = delta * total_D_before
        ratio = (total_D_before - amort) / total_D_before

        # Application proportionnelle sur toutes les composantes
        self.D_materielle *= ratio
        self.D_contractuelle *= ratio
        self.D_consommation *= ratio
        self.D_catastrophes *= ratio

        logger.debug(f"Amortized D: {amort:.2f} ({delta*100:.4f}% of {total_D_before:.2f})")

        return amort

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du RAD."""
        total_D = self.total_D()

        return {
            "total_D": total_D,
            "D_materielle": self.D_materielle,
            "D_contractuelle": self.D_contractuelle,
            "D_consommation": self.D_consommation,
            "D_catastrophes": self.D_catastrophes,
            "kappa": self.kappa,
            "eta": self.eta,
            "theta_mean": float(np.mean(self.theta_history)) if self.theta_history else 1.0,
            "theta_std": float(np.std(self.theta_history)) if len(self.theta_history) > 1 else 0.0,
        }

    def __repr__(self) -> str:
        return (
            f"RADState(D_total={self.total_D():.2f}, "
            f"κ={self.kappa:.3f}, η={self.eta:.3f})"
        )
