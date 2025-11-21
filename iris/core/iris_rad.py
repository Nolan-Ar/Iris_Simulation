"""
IRIS Economic System - RAD (Registre Automatique Décentralisé)
================================================================

Registre thermodynamique avec composantes sectorielles de D.

Le RAD est le cœur de la régulation IRIS. Il maintient l'équilibre
thermodynamique via le thermomètre θ = D / V_on et ajuste les paramètres
κ (kappa) et η (eta) selon la tension mesurée.

COMPOSANTES DE D (Miroir Thermométrique) - THÉORIE §1.1.3 :
- D_materielle : Biens et immobilisations (actifs physiques)
- D_services : Flux d'entretien et services (maintenance continue)
- D_contractuelle : Titres à promesse productive (NFT financiers)
- D_engagement : Staking et opérations de mise en réserve
- D_regulatrice : Chambre de Relance (redistribution, RU)

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

    COMPOSANTES DE D (THÉORIE §1.1.3):
    - D_materielle : Biens et immobilisations (actifs physiques)
    - D_services : Flux d'entretien et services (maintenance)
    - D_contractuelle : Titres à promesse productive (NFT financiers)
    - D_engagement : Staking et mise en réserve
    - D_regulatrice : Chambre de Relance (redistribution, RU)

    PARAMÈTRES DE RÉGULATION:
    - kappa (κ) : conversion V→U (bornes: [0.5, 2.0])
    - eta (η) : rendement combustion S+U→V (bornes: [0.5, 2.0])
    - delta_m : amortissement mensuel de D (≈ 0.104%/mois ≈ 1.25%/an)
    """

    # === COMPOSANTES DE D (MIROIR THERMOMÉTRIQUE) - THÉORIE §1.1.3 ===
    D_materielle: float = 0.0       # Biens et immobilisations
    D_services: float = 0.0         # Flux d'entretien
    D_contractuelle: float = 0.0    # Titres à promesse productive (NFT financiers)
    D_engagement: float = 0.0       # Staking et mise en réserve
    D_regulatrice: float = 0.0      # Chambre de Relance

    # === PARAMÈTRES DE RÉGULATION ===
    kappa: float = 1.0              # Coefficient conversion V→U
    eta: float = 1.0                # Coefficient rendement combustion S+U→V

    # Bornes de κ (kappa) - THÉORIE §3.1.2: [0.5, 2.0]
    kappa_min: float = 0.5
    kappa_max: float = 2.0

    # Bornes de η (eta) - THÉORIE §3.1.2: [0.5, 2.0]
    eta_min: float = 0.5
    eta_max: float = 2.0

    # === CAPTEURS (SENSORS) - SYSTÈME TRI-CAPTEUR (THÉORIE §3.3.2) ===
    # Stockage des valeurs actuelles des capteurs
    nu_eff: float = 0.20         # Vélocité effective (U_burn+S_burn)/V_on_prev
    tau_eng: float = 0.35        # Taux engagement U_staké/U

    # Cibles des capteurs (THÉORIE §3.3.2)
    nu_target: float = 0.20      # Cible vitesse circulation (20%)
    tau_target: float = 0.35     # Cible taux engagement (35%)

    # === TRACKING DES FLUX (pour calcul des capteurs) ===
    # Ces valeurs doivent être mises à jour à chaque cycle
    U_burn: float = 0.0          # U brûlé pendant le cycle actuel
    S_burn: float = 0.0          # S brûlé pendant le cycle actuel
    U_stake: float = 0.0         # U mis en staking
    U_total: float = 0.0         # U total en circulation
    V_on_previous: float = 0.0   # V_on du cycle précédent

    # Coefficients tri-capteur (THÉORIE §3.3.1)
    # Pour Δη: α_η=0.3, β_η=0.4, γ_η=0.2
    alpha_eta: float = 0.3       # Poids thermomètre dans Δη
    beta_eta: float = 0.4        # Poids vitesse dans Δη
    gamma_eta: float = 0.2       # Poids engagement dans Δη

    # Pour Δκ: α_κ=0.4, β_κ=0.3, γ_κ=0.2
    alpha_kappa: float = 0.4     # Poids vitesse dans Δκ
    beta_kappa: float = 0.3      # Poids engagement dans Δκ
    gamma_kappa: float = 0.2     # Poids thermomètre dans Δκ

    # Contraintes de variation (THÉORIE §3.3.1)
    max_delta_eta: float = 0.15   # |Δη| ≤ 0.15 (15% max par cycle)
    max_delta_kappa: float = 0.15 # |Δκ| ≤ 0.15 (15% max par cycle)

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

        D = D_materielle + D_services + D_contractuelle + D_engagement + D_regulatrice

        D n'est PAS une dette juridique, c'est un indicateur de régulation
        thermodynamique (THÉORIE §1.1.3).
        """
        return (
            self.D_materielle +
            self.D_services +
            self.D_contractuelle +
            self.D_engagement +
            self.D_regulatrice
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

    def add_D_services(self, amount: float) -> None:
        """
        Ajoute de la dette de services (flux d'entretien).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_services")
        self.D_services += amount

    def add_D_engagement(self, amount: float) -> None:
        """
        Ajoute de la dette d'engagement (staking).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_engagement")
        self.D_engagement += amount

    def add_D_regulatrice(self, amount: float) -> None:
        """
        Ajoute de la dette régulatrice (Chambre de Relance).

        Args:
            amount: Montant à ajouter
        """
        validate_non_negative(amount, "D_regulatrice")
        self.D_regulatrice += amount

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

    def calculate_nu_eff(self, U_burn: float, S_burn: float, V_on_prev: float) -> float:
        """
        Calcule ν_eff : vélocité effective de circulation (THÉORIE §3.3.2)

        FORMULE THÉORIQUE :
        ν_eff = (U_burn + S_burn) / V_{t-1}^{on}

        Mesure la vigueur de l'activité économique réelle via les combustions.

        Args:
            U_burn: Montant de U brûlé pendant le cycle
            S_burn: Montant de S brûlé pendant le cycle
            V_on_prev: Valeur vivante du cycle précédent

        Returns:
            Vélocité effective ν_eff
        """
        if V_on_prev > 0:
            nu_eff = (U_burn + S_burn) / V_on_prev
        else:
            nu_eff = 0.0

        self.nu_eff = nu_eff
        return nu_eff

    def calculate_tau_eng(self, U_stake: float, U_total: float) -> float:
        """
        Calcule τ_eng : taux d'engagement (staking) (THÉORIE §3.3.2)

        FORMULE THÉORIQUE :
        τ_eng = U_staké / U

        Mesure la part du RU engagée en staking.

        Args:
            U_stake: Montant de U mis en staking
            U_total: Montant total de U en circulation

        Returns:
            Taux d'engagement τ_eng
        """
        if U_total > 0:
            tau_eng = U_stake / U_total
        else:
            tau_eng = 0.0

        self.tau_eng = tau_eng
        return tau_eng

    def compute_delta_eta(self, r_t: float, nu_eff: float, tau_eng: float) -> float:
        """
        Calcule la VARIATION Δη selon le système tri-capteur (THÉORIE §3.3.1).

        FORMULE THÉORIQUE (Iris_proto_complet.md §3.3.1):
        Δη_t = +α_η × (1 - r_{t-1}) + β_η × (ν_target - ν_{t-1}) - γ_η × (τ_eng - τ_target)

        TROIS CAPTEURS:
        1. r_t = θ = D/V_on (thermomètre, cible=1)
        2. ν_eff = (U_burn+S_burn)/V_on (vitesse circulation, cible=0.20)
        3. τ_eng = U_staké/U (taux engagement, cible=0.35)

        PRINCIPE:
        - η augmente si: r < 1 (sous-investissement) OU ν < cible (léthargie)
        - η diminue si: τ_eng > cible (sacrifice excessif du présent)

        COEFFICIENTS (§3.3.1):
        - α_η = 0.3 (thermomètre, poids modéré)
        - β_η = 0.4 (vitesse, poids le plus fort car mesure activité réelle)
        - γ_η = 0.2 (engagement, poids faible car indicateur social secondaire)

        Args:
            r_t: Thermomètre actuel θ = D/V_on
            nu_eff: Vitesse de circulation actuelle
            tau_eng: Taux d'engagement actuel

        Returns:
            Δη (variation de eta, bornée dans [-0.15, +0.15])
        """
        # Contributions des trois capteurs
        contrib_thermo = self.alpha_eta * (1.0 - r_t)  # + si r < 1 (sous-investissement)
        contrib_vitesse = self.beta_eta * (self.nu_target - nu_eff)  # + si ν < cible (léthargie)
        contrib_engagement = -self.gamma_eta * (tau_eng - self.tau_target)  # - si τ > cible (sacrifice)

        # Somme pondérée
        delta_eta = contrib_thermo + contrib_vitesse + contrib_engagement

        # Contrainte de variation maximale: |Δη| ≤ 0.15 (THÉORIE §3.3.1)
        delta_eta = np.clip(delta_eta, -self.max_delta_eta, self.max_delta_eta)

        return float(delta_eta)

    def compute_delta_kappa(self, r_t: float, nu_eff: float, tau_eng: float) -> float:
        """
        Calcule la VARIATION Δκ selon le système tri-capteur (THÉORIE §3.3.1).

        FORMULE THÉORIQUE (Iris_proto_complet.md §3.3.1):
        Δκ_t = +α_κ × (ν_target - ν_{t-1}) - β_κ × (τ_eng - τ_target) + γ_κ × (1 - r_{t-1})

        PRINCIPE:
        - κ augmente si: ν < cible (besoin liquidité pour ranimer) OU r < 1 (sous-régime)
        - κ diminue si: τ_eng > cible (protéger pouvoir d'achat présent) OU r > 1 (surchauffe)

        COEFFICIENTS (§3.3.1):
        - α_κ = 0.4 (vitesse, poids le plus fort car κ répond prioritairement à la circulation)
        - β_κ = 0.3 (engagement, poids modéré pour protection sociale)
        - γ_κ = 0.2 (thermomètre, poids faible)

        Args:
            r_t: Thermomètre actuel θ = D/V_on
            nu_eff: Vitesse de circulation actuelle
            tau_eng: Taux d'engagement actuel

        Returns:
            Δκ (variation de kappa, bornée dans [-0.15, +0.15])
        """
        # Contributions des trois capteurs
        contrib_vitesse = self.alpha_kappa * (self.nu_target - nu_eff)  # + si ν < cible
        contrib_engagement = -self.beta_kappa * (tau_eng - self.tau_target)  # - si τ > cible
        contrib_thermo = self.gamma_kappa * (1.0 - r_t)  # + si r < 1

        # Somme pondérée
        delta_kappa = contrib_vitesse + contrib_engagement + contrib_thermo

        # Contrainte de variation maximale: |Δκ| ≤ 0.15 (THÉORIE §3.3.1)
        delta_kappa = np.clip(delta_kappa, -self.max_delta_kappa, self.max_delta_kappa)

        return float(delta_kappa)

    def update_kappa(self, r_t: float, nu_eff: float, tau_eng: float) -> None:
        """
        Met à jour κ (kappa) avec système tri-capteur (CORRECTION A).

        CHANGEMENT MAJEUR: Utilise compute_delta_kappa() qui prend 3 capteurs
        au lieu de l'ancien système mono-capteur basé uniquement sur θ.

        Args:
            r_t: Thermomètre actuel θ = D/V_on
            nu_eff: Vitesse de circulation actuelle
            tau_eng: Taux d'engagement actuel
        """
        # Calcul de la variation Δκ (tri-capteur)
        delta_kappa = self.compute_delta_kappa(r_t, nu_eff, tau_eng)

        # Application de la variation
        self.kappa += delta_kappa

        # Application des bornes strictes [0.7, 1.3]
        self.kappa = float(np.clip(self.kappa, self.kappa_min, self.kappa_max))

        # Enregistrement historique
        self.kappa_history.append(self.kappa)
        if len(self.kappa_history) > 100:
            self.kappa_history.pop(0)

    def update_eta(self, r_t: float, nu_eff: float, tau_eng: float) -> None:
        """
        Met à jour η (eta) avec système tri-capteur (CORRECTION A).

        CHANGEMENT MAJEUR: Utilise compute_delta_eta() qui prend 3 capteurs
        au lieu de l'ancien système mono-capteur basé uniquement sur θ.

        Args:
            r_t: Thermomètre actuel θ = D/V_on
            nu_eff: Vitesse de circulation actuelle
            tau_eng: Taux d'engagement actuel
        """
        # Calcul de la variation Δη (tri-capteur)
        delta_eta = self.compute_delta_eta(r_t, nu_eff, tau_eng)

        # Application de la variation
        self.eta += delta_eta

        # Application des bornes strictes [0.7, 1.3]
        self.eta = float(np.clip(self.eta, self.eta_min, self.eta_max))

        # Enregistrement historique
        self.eta_history.append(self.eta)
        if len(self.eta_history) > 100:
            self.eta_history.pop(0)

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
        self.D_services *= ratio
        self.D_contractuelle *= ratio
        self.D_engagement *= ratio
        self.D_regulatrice *= ratio

        logger.debug(f"Amortized D: {amort:.2f} ({delta*100:.4f}% of {total_D_before:.2f})")

        return amort

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du RAD."""
        total_D = self.total_D()

        return {
            "total_D": total_D,
            "D_materielle": self.D_materielle,
            "D_services": self.D_services,
            "D_contractuelle": self.D_contractuelle,
            "D_engagement": self.D_engagement,
            "D_regulatrice": self.D_regulatrice,
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
