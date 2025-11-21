"""
IRIS Economic System - Core Model
==================================

Modèle du système économique IRIS (Integrative Resilience Intelligence System)
basé sur la preuve d'acte plutôt que la promesse de remboursement.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

═══════════════════════════════════════════════════════════════════════════════
ÉCHELLE DE TEMPS : 1 step = 1 mois
═══════════════════════════════════════════════════════════════════════════════

CONVENTION TEMPORELLE :
- 1 step de simulation = 1 mois calendaire
- STEPS_PER_YEAR = 12 (constante globale)
- Toutes les fréquences sont exprimées en mois (steps)

FRÉQUENCES DES MÉCANISMES :
- Revenu Universel (RU) : distribué tous les 12 steps (1 fois/an)
- Démographie (naissances/décès/vieillissement) : mise à jour tous les 12 steps (1 fois/an)
- Combustion entreprises : tous les 1 step (1 fois/mois) - production continue
- Chambre de Relance (redistribution pool) : tous les 12 steps (1 fois/an)
- Régulation RAD C2 (profonde) : tous les 12 steps (T_period = 12)
- Calibration automatique : tous les 50 steps (≈ 4 ans)
- Catastrophes : probabilité annuelle (déclenchement potentiel chaque step)
- Amortissement D : δ_m = 0.104%/mois appliqué à chaque step

EXEMPLE D'UTILISATION :
  economy = IRISEconomy(initial_agents=100)
  economy.simulate(steps=120)  # Simule 120 mois = 10 ans

═══════════════════════════════════════════════════════════════════════════════
MAPPING THÉORIE ↔ CODE : VARIABLES, CAPTEURS ET PARAMÈTRES
═══════════════════════════════════════════════════════════════════════════════

VARIABLES D'ÉTAT MACRO
─────────────────────────────────────────────────────────────────────────────
Symbole   │ Signification                        │ Variable Code
──────────┼──────────────────────────────────────┼──────────────────────────────
V         │ Verum (patrimoine ancré)             │ Agent.V_balance
U         │ Usage (liquidité, monnaie transaction)│ Agent.U_balance
S         │ Service/Travail (combustion)         │ Paramètre implicite
V_on      │ Valeur vivante en circulation        │ get_V_on()
D         │ Dette thermométrique totale          │ RADState.total_D()
D_mat     │ Composante matérielle de D           │ RADState.D_materielle
D_contr   │ Composante contractuelle de D (NFT)  │ RADState.D_contractuelle
D_conso   │ Composante consommation de D         │ RADState.D_consommation (iris_rad.py)
D_cata    │ Composante catastrophes de D         │ RADState.D_catastrophes (iris_rad.py)
D_serv    │ Composante services de D             │ RADState.D_services
D_eng     │ Composante engagement de D (staking) │ RADState.D_engagement
D_reg     │ Composante régulatrice de D (CR)     │ RADState.D_regulatrice

THERMOMÈTRE ET INDICATEURS DE RÉGULATION
─────────────────────────────────────────────────────────────────────────────
Symbole   │ Signification                        │ Variable Code
──────────┼──────────────────────────────────────┼──────────────────────────────
θ (theta) │ Thermomètre économique = D / V_on    │ thermometer()
I         │ Indicateur centré = θ - 1            │ indicator()
r_ic      │ Taux inflation/contraction (Δθ)      │ RADState.r_ic, calculate_r_ic()
ν_eff     │ Vélocité effective = U / V_on        │ RADState.nu_eff, calculate_nu_eff()
τ_eng     │ Taux engagement = D_eng / D_total    │ RADState.tau_eng, calculate_tau_eng()

PARAMÈTRES DE RÉGULATION RAD (Contracycliques)
─────────────────────────────────────────────────────────────────────────────
Symbole   │ Signification                        │ Variable Code
──────────┼──────────────────────────────────────┼──────────────────────────────
κ (kappa) │ Coeff. LIQUIDITÉ [0.5, 2.0]          │ RADState.kappa, update_kappa()
          │ Module conversion V→U ET montant RU  │
          │ • θ > 1 (surchauffe) → κ < 1 (FREINE liquidité)
          │ • θ < 1 (sous-régime) → κ > 1 (STIMULE liquidité)
          │ • θ = 1 (équilibre) → κ = 1 (neutre) │
η (eta)   │ Rendement combustion S+U→V [0.5, 2.0]│ RADState.eta, compute_eta()
          │ • θ > 1 → η < 1 (freine production)  │
          │ • θ < 1 → η > 1 (stimule production) │
          │ • θ = 1 → η = 1 (production normale) │
δ_m       │ Amortissement mensuel D              │ RADState.delta_m (≈0.104%/mois)
          │ (≈ 0.104%/mois ≈ 1.25%/an)           │ apply_amortization()
τ (tau)   │ Taux revenu universel (1% défaut)    │ universal_income_rate
α_RU      │ Contrainte variation max RU (10%)    │ alpha_RU
β (beta)  │ Sensibilité κ à l'indicateur I       │ RADState.kappa_beta
α (alpha) │ Sensibilité η à l'indicateur I       │ RADState.eta_alpha

MÉCANISMES ÉCONOMIQUES FONDAMENTAUX
─────────────────────────────────────────────────────────────────────────────
Mécanisme            │ Formule/Description              │ Fonction Code
─────────────────────┼──────────────────────────────────┼──────────────────────
Thermomètre          │ θ = D / V_on                     │ thermometer()
Indicateur           │ I = θ - 1                        │ indicator()
Conversion V→U       │ U = V × κ (κ module liquidité)   │ convert_V_to_U()
Combustion           │ S + U → V × η                    │ CompteEntreprise.distribute_V_genere()
Revenu Universel     │ RU_t = κ × (V_on × τ) / N_agents│ distribute_universal_income()
                     │ (κ module liquidité distribuée)  │
Distribution 40/60   │ 40% → Masse salariale (U)        │ CompteEntreprise (ratio_salarial=0.40)
                     │ 60% → Trésorerie (V_operationnel)│ CompteEntreprise (ratio_tresorerie=0.60)

COUCHES DE RÉGULATION RAD (Architecture Multi-Couches)
─────────────────────────────────────────────────────────────────────────────
Couche │ Déclenchement           │ Action                      │ Code
───────┼─────────────────────────┼─────────────────────────────┼─────────────
C1     │ Chaque cycle            │ Ajuste κ et η               │ regulate() (continu)
       │                         │ Réduction cyclique D        │
C2     │ Tous les T=12 cycles    │ Régulation profonde         │ regulate() (si |I| > 15%)
       │ si |I| > 15%            │ Recalibration structurelle  │
C3     │ Si |I| > 30%            │ Rebalancement D_regulatrice │ regulate() (urgence)
       │                         │ Intervention d'urgence      │ (limité à 5 cycles consécutifs)

COMPTES ENTREPRISES (Distribution Organique)
─────────────────────────────────────────────────────────────────────────────
Variable          │ Signification                    │ Code
──────────────────┼──────────────────────────────────┼──────────────────────────
V_entreprise      │ Patrimoine de base entreprise    │ CompteEntreprise.V_entreprise
V_operationnel    │ Trésorerie opérationnelle        │ CompteEntreprise.V_operationnel
Seuil rétention   │ Limite V_op (20% × V_entreprise) │ CompteEntreprise.seuil_retention
NFT_financier     │ Titre productif (excédent V)     │ NFTFinancier
Masse salariale   │ 40% V généré → U (salaires)      │ ratio_salarial (0.40)
Trésorerie        │ 60% V généré → V_operationnel    │ ratio_tresorerie (0.60)

DÉMOGRAPHIE ET POPULATION
─────────────────────────────────────────────────────────────────────────────
Variable          │ Signification                    │ Code
──────────────────┼──────────────────────────────────┼──────────────────────────
N_agents          │ Nombre d'agents (population)     │ len(agents)
Âge moyen         │ Âge moyen de la population       │ Demographics.get_statistics()
Taux natalité     │ Naissances annuelles (4.14%)     │ Demographics.birth_rate
Espérance de vie  │ Espérance de vie (80 ans)        │ Demographics.life_expectancy
D_conso/an/pers   │ D consommation annuelle/personne │ Demographics.consumption_D_per_year

ORACLE D'INITIALISATION
─────────────────────────────────────────────────────────────────────────────
Variable          │ Signification                    │ Code
──────────────────┼──────────────────────────────────┼──────────────────────────
φ_or (phi_or)     │ Facteur or de zone               │ Oracle.phi_or
V_0               │ Verum initial = valeur × auth    │ Asset.V_initial
D_0               │ Miroir initial = V_0             │ Asset.D_initial
NFT fondateur     │ Preuve crypto existence unique   │ Asset.nft_hash
auth_factor       │ Facteur authentification         │ Asset.auth_factor (1.0 = officiel)

═══════════════════════════════════════════════════════════════════════════════
PRINCIPES THÉORIQUES FONDAMENTAUX
═══════════════════════════════════════════════════════════════════════════════

1. ÉQUILIBRE INITIAL : ΣV₀ = ΣD₀ (vérifié dans _verify_initial_balance())

2. THERMOMÈTRE θ = D / V_on :
   - θ = 1.0 : Équilibre parfait (cible)
   - θ > 1.0 : Surchauffe (excès de demande)
   - θ < 1.0 : Sous-régime (excès d'offre)

3. RÉGULATION CONTRACYCLIQUE :
   - Surchauffe (θ > 1) → κ ↓, η ↓ (freinent conversion et production)
   - Sous-régime (θ < 1) → κ ↑, η ↑ (stimulent conversion et production)
   - Équilibre (θ = 1) → κ = 1, η = 1 (neutre)

4. REVENU UNIVERSEL : RU basé sur V_on (valeur vivante), avec contrainte α_RU

5. DISTRIBUTION ORGANIQUE 40/60 : Entreprises distribuent V généré selon
   40% masse salariale (U) + 60% trésorerie (V_operationnel)

6. AMORTISSEMENT : δ_m ≈ 0.104%/mois ≈ 1.25%/an (appliqué à toutes composantes D)

═══════════════════════════════════════════════════════════════════════════════

Références théoriques :
- Cybernétique : Wiener, Ashby, Beer
- Thermodynamique : Georgescu-Roegen, Ayres
- Anthropologie économique : Graeber, Polanyi, Mauss

Voir aussi : MAPPING_THEORY_CODE.md pour le mapping complet détaillé
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Import modules IRIS étendus
from .iris_oracle import Oracle, FluxType, NFTMetadata
from .iris_chambre_relance import ChambreRelance, OrphanReason
from .iris_comptes_entreprises import (
    RegistreComptesEntreprises, CompteEntreprise, BusinessType, NFTFinancier
)
from .iris_prix import PriceManager, GoodType
from .iris_entreprises import EntrepriseManager


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTE TEMPORELLE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════
STEPS_PER_YEAR = 12  # 1 step = 1 mois, donc 12 steps = 1 an


class AssetType(Enum):
    """Types d'actifs dans le système IRIS"""
    IMMOBILIER = "immobilier"
    MOBILIER = "mobilier"
    ENTREPRISE = "entreprise"
    INTELLECTUEL = "intellectuel"
    SERVICE = "service"


class DebtComponent(Enum):
    """Composantes de la dette thermométrique"""
    MATERIELLE = "materielle"  # Biens et immobilisations
    SERVICES = "services"  # Flux d'entretien
    CONTRACTUELLE = "contractuelle"  # Titres à promesse productive
    ENGAGEMENT = "engagement"  # Opérations de staking
    REGULATRICE = "regulatrice"  # Chambre de Relance


@dataclass
class Asset:
    """
    Représente un actif dans le système IRIS

    Un actif est un bien réel (terrain, immeuble, entreprise, etc.) qui est
    ancré dans le système via l'Oracle d'initialisation. Chaque actif génère :
    - Un Verum (V) : la mémoire de sa valeur
    - Un miroir thermométrique (D) : l'indicateur de régulation associé
    - Un NFT fondateur : preuve cryptographique d'existence unique
    """
    id: str  # Identifiant unique de l'actif
    asset_type: AssetType  # Type d'actif (immobilier, mobilier, etc.)
    real_value: float  # Valeur réelle dans le monde physique (en unités monétaires classiques)
    V_initial: float = 0.0  # V₀ : Verum d'initialisation (mémoire de valeur IRIS)
    D_initial: float = 0.0  # D₀ : Miroir thermométrique initial (indicateur de régulation)
    owner_id: str = ""  # Identifiant du propriétaire
    nft_hash: str = ""  # Empreinte cryptographique du NFT fondateur (SHA-256)
    auth_factor: float = 1.0  # Facteur d'authentification (1.0 = source officielle, <1.0 = auto-déclaration)
    creation_time: int = 0  # Moment de l'ancrage dans le système

    def __post_init__(self):
        """
        Initialise V₀ et D₀ selon les règles IRIS

        Principe fondamental : Équilibre initial ΣV₀ = ΣD₀
        Cette égalité garantit que le thermomètre θ = D/V démarre à 1.0
        """
        if self.V_initial == 0.0:
            # Conversion de la valeur réelle en Verum IRIS
            # Formule complète : V_IRIS = V_asset × facteur_or × ajustement_thermométrique × auth_factor
            # Pour simplification dans cette simulation, on utilise directement real_value × auth_factor
            self.V_initial = self.real_value * self.auth_factor

            # Création du miroir thermométrique : D₀ = V₀
            # Ce miroir n'est PAS une dette exigible, mais un indicateur de régulation
            # Il permet au RAD de mesurer la tension thermométrique du système
            self.D_initial = self.V_initial


@dataclass
class Agent:
    """
    Représente un agent économique dans le système IRIS

    Un agent est une personne ou une entité qui possède :
    - Des actifs réels (ancré dans le système)
    - Un solde V (Verum) : mémoire de valeur, patrimoine ancré
    - Un solde U (Usage) : monnaie d'usage, liquidité pour transactions
    - Un score de contribution : mesure des actes prouvés
    - Des biens de consommation accumulés (consumables)

    L'agent peut :
    - Convertir V en U (activer son patrimoine)
    - Reconvertir U en V (épargner, investir)
    - Effectuer des transactions en U
    - Recevoir le revenu universel
    """
    id: str  # Identifiant unique de l'agent
    V_balance: float = 0.0  # Solde en Verum (patrimoine, mémoire de valeur)
    U_balance: float = 0.0  # Solde en Usage (liquidité, monnaie de transaction)
    assets: List[Asset] = field(default_factory=list)  # Liste des actifs possédés
    contribution_score: float = 0.0  # Score de contribution prouvée (pour gouvernance future)
    consumables: float = 0.0  # Biens de consommation accumulés (lifetime consumption D)

    def add_asset(self, asset: Asset) -> None:
        """
        Ajoute un actif et met à jour le solde V

        Quand un agent ancre un nouvel actif :
        - L'actif est ajouté à sa liste
        - Son V_balance augmente du V₀ de l'actif
        - Le système global gagne V₀ en circulation et D₀ dans le RAD

        Args:
            asset: Actif à ajouter
        """
        self.assets.append(asset)
        self.V_balance += asset.V_initial  # Crédite le Verum d'initialisation

    def remove_asset(self, asset_id: str) -> None:
        """
        Retire un actif et met à jour le solde V

        Utilise lors de la destruction d'un actif (catastrophe, etc.)
        - L'actif est retire de la liste
        - Le V_balance est reduit du V_initial de l'actif

        Args:
            asset_id: Identifiant de l'actif à retirer
        """
        for i, asset in enumerate(self.assets):
            if asset.id == asset_id:
                self.V_balance -= asset.V_initial
                self.assets.pop(i)
                break

    def total_wealth(self) -> float:
        """
        Richesse totale de l'agent (V + U)

        La richesse totale combine :
        - V : patrimoine ancré (épargne, actifs)
        - U : liquidité (argent de poche)
        Cette somme est utilisée pour calculer le revenu universel
        """
        return self.V_balance + self.U_balance


@dataclass
class RADState:
    """
    État du Régulateur Automatique Décentralisé (RAD)

    Le RAD est le cœur du système IRIS. C'est un mécanisme autonome
    qui maintient l'équilibre thermodynamique en ajustant les paramètres
    du système selon la tension mesurée.

    Analogie : Le RAD joue le rôle d'un thermostat pour l'économie.
    - Si θ > 1 (trop de demande) → il refroidit (réduit κ)
    - Si θ < 1 (trop d'offre) → il réchauffe (augmente κ)

    ARCHITECTURE MULTI-COUCHES (Phase C) :
    - C1 : Régulation continue (κ, η) - chaque cycle
    - C2 : Régulation profonde (τ, ajustements structurels) - périodique (T cycles)
    - C3 : Rebalancement d'urgence (D direct) - si |I| > seuil critique

    CAPTEURS DE RÉGULATION :
    - r_ic : Taux d'inflation/contraction (variation θ)
    - ν_eff : Vélocité effective (circulation U/V)
    - τ_eng : Taux d'engagement (staking, D_engagement/D_total)

    Composantes de D (miroir thermométrique sectoriel) :
    - D_materielle : Biens physiques (terrains, immeubles)
    - D_services : Flux d'entretien et services
    - D_contractuelle : Titres et promesses productives
    - D_engagement : Staking et engagements
    - D_regulatrice : Chambre de relance (revenu universel)
    """
    # Composantes sectorielles du miroir thermométrique D
    # Chaque composante suit un type spécifique d'actifs/transactions
    D_materielle: float = 0.0  # Dette thermométrique des biens matériels
    D_services: float = 0.0  # Dette thermométrique des services
    D_contractuelle: float = 0.0  # Dette thermométrique des contrats
    D_engagement: float = 0.0  # Dette thermométrique des engagements
    D_regulatrice: float = 0.0  # Dette thermométrique de la régulation (RU, dissipation)

    # Paramètres de régulation du système
    kappa: float = 1.0  # Coefficient de conversion V → U (κ, kappa)
    eta: float = 1.0  # Coefficient d'efficacité (η, eta) - NOUVEAU Phase C
    T_period: int = 12  # Périodicité de régulation profonde (12 cycles = 1 an)
    dissipation_rate: float = 0.0  # Supprimé : friction non-IRIS (était 0.02)

    # Amortissement global de la dette thermométrique D (conforme document IRIS)
    delta_m: float = 0.001041666  # Amortissement mensuel ≈ 0.104%/mois ≈ 1.25%/an

    # CORRECTION C: PARAMÈTRES η (ETA) et κ (KAPPA) AVEC BORNES STRICTES [0.7, 1.3]
    # Bornes de η (rendement combustion S+U→V) - CORRECTION C
    eta_min: float = 0.7  # Rendement minimum (70%) - borne stricte
    eta_max: float = 1.3  # Rendement maximum (130%) - borne stricte
    eta_smoothing: float = 0.15  # Facteur de lissage EMA pour η (évite oscillations)

    # Bornes de κ (conversion V→U) - CORRECTION C
    kappa_min: float = 0.7  # Conversion minimum (70%) - borne stricte
    kappa_max: float = 1.3  # Conversion maximum (130%) - borne stricte
    kappa_smoothing: float = 0.1  # Facteur de lissage EMA pour κ

    # CORRECTION A: SYSTÈME TRI-CAPTEUR (THÉORIE §3.3.1)
    # Cibles des capteurs
    nu_target: float = 0.20  # Cible vitesse circulation (20%)
    tau_target: float = 0.35  # Cible taux engagement (35%)

    # Coefficients tri-capteur pour Δη (THÉORIE §3.3.1)
    alpha_eta: float = 0.3  # Poids thermomètre dans Δη
    beta_eta: float = 0.4  # Poids vitesse dans Δη
    gamma_eta: float = 0.2  # Poids engagement dans Δη

    # Coefficients tri-capteur pour Δκ (THÉORIE §3.3.1)
    alpha_kappa: float = 0.4  # Poids vitesse dans Δκ
    beta_kappa: float = 0.3  # Poids engagement dans Δκ
    gamma_kappa: float = 0.2  # Poids thermomètre dans Δκ

    # Contraintes de variation (THÉORIE §3.3.1)
    max_delta_eta: float = 0.15  # |Δη| ≤ 0.15 (15% max par cycle)
    max_delta_kappa: float = 0.15  # |Δκ| ≤ 0.15 (15% max par cycle)

    # Capteurs de régulation (Phase C)
    r_ic: float = 0.0  # Taux inflation/contraction (variation θ)
    nu_eff: float = 0.0  # Vélocité effective (circulation)
    tau_eng: float = 0.0  # Taux engagement (staking)

    # Historique pour calcul capteurs et calibration
    theta_history: List[float] = field(default_factory=list)
    eta_history: List[float] = field(default_factory=list)  # Pour smoothing
    kappa_history: List[float] = field(default_factory=list)  # Pour analyse

    # Seuils activation couches
    C2_activation_threshold: float = 0.15  # |I| > 15% → active C2
    C3_activation_threshold: float = 0.30  # |I| > 30% → active C3

    # Compteur de cycles de crise (pour limiter durée intervention C3)
    C3_crisis_counter: int = 0  # Nombre de cycles consécutifs en mode C3
    C3_max_duration: int = 5  # Durée maximale d'intervention C3 (5 cycles consécutifs)
    C3_cooldown_counter: int = 0  # Période de repos après intervention C3

    # Calibration automatique
    auto_calibration_enabled: bool = True  # Active la calibration automatique
    calibration_period: int = 50  # Période de recalibration (en cycles)
    oscillation_tolerance: float = 0.20  # Tolérance d'oscillation de θ (±20%)

    def total_D(self) -> float:
        """
        Calcule la dette thermométrique totale D

        D = somme de toutes les composantes sectorielles
        D est utilisé pour calculer le thermomètre : θ = D/V

        Note : D n'est PAS une dette au sens juridique, c'est un
        indicateur de régulation (miroir thermométrique)
        """
        return (self.D_materielle + self.D_services + self.D_contractuelle +
                self.D_engagement + self.D_regulatrice)

    def compute_delta_kappa(self, r_t: float, nu_eff: float, tau_eng: float) -> float:
        """
        CORRECTION A: Calcule la VARIATION Δκ selon le système tri-capteur

        FORMULE TRI-CAPTEUR (THÉORIE §3.3.1):
        Δκ_t = α_κ × (ν_target - ν) - β_κ × (τ_eng - τ_target) + γ_κ × (1 - r)

        où:
        - α_κ = 0.4 : poids de la vitesse de circulation
        - β_κ = 0.3 : poids de l'engagement
        - γ_κ = 0.2 : poids du thermomètre
        - ν_target = 0.20 : cible vitesse (20%)
        - τ_target = 0.35 : cible engagement (35%)

        Args:
            r_t: Thermomètre (r = D/V_on, cible = 1.0)
            nu_eff: Vélocité effective (U/V_on)
            tau_eng: Taux d'engagement (D_eng/D_total)

        Returns:
            Variation Δκ (bornée dans [-max_delta_kappa, +max_delta_kappa])
        """
        # Contribution de la vitesse de circulation
        contrib_vitesse = self.alpha_kappa * (self.nu_target - nu_eff)

        # Contribution de l'engagement (signe négatif)
        contrib_engagement = -self.beta_kappa * (tau_eng - self.tau_target)

        # Contribution du thermomètre
        contrib_thermo = self.gamma_kappa * (1.0 - r_t)

        # Variation totale
        delta_kappa = contrib_vitesse + contrib_engagement + contrib_thermo

        # Contrainte de variation maximale
        delta_kappa = np.clip(delta_kappa, -self.max_delta_kappa, self.max_delta_kappa)

        return float(delta_kappa)

    def update_kappa(self, r_t: float, nu_eff: float, tau_eng: float) -> None:
        """
        CORRECTION A: Mise à jour κ (kappa) avec système tri-capteur

        Utilise la formule tri-capteur pour calculer Δκ, puis applique la variation
        avec contraintes de bornes.

        Formule : Δκ_t = α_κ×(ν_target-ν) - β_κ×(τ_eng-τ_target) + γ_κ×(1-r)

        Args:
            r_t: Thermomètre (r = D/V_on, cible = 1.0)
            nu_eff: Vélocité effective (U/V_on, cible = 0.20)
            tau_eng: Taux d'engagement (D_eng/D_total, cible = 0.35)
        """
        # Calcul de la variation Δκ via tri-capteur
        delta_kappa = self.compute_delta_kappa(r_t, nu_eff, tau_eng)

        # Application de la variation
        self.kappa += delta_kappa

        # Application des bornes strictes [0.7, 1.3]
        self.kappa = float(np.clip(self.kappa, self.kappa_min, self.kappa_max))

        # Enregistrement dans l'historique
        self.kappa_history.append(self.kappa)
        if len(self.kappa_history) > 100:
            self.kappa_history.pop(0)

    def compute_delta_eta(self, r_t: float, nu_eff: float, tau_eng: float) -> float:
        """
        CORRECTION A: Calcule la VARIATION Δη selon le système tri-capteur

        FORMULE TRI-CAPTEUR (THÉORIE §3.3.1):
        Δη_t = α_η × (1 - r) + β_η × (ν_target - ν) - γ_η × (τ_eng - τ_target)

        où:
        - α_η = 0.3 : poids du thermomètre
        - β_η = 0.4 : poids de la vitesse
        - γ_η = 0.2 : poids de l'engagement
        - ν_target = 0.20 : cible vitesse (20%)
        - τ_target = 0.35 : cible engagement (35%)

        Args:
            r_t: Thermomètre (r = D/V_on, cible = 1.0)
            nu_eff: Vélocité effective (U/V_on)
            tau_eng: Taux d'engagement (D_eng/D_total)

        Returns:
            Variation Δη (bornée dans [-max_delta_eta, +max_delta_eta])
        """
        # Contribution du thermomètre
        contrib_thermo = self.alpha_eta * (1.0 - r_t)

        # Contribution de la vitesse
        contrib_vitesse = self.beta_eta * (self.nu_target - nu_eff)

        # Contribution de l'engagement (signe négatif)
        contrib_engagement = -self.gamma_eta * (tau_eng - self.tau_target)

        # Variation totale
        delta_eta = contrib_thermo + contrib_vitesse + contrib_engagement

        # Contrainte de variation maximale
        delta_eta = np.clip(delta_eta, -self.max_delta_eta, self.max_delta_eta)

        return float(delta_eta)

    def update_eta(self, r_t: float, nu_eff: float, tau_eng: float) -> None:
        """
        CORRECTION A: Mise à jour η (eta) avec système tri-capteur

        Utilise la formule tri-capteur pour calculer Δη, puis applique la variation
        avec contraintes de bornes.

        Formule : Δη_t = α_η×(1-r) + β_η×(ν_target-ν) - γ_η×(τ_eng-τ_target)

        Args:
            r_t: Thermomètre (r = D/V_on, cible = 1.0)
            nu_eff: Vélocité effective (U/V_on, cible = 0.20)
            tau_eng: Taux d'engagement (D_eng/D_total, cible = 0.35)
        """
        # Calcul de la variation Δη via tri-capteur
        delta_eta = self.compute_delta_eta(r_t, nu_eff, tau_eng)

        # Application de la variation
        self.eta += delta_eta

        # Application des bornes strictes [0.7, 1.3]
        self.eta = float(np.clip(self.eta, self.eta_min, self.eta_max))

        # Enregistrement dans l'historique
        self.eta_history.append(self.eta)
        if len(self.eta_history) > 100:
            self.eta_history.pop(0)

    def calculate_r_ic(self, current_theta: float) -> float:
        """
        Calcule r_ic : taux d'inflation/contraction

        r_ic mesure la variation du thermomètre θ entre deux périodes.
        C'est un indicateur de la pression inflationniste ou déflationniste.

        Formule : r_ic = (θ_t - θ_{t-1}) / θ_{t-1}

        Returns:
            Taux de variation de θ (positif = inflation, négatif = déflation)
        """
        if len(self.theta_history) == 0:
            self.theta_history.append(current_theta)
            return 0.0

        last_theta = self.theta_history[-1]
        if last_theta > 0:
            r_ic = (current_theta - last_theta) / last_theta
        else:
            r_ic = 0.0

        # Mise à jour historique
        self.theta_history.append(current_theta)

        # Garde seulement les 12 dernières valeurs (1 an)
        if len(self.theta_history) > 12:
            self.theta_history.pop(0)

        self.r_ic = r_ic
        return r_ic

    def calculate_nu_eff(self, total_U: float, V_on: float) -> float:
        """
        Calcule ν_eff : vélocité effective de circulation

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        ν_eff mesure la fluidité de la monnaie d'usage U dans le système,
        par rapport à la valeur VIVANTE en circulation (V_on).

        Formule (conforme à la théorie) :
        ν_eff = U / V_on

        Interprétation :
        - ν_eff élevé : beaucoup de liquidité, économie active
        - ν_eff faible : liquidité bloquée, patrimoine immobilisé

        Note d'implémentation :
        Utilise V_on (valeur vivante) au lieu de V total pour refléter
        la circulation réelle, excluant les immobilisations (NFT, réserves).

        Args:
            total_U: Total de la monnaie d'usage en circulation
            V_on: Valeur vivante en circulation (excluant immobilisations)

        Returns:
            Vélocité effective (ratio U/V_on)
        """
        if V_on > 0:
            nu_eff = total_U / V_on
        else:
            nu_eff = 0.0

        self.nu_eff = nu_eff
        return nu_eff

    def calculate_tau_eng(self) -> float:
        """
        Calcule τ_eng : taux d'engagement (staking)

        τ_eng mesure la part de la dette thermométrique issue des engagements
        (staking, promesses productives, etc.).

        Formule : τ_eng = D_engagement / D_total

        Interprétation :
        - τ_eng élevé : forte mobilisation des actifs
        - τ_eng faible : actifs peu engagés

        Returns:
            Taux d'engagement (0-1)
        """
        total_D = self.total_D()
        if total_D > 0:
            tau_eng = self.D_engagement / total_D
        else:
            tau_eng = 0.0

        self.tau_eng = tau_eng
        return tau_eng

    def auto_calibrate(self, cycle: int) -> Dict[str, float]:
        """
        Calibration automatique des coefficients η et κ selon les oscillations de θ

        OBJECTIF :
        Ajuste dynamiquement les paramètres de sensibilité (alpha, beta, gamma)
        pour stabiliser le système et réduire les oscillations du thermomètre.

        PRINCIPE :
        - Mesure l'amplitude des oscillations de θ sur les N derniers cycles
        - Si oscillations > tolérance : RÉDUIT la sensibilité (alpha, beta)
        - Si oscillations < tolérance/2 : AUGMENTE légèrement la sensibilité
        - Converge vers des paramètres optimaux pour la stabilité

        MÉTHODE :
        1. Calcule l'écart-type de θ sur les 50 derniers cycles
        2. Compare à la tolérance cible (oscillation_tolerance)
        3. Ajuste alpha, beta proportionnellement à l'écart

        FRÉQUENCE :
        Activé tous les calibration_period cycles (défaut: 50)

        Args:
            cycle: Numéro de cycle actuel

        Returns:
            Dictionnaire des ajustements effectués
        """
        if not self.auto_calibration_enabled:
            return {}

        # Ne calibre que périodiquement
        if cycle % self.calibration_period != 0 or cycle == 0:
            return {}

        # Besoin d'au moins 20 mesures pour une calibration fiable
        if len(self.theta_history) < 20:
            return {}

        # MESURE DES OSCILLATIONS : écart-type de θ
        theta_recent = np.array(self.theta_history[-50:])  # 50 dernières valeurs
        theta_mean = np.mean(theta_recent)
        theta_std = np.std(theta_recent)  # Écart-type = mesure d'oscillation

        # DIAGNOSTIC : oscillations par rapport à la tolérance
        oscillation_ratio = theta_std / self.oscillation_tolerance

        adjustments = {}

        # CAS 1 : OSCILLATIONS EXCESSIVES (> tolérance)
        # → Système instable, réduire la sensibilité
        if oscillation_ratio > 1.2:
            # Réduction proportionnelle (10% par excès de 20%)
            reduction_factor = 0.9  # Réduit de 10%

            # Ajuste ETA
            old_alpha = self.eta_alpha
            self.eta_alpha *= reduction_factor
            self.eta_alpha = max(0.1, min(1.0, self.eta_alpha))  # Bornes [0.1, 1.0]
            adjustments['eta_alpha'] = self.eta_alpha - old_alpha

            # Ajuste KAPPA
            old_beta = self.kappa_beta
            self.kappa_beta *= reduction_factor
            self.kappa_beta = max(0.1, min(1.0, self.kappa_beta))  # Bornes [0.1, 1.0]
            adjustments['kappa_beta'] = self.kappa_beta - old_beta

            # Augmente le smoothing (plus d'inertie)
            old_smooth = self.eta_smoothing
            self.eta_smoothing = min(0.3, self.eta_smoothing * 1.1)
            adjustments['eta_smoothing'] = self.eta_smoothing - old_smooth

        # CAS 2 : OSCILLATIONS TROP FAIBLES (< tolérance/2)
        # → Système trop mou, augmenter légèrement la réactivité
        elif oscillation_ratio < 0.5:
            # Augmentation modérée (5%)
            increase_factor = 1.05

            # Ajuste ETA
            old_alpha = self.eta_alpha
            self.eta_alpha *= increase_factor
            self.eta_alpha = max(0.1, min(1.0, self.eta_alpha))
            adjustments['eta_alpha'] = self.eta_alpha - old_alpha

            # Ajuste KAPPA
            old_beta = self.kappa_beta
            self.kappa_beta *= increase_factor
            self.kappa_beta = max(0.1, min(1.0, self.kappa_beta))
            adjustments['kappa_beta'] = self.kappa_beta - old_beta

            # Réduit légèrement le smoothing (moins d'inertie)
            old_smooth = self.eta_smoothing
            self.eta_smoothing = max(0.05, self.eta_smoothing * 0.95)
            adjustments['eta_smoothing'] = self.eta_smoothing - old_smooth

        # CAS 3 : OSCILLATIONS OPTIMALES
        # → Aucun ajustement nécessaire
        else:
            adjustments['status'] = 'optimal'

        # Enregistre les diagnostics
        adjustments['theta_std'] = theta_std
        adjustments['oscillation_ratio'] = oscillation_ratio
        adjustments['theta_mean'] = theta_mean

        return adjustments

    def update_sensors(self, current_theta: float, total_U: float, V_on: float) -> None:
        """
        Met à jour tous les capteurs de régulation

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        Les capteurs utilisent V_on (valeur vivante en circulation) pour
        refléter la dynamique économique réelle.

        Args:
            current_theta: Thermomètre actuel θ = D / V_on
            total_U: Total monnaie d'usage en circulation
            V_on: Valeur vivante en circulation (excluant immobilisations)
        """
        self.calculate_r_ic(current_theta)
        self.calculate_nu_eff(total_U, V_on)
        self.calculate_tau_eng()


class IRISEconomy:
    """
    Modèle complet de l'économie IRIS

    Principes fondamentaux :
    1. Équilibre initial : ΣV₀ = ΣD₀
    2. Thermomètre global : θ = D/V_circulation
    3. Régulation contracyclique via RAD
    4. Conservation des flux avec dissipation mesurée
    """

    def __init__(self,
                 initial_agents: int = 100,
                 gold_factor: float = 1.0,
                 universal_income_rate: float = 0.01,
                 enable_demographics: bool = True,
                 enable_catastrophes: bool = True,
                 enable_price_discovery: bool = True,
                 enable_dynamic_business: bool = True,
                 enable_business_combustion: bool = True,
                 enable_chambre_relance: bool = True,
                 time_scale: Optional[str] = None,  # DEPRECATED: 1 step = 1 mois (fixe)
                 max_population: int = 10000,
                 initial_total_wealth_V: Optional[float] = None,
                 mode_population: str = "object",
                 taux_creation_entreprises: float = 0.05,
                 taux_faillite_entreprises: float = 0.03,
                 seed: Optional[int] = None):
        """
        Initialise l'économie IRIS (version 2.1 unifiée)

        Cette version unifie l'ancien iris_model.py avec iris_v2_1_model.py
        en créant une architecture modulaire configurable.

        ÉCHELLE TEMPORELLE : 1 step = 1 mois (STEPS_PER_YEAR = 12)

        Args:
            initial_agents: Nombre d'agents initiaux (population de départ)
            gold_factor: Facteur or de zone (équivalent or local)
            universal_income_rate: Taux de revenu universel (annuel)
            enable_demographics: Active la démographie (naissances/décès/âges)
            enable_catastrophes: Active les catastrophes aléatoires
            enable_price_discovery: Active le mécanisme de prix explicites
            enable_dynamic_business: Active les entreprises dynamiques (créations/faillites)
            enable_business_combustion: Active la combustion des entreprises (S+U→V, distribution 40/60)
            enable_chambre_relance: Active la Chambre de Relance (redistribution pool orphelins)
            time_scale: DEPRECATED - Ignoré, l'échelle est toujours en mois (1 step = 1 mois)
            max_population: Population maximale (0 = illimité, défaut: 10000)
            initial_total_wealth_V: Richesse totale initiale à répartir entre agents
                                    (None = calcul auto: ~5.78 V/agent, ancien défaut: 1 200 000)
            mode_population: "object" (détaillé, NFT) ou "vectorized" (rapide, gros volumes)
            taux_creation_entreprises: Taux de création d'entreprises (si enable_dynamic_business)
            taux_faillite_entreprises: Taux de faillite de base (si enable_dynamic_business)
            seed: Graine aléatoire pour reproductibilité (None = aléatoire)
        """
        # Graine aléatoire si fournie
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)

        # Mode de population
        # IMPORTANT: Mode vectorisé désactivé (expérimental et non fiabilisé)
        if mode_population != "object":
            raise NotImplementedError(
                f"Le mode '{mode_population}' est expérimental et désactivé dans cette version. "
                f"Seul le mode 'object' est supporté. "
                f"Pour réactiver le mode vectorisé, voir RAPPORT_CORRECTIONS_IRIS.md section 'Mode vectorisé'."
            )
        self.mode_population = "object"

        self.agents: Dict[str, Agent] = {}
        self.assets: Dict[str, Asset] = {}
        self.population = None  # VectorizedPopulation si mode vectorisé

        self.rad = RADState()
        self.gold_factor = gold_factor
        self.universal_income_rate = universal_income_rate

        # DEPRECATED: time_scale est maintenant toujours "months" (1 step = 1 mois)
        if time_scale is not None and time_scale != "months":
            import warnings
            warnings.warn(
                f"time_scale='{time_scale}' est ignoré. L'échelle est maintenant fixée à 1 step = 1 mois.",
                DeprecationWarning,
                stacklevel=2
            )
        self.time_scale = "months"  # Fixé, toujours en mois

        self.enable_demographics = enable_demographics
        self.enable_catastrophes = enable_catastrophes
        self.enable_price_discovery = enable_price_discovery
        self.enable_dynamic_business = enable_dynamic_business
        self.enable_business_combustion = enable_business_combustion
        self.enable_chambre_relance = enable_chambre_relance
        self.max_population = max_population

        # Calcul automatique de initial_total_wealth_V si non spécifié
        # Nouveau ratio: ~5.78 V/agent (23530 V pour 4069 agents)
        # Au lieu de l'ancien: 12000 V/agent (1200000 V pour 100 agents)
        if initial_total_wealth_V is None:
            self.initial_total_wealth_V = initial_agents * 5.78
            print(f"INFO: Richesse initiale calculée automatiquement: {self.initial_total_wealth_V:.2f} V ({initial_agents} agents × 5.78 V/agent)")
        else:
            self.initial_total_wealth_V = initial_total_wealth_V

        # Modules fondamentaux IRIS
        self.oracle = Oracle(phi_or_default=gold_factor)
        self.chambre_relance = ChambreRelance()
        self.registre_entreprises = RegistreComptesEntreprises()

        # Modules optionnels
        self.demographics = None
        self.catastrophe_manager = None
        self.price_manager = None
        self.entreprise_manager = None
        self.agent_ages: Dict[str, int] = {}

        # Si démographie activée, initialise le module
        if enable_demographics:
            from .iris_demographics import Demographics
            self.demographics = Demographics(max_population=max_population)

        # Si catastrophes activées, initialise le gestionnaire
        if enable_catastrophes:
            from .iris_catastrophes import CatastropheManager
            self.catastrophe_manager = CatastropheManager()

        # Si prix explicites activés, initialise le gestionnaire
        if enable_price_discovery:
            self.price_manager = PriceManager(epsilon=1e-6, max_step_change=0.05)

            # Enregistre quelques biens par défaut avec poids
            # Poids basés sur importance dans panier consommation
            self.price_manager.register_good("food", initial_price=1.0, weight=0.25)
            self.price_manager.register_good("housing", initial_price=1.0, weight=0.30)
            self.price_manager.register_good("services", initial_price=1.0, weight=0.20)
            self.price_manager.register_good("energy", initial_price=1.0, weight=0.15)
            self.price_manager.register_good("culture", initial_price=1.0, weight=0.10)

        # Si entreprises dynamiques activées, initialise le gestionnaire
        if enable_dynamic_business:
            self.entreprise_manager = EntrepriseManager(
                registre=self.registre_entreprises,
                taux_creation=taux_creation_entreprises,
                taux_faillite_base=taux_faillite_entreprises
            )

        # Métriques de suivi
        self.time = 0
        self.history = {
            'time': [],
            'total_V': [],
            'total_U': [],
            'total_D': [],
            'thermometer': [],
            'indicator': [],
            'kappa': [],
            'eta': [],  # Coefficient de rendement η (combustion S+U→V)
            'gini_coefficient': [],
            'circulation_rate': [],
            'population': [],
            'avg_age': [],
            'births': [],
            'deaths': [],
            'catastrophes': [],
            'RU_distribue': [],  # Suivi du revenu universel distribué (basé sur V_on)
            'business_masse_salariale': [],  # Masse salariale des entreprises (40% organique)
            'business_NFT_created': [],  # NFT financiers créés
            'C2_activated': [],  # Activation couche C2 (régulation profonde)
            'C3_activated': [],  # Activation couche C3 (rebalancement d'urgence)
            'C3_crisis_duration': [],  # Durée intervention C3 (cycles consécutifs)
            'D_lifetime': [],  # D de consommation de vie (versée au décès)
            # Métriques v2.1 supplémentaires
            'prix_moyen': [],  # Prix moyen (si enable_price_discovery)
            'inflation': [],  # Inflation globale (si enable_price_discovery)
            'nb_entreprises': [],  # Nombre d'entreprises actives
            'creations_entreprises': [],  # Créations d'entreprises (si enable_dynamic_business)
            'faillites_entreprises': []  # Faillites d'entreprises (si enable_dynamic_business)
        }

        # Paramètres revenu universel contraint
        self.last_RU_per_agent = 0.0  # Dernier RU distribué par agent
        self.alpha_RU = 0.1  # Contrainte variation max (10%)

        # CORRECTION B: Bornes absolues RU (stabilisation)
        # Empêchent l'explosion ou l'effondrement du RU
        self.RU_min_absolute = 0.1    # Plancher absolu (sécurité)
        self.RU_max_absolute = 500.0  # Plafond absolu (anti-explosion)

        # Initialisation avec des agents et actifs
        if self.mode_population == "object":
            self._initialize_agents_object(initial_agents)
            # Initialise les âges si démographie activée
            if self.enable_demographics:
                self.agent_ages = self.demographics.initialize_ages(self.agents)
        elif self.mode_population == "vectorized":
            self._initialize_agents_vectorized(initial_agents)
            # En mode vectorisé, les âges sont déjà initialisés dans VectorizedPopulation
        else:
            raise ValueError(f"Mode population inconnu: {self.mode_population}")

        # Initialise quelques entreprises si entreprises dynamiques activées
        if self.enable_dynamic_business and self.entreprise_manager:
            n_entreprises_init = max(5, initial_agents // 20)
            self._initialize_entreprises(n_entreprises_init)

    def _initialize_agents_object(self, n_agents: int) -> None:
        """
        Crée les agents initiaux avec des actifs distribués de manière réaliste (MODE OBJET)

        Cette fonction simule l'Oracle d'initialisation en créant :
        - Des agents avec des identités uniques
        - Des actifs de différents types (immobilier, mobilier, entreprises, etc.)
        - Une distribution log-normale des richesses (réaliste : peu de riches, beaucoup de pauvres)

        Processus :
        1. Pour chaque agent :
           - Génère 1-3 actifs (distribution de Poisson)
           - Chaque actif a une valeur log-normale (réaliste)
           - Chaque actif génère V₀ et D₀ égaux
        2. Les D₀ sont répartis dans le RAD selon le type d'actif

        Args:
            n_agents: Nombre d'agents à créer
        3. Vérification finale : ΣV₀ = ΣD₀
        """
        # NOTE: Ne fixe PAS la graine ici pour permettre des résultats différents
        # Si reproductibilité nécessaire, utiliser --seed en ligne de commande

        for i in range(n_agents):
            # Crée un nouvel agent
            agent = Agent(id=f"agent_{i}")

            # Distribution log-normale des richesses (réaliste)
            # La plupart des agents ont peu d'actifs, quelques-uns en ont beaucoup
            n_assets = np.random.poisson(2) + 1  # 1 à ~5 actifs (moyenne 3)

            for j in range(n_assets):
                # Type d'actif aléatoire (immobilier, mobilier, entreprise, etc.)
                asset_type = np.random.choice(list(AssetType))

                # Valeur réelle log-normale : e^(10 ± 1.5)
                # Produit une distribution réaliste : beaucoup de petits actifs, peu de grands
                real_value = np.random.lognormal(10, 1.5)

                # ÉMISSION CADASTRALE VIA L'ORACLE
                # L'Oracle garantit : unicité NFT, calcul V₀ correct, équilibre V₀=D₀
                auth_factor = np.random.uniform(0.9, 1.0)
                success, nft_metadata, msg = self.oracle.emit_asset(
                    asset_id=f"asset_{i}_{j}",
                    asset_type=asset_type.value,
                    owner_id=agent.id,
                    valeur_estimee=real_value,
                    flux_type=FluxType.OFFICIEL,
                    phi_auth=auth_factor,
                    timestamp=0  # Initialisation au temps 0
                )

                if success:
                    # Crée l'actif avec les valeurs de l'Oracle
                    asset = Asset(
                        id=nft_metadata.asset_id,
                        asset_type=asset_type,
                        real_value=real_value,
                        V_initial=nft_metadata.V_initial,
                        D_initial=nft_metadata.D_initial,
                        owner_id=agent.id,
                        nft_hash=nft_metadata.hash_nft,
                        auth_factor=auth_factor,
                        creation_time=0
                    )

                    # Ajoute l'actif à l'agent (génère V₀)
                    agent.add_asset(asset)
                    # Enregistre l'actif dans le système
                    self.assets[asset.id] = asset

                    # Mise à jour du RAD : distribue D₀ dans la bonne composante
                    # Selon le type d'actif, D₀ va dans une composante sectorielle différente
                    if asset_type == AssetType.IMMOBILIER or asset_type == AssetType.MOBILIER:
                        # Biens physiques → D_materielle
                        self.rad.D_materielle += asset.D_initial
                    elif asset_type == AssetType.SERVICE:
                        # Services → D_services
                        self.rad.D_services += asset.D_initial
                    elif asset_type == AssetType.ENTREPRISE:
                        # Entreprises → D_contractuelle
                        self.rad.D_contractuelle += asset.D_initial
                    else:
                        # Par défaut → D_materielle
                        self.rad.D_materielle += asset.D_initial

            # Enregistre l'agent dans le système
            self.agents[agent.id] = agent

        # === RENORMALISATION GLOBALE DE LA RICHESSE V ===
        # Réajuste tous les V_balance et les actifs pour que le total V corresponde
        # à initial_total_wealth_V (par défaut 1 200 000 V)
        target_total_V = self.initial_total_wealth_V

        # Calculer le V total actuel
        total_V_current = sum(agent.V_balance for agent in self.agents.values())

        if total_V_current > 0:
            scale = target_total_V / total_V_current

            # Appliquer l'échelle à tous les agents et à tous leurs actifs
            for agent in self.agents.values():
                agent.V_balance *= scale
                # Ajuster aussi les actifs pour maintenir la cohérence
                for asset in agent.assets:
                    asset.V_initial *= scale
                    asset.D_initial *= scale

            # Ajuster aussi le RAD pour maintenir l'équilibre V = D
            self.rad.D_materielle *= scale
            self.rad.D_services *= scale
            self.rad.D_contractuelle *= scale

            print(f"INFO: Richesse renormalisée - {total_V_current:.2f} → {target_total_V:.2f} V (facteur: {scale:.4f})")

        # Vérification critique : l'équilibre initial doit être respecté
        self._verify_initial_balance()

    def _verify_initial_balance(self):
        """Vérifie l'équilibre initial : ΣV₀ = ΣD₀"""
        total_V = sum(agent.V_balance for agent in self.agents.values())
        total_D = self.rad.total_D()

        assert abs(total_V - total_D) < 1e-6, \
            f"Déséquilibre initial : V={total_V:.2f}, D={total_D:.2f}"

        print(f"OK: Équilibre initial vérifié : V₀ = D₀ = {total_V:.2f}")

    def _initialize_agents_vectorized(self, n_agents: int) -> None:
        """
        Initialise la population en mode vectorisé (MODE VECTORISÉ)

        Cette méthode crée une VectorizedPopulation avec distributions réalistes :
        - Distribution triangulaire des âges (mode 32 ans, moyenne cible 36 ans)
        - Distribution log-normale des richesses V
        - Renormalisation pour respecter initial_total_wealth_V
        - Initialisation du RAD avec équilibre V = D

        Args:
            n_agents: Nombre d'agents à créer
        """
        from .iris_population_vectorized import VectorizedPopulation

        # Création du générateur aléatoire avec seed si fourni
        rng = np.random.default_rng(self.seed)

        # Création de la population vectorisée avec distribution initiale
        self.population = VectorizedPopulation.from_initial_distribution(
            n_agents=n_agents,
            total_V=self.initial_total_wealth_V,
            rng=rng,
            target_mean_age=36.0  # Âge moyen cible de la population
        )

        # === INITIALISATION DU RAD ===
        # En mode vectorisé, on initialise le RAD avec D total = V total
        # Distribution sectorielle par défaut : 50% matérielle, 30% services, 20% contractuelle
        total_D = self.population.total_V()
        self.rad.D_materielle = total_D * 0.50
        self.rad.D_services = total_D * 0.30
        self.rad.D_contractuelle = total_D * 0.20

        print(f"INFO: Population vectorisée initialisée - {n_agents} agents, V total = {total_D:.2f}")
        print(f"OK: Équilibre initial vérifié : V₀ = D₀ = {total_D:.2f}")

    def _initialize_entreprises(self, n_entreprises: int) -> None:
        """
        Crée des entreprises initiales

        Args:
            n_entreprises: Nombre d'entreprises à créer
        """
        if not self.enable_dynamic_business or not self.entreprise_manager:
            return
        for i in range(n_entreprises):
            # Sélectionne un agent fondateur aléatoire
            if not self.agents:
                break

            agent_id = np.random.choice(list(self.agents.keys()))
            agent = self.agents[agent_id]

            # Capital initial : 20-40% de la richesse de l'agent
            richesse = agent.V_balance + agent.U_balance
            V_initial = richesse * np.random.uniform(0.20, 0.40)


            # Type d'entreprise aléatoire
            business_type = np.random.choice(list(BusinessType))

            # Crée l'entreprise
            business_id = self.entreprise_manager.create_entreprise(
                founder_agent_id=agent_id,
                V_initial=V_initial,
                business_type=business_type,
                cycle=0
            )

            if business_id:
                # Déduit le capital de l'agent
                agent.V_balance -= V_initial

        # Vérifier combien d'entreprises ont été créées
        nb_created = len(self.registre_entreprises.comptes)

    def get_V_on(self) -> float:
        """
        Calcule V_on(t) : valeur "vivante" en circulation

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        V_on représente la valeur RÉELLEMENT EN CIRCULATION dans l'économie,
        c'est-à-dire le patrimoine ACTIF des agents (excluant immobilisations).

        CORRECTION COMPTABLE (v2.1) :
        Les NFT financiers des entreprises représentent du V_operationnel
        des entreprises (créé par combustion), PAS du V des agents.
        Ils ne doivent donc PAS être soustraits de V_on.

        Formule corrigée :
        V_on = ΣV_agents

        V_on est utilisé pour :
        1. Calcul du RU : RU_t = α_RU × V_on(t-1) / N_agents
        2. Thermomètre : θ = D / V_on (tension économique réelle)
        3. Indicateurs RAD : ν_eff, r_ic, etc.

        Note théorique :
        Le V des entreprises (V_operationnel, NFT financiers) est créé par
        combustion (S + U → V) et ne fait pas partie du patrimoine initial
        des agents. Il représente la CRÉATION DE VALEUR par l'activité
        économique, distincte du patrimoine ancré initial (V₀).

        Returns:
            V_on : Valeur vivante en circulation (patrimoine des agents)
        """
        # CALCUL SIMPLE : Somme de tous les V_balance des agents
        # Le patrimoine des agents représente la valeur vivante en circulation
        V_on = sum(agent.V_balance for agent in self.agents.values())

        # Sécurité : V_on ne peut pas être négatif
        # (cela ne devrait jamais arriver avec cette formule simple)
        if V_on < 0:
            print(f"AVERTISSEMENT: V_on négatif détecté ({V_on:.2f}). "
                  f"Cela indique une anomalie grave dans la comptabilité.")
            V_on = max(0.0, V_on)

        return V_on

    def compute_eta(self) -> float:
        """
        Calcule le coefficient η (ETA) de rendement de la combustion S + U → V

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        η est le coefficient de rendement thermodynamique qui module la productivité
        de la combustion (S + U → V) en fonction de la tension économique.

        Objectif : STABILISER le système en modulant la création de V :
        - Surchauffe (θ > 1, I > 0) → η < 1 → FREINE la production de V
        - Sous-régime (θ < 1, I < 0) → η > 1 → STIMULE la production de V
        - Équilibre (θ = 1, I = 0) → η = 1 → Production normale

        FORMULES DISPONIBLES (configurables via rad.eta_formula) :
        1. "linear" : η = 1.0 - α × I (défaut, simple et stable)
        2. "inverse" : η = 1.0 / (1.0 + β × |I|) (atténuation douce)
        3. "offset" : η = 1.0 + γ × (1 - θ) (équivalent à linear)

        INERTIE / SMOOTHING :
        Applique un lissage EMA pour éviter les oscillations brutales :
        η(t+1) = (1 - α_smooth) × η(t) + α_smooth × η_target
        avec α_smooth = rad.eta_smoothing

        Impact dans le système :
        Quand une entreprise génère V par combustion, le V effectif est :
        V_effectif = V_brut × η

        Ce V_effectif est ensuite distribué selon le schéma organique 40/60
        (40% → masse salariale, 60% → trésorerie).

        Returns:
            Coefficient η (bornée dans [eta_min, eta_max])
        """
        # Calcul de l'indicateur I = θ - 1
        theta = self.thermometer()
        indicator = theta - 1.0

        # CALCUL DE LA CIBLE η selon la formule choisie
        if self.rad.eta_formula == "linear":
            # Formule linéaire : η = 1.0 - α × I
            # Diminue quand I > 0 (frein), augmente quand I < 0 (stimulation)
            eta_target = 1.0 - self.rad.eta_alpha * indicator

        elif self.rad.eta_formula == "inverse":
            # Formule inverse : η = 1.0 / (1.0 + β × |I|)
            # Atténuation douce, asymptotique
            eta_target = 1.0 / (1.0 + self.rad.eta_beta * abs(indicator))
            # Ajustement contracyclique : inverse le sens si I < 0
            if indicator < 0:
                eta_target = 2.0 - eta_target  # Miroir autour de 1.0

        elif self.rad.eta_formula == "offset":
            # Formule offset : η = 1.0 + γ × (1 - θ) = 1.0 - γ × I
            # Équivalent à linear mais avec coefficient différent
            eta_target = 1.0 + self.rad.eta_gamma * (1.0 - theta)

        else:
            # Par défaut : formule linéaire
            eta_target = 1.0 - self.rad.eta_alpha * indicator

        # Application des bornes configurables
        eta_target = max(self.rad.eta_min, min(self.rad.eta_max, eta_target))

        # LISSAGE TEMPOREL (EMA) pour éviter oscillations brutales
        # Si c'est le premier calcul, initialise directement
        if len(self.rad.eta_history) == 0:
            eta_smoothed = eta_target
        else:
            # Applique le lissage exponentiel
            eta_prev = self.rad.eta_history[-1] if self.rad.eta_history else 1.0
            smoothing = self.rad.eta_smoothing
            eta_smoothed = (1.0 - smoothing) * eta_prev + smoothing * eta_target

        # Sécurité finale : re-application des bornes après smoothing
        eta_smoothed = max(self.rad.eta_min, min(self.rad.eta_max, eta_smoothed))

        # Enregistrement dans l'historique (pour smoothing et calibration)
        self.rad.eta_history.append(eta_smoothed)
        # Garde seulement les 100 dernières valeurs
        if len(self.rad.eta_history) > 100:
            self.rad.eta_history.pop(0)

        # Mise à jour de rad.eta pour traçabilité
        self.rad.eta = eta_smoothed

        return eta_smoothed

    def thermometer(self) -> float:
        """
        Calcul du thermomètre global : θ = D / V_on

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        Le thermomètre est LA MÉTRIQUE CENTRALE du système IRIS.
        Il mesure la tension thermodynamique de l'économie réelle.

        Formule (conforme à la théorie) :
        θ = D_total / V_on(t)

        Où V_on(t) est la valeur VIVANTE en circulation (excluant immobilisations).
        Cela garantit que θ reflète la tension sur l'économie ACTIVE, pas sur
        des actifs figés (NFT financiers, réserves).

        Interprétation :
        - θ = 1.0 : Équilibre parfait (cible)
        - θ > 1.0 : Excès de demande / pénurie de patrimoine actif
        - θ < 1.0 : Excès d'offre / patrimoine sous-utilisé

        Analogie : θ est comme la température d'un système thermodynamique.
        Le RAD agit comme un thermostat pour maintenir θ proche de 1.

        Note d'implémentation :
        Utilise get_V_on() qui exclut les NFT financiers des entreprises.

        Returns:
            Ratio D/V_on (devrait être proche de 1 en équilibre)
        """
        # Calcule V_on (valeur vivante en circulation, excluant immobilisations)
        V_on = self.get_V_on()

        # Somme de tous les D dans le RAD (miroir thermométrique total)
        total_D = self.rad.total_D()

        # Cas limite : si V_on est presque nul, on retourne 1.0 par défaut
        if V_on < 1e-6:
            return 1.0

        # Calcul du thermomètre : θ = D / V_on (CONFORME À LA THÉORIE)
        return total_D / V_on

    def indicator(self) -> float:
        """
        Indicateur centré : I = θ - 1

        L'indicateur mesure la DÉVIATION par rapport à l'équilibre :
        - I = 0 : Système en équilibre parfait
        - I > 0 : Tension positive (θ > 1), excès de demande
        - I < 0 : Tension négative (θ < 1), excès d'offre

        L'indicateur est utilisé par le RAD pour décider des ajustements.
        Objectif : maintenir |I| < 0.1 (déviation < 10%)

        Returns:
            Déviation du thermomètre par rapport à l'équilibre (0 = équilibre parfait)
        """
        return self.thermometer() - 1.0

    def gini_coefficient(self) -> float:
        """
        Calcul du coefficient de Gini pour mesurer les inégalités

        Le coefficient de Gini mesure la distribution des richesses :
        - 0.0 : Égalité parfaite (tous ont la même richesse)
        - 1.0 : Inégalité maximale (une personne a tout)

        Dans IRIS, le Gini devrait diminuer grâce au revenu universel
        et à la redistribution thermodynamique.

        Formule de Gini :
        G = (2 × Σ(i × w_i)) / (n × Σw_i) - (n+1)/n

        où w_i est la richesse de l'agent i (classé par richesse croissante)

        Returns:
            Coefficient entre 0 (égalité parfaite) et 1 (inégalité maximale)
        """
        # Mode de population
        if self.mode_population == "object":
            # Récupère toutes les richesses (V + U) de chaque agent
            wealths = np.array([agent.total_wealth() for agent in self.agents.values()])
        else:  # vectorized
            # Utilise la méthode optimisée de VectorizedPopulation
            return self.population.gini_coefficient()

        # Trie par richesse croissante (nécessaire pour le calcul de Gini)
        wealths = np.sort(wealths)
        n = len(wealths)

        # Cas limite : richesse totale nulle
        if wealths.sum() < 1e-6:
            return 0.0

        # Calcul du coefficient de Gini
        # cumsum[- 1] = somme totale des richesses
        cumsum = np.cumsum(wealths)

        # Formule de Gini :  2 × Σ(rang × richesse) / (n × total) - (n+1)/n
        return (2 * np.sum((np.arange(1, n+1)) * wealths)) / (n * cumsum[-1]) - (n + 1) / n

    def circulation_rate(self) -> float:
        """
        Taux de circulation : ratio entre U (usage) et V (mémoire)

        Mesure la LIQUIDITÉ du système :
        - Taux faible (U/V petit) : patrimoine immobilisé, peu de transactions
        - Taux élevé (U/V grand) : beaucoup de liquidité, économie active

        Un taux optimal se situe autour de 0.1-0.3 (10-30% de liquidité)

        Returns:
            Ratio U/V mesurant la liquidité du système
        """
        # Total du patrimoine ancré (Verum)
        total_V = sum(agent.V_balance for agent in self.agents.values())
        # Total de la liquidité (Usage)
        total_U = sum(agent.U_balance for agent in self.agents.values())

        # Cas limite : pas de patrimoine ancré
        if total_V < 1e-6:
            return 0.0

        # Calcul du taux de circulation
        return total_U / total_V

    def convert_V_to_U(self, agent_id: str, amount: float) -> bool:
        """
        Conversion de V (mémoire) en U (usage) via le coefficient κ

        C'EST LA FONCTION CLE DU SYSTÈME IRIS !

        Logique économique :
        - V (Verum) = patrimoine ancré, "épargne", mémoire de valeur
        - U (Usage) = liquidité, "argent de poche", monnaie de transaction
        - La conversion V→U "active" le patrimoine pour l'utiliser

        Mécanisme :
        1. L'agent "dépense" une partie de son V
        2. Il reçoit U = V × κ (κ est ajusté par le RAD)
        3. D ne change PAS (le miroir thermométrique reste constant)
        4. θ = D/V AUGMENTE (car V diminue) → signale au RAD
        5. Le RAD détecte et ajuste κ pour ralentir les conversions futures

        Analogie : V→U c'est comme retirer de l'argent d'un compte épargne
        pour le mettre en liquidité. Le RAD observe et ajuste les "frais".

        Impact sur le système :
        - V↓ → θ↑ → RAD détecte → κ↓ → futures conversions plus coûteuses
        - C'est le mécanisme CONTRACYCLIQUE qui stabilise le système

        Args:
            agent_id: Identifiant de l'agent
            amount: Montant de V à convertir en U

        Returns:
            True si la conversion a réussi, False si l'agent n'a pas assez de V
        """
        # Vérifie que l'agent existe et a assez de V
        agent = self.agents.get(agent_id)
        if not agent or agent.V_balance < amount:
            return False  # Conversion impossible

        # ═══════════════════════════════════════════════════════════════════════════
        # κ MODULE ICI LA LIQUIDITÉ (CONVERSION V→U)
        # ═══════════════════════════════════════════════════════════════════════════
        # CONVERSION : U = V × κ
        # κ (kappa) est le coefficient de conversion ajusté par le RAD selon θ
        # • κ = 1.0 en équilibre (θ = 1) → conversion 1:1
        # • κ < 1.0 si θ > 1 (surchauffe) → conversion défavorable, FREINE la liquidité
        # • κ > 1.0 si θ < 1 (sous-régime) → conversion favorable, STIMULE la liquidité
        # C'est le MÉCANISME CONTRACYCLIQUE : κ régule l'accès à la liquidité
        U_amount = amount * self.rad.kappa

        # Débite le V de l'agent
        agent.V_balance -= amount
        # Crédite le U de l'agent
        agent.U_balance += U_amount

        # IMPORTANT : D ne change pas lors de la conversion V→U
        # Pourquoi ? Parce que la valeur totale (V+U) reste la même
        # Seule la FORME change (patrimoine → liquidité)

        # Conséquence : θ = D/V augmente naturellement car V↓
        # Le RAD détectera cette hausse et ajustera κ vers le bas
        # C'est le mécanisme de RÉTROACTION NÉGATIVE qui stabilise

        return True

    def transaction(self, from_id: str, to_id: str, amount: float) -> bool:
        """
        Transaction en U (monnaie d'usage) entre deux agents
        TRANSFERT PUR SANS FRICTION (conforme document IRIS)

        U est une monnaie d'usage pure :
        - Pas de dissipation/friction sur les transactions
        - Transfert intégral du montant
        - D reste inchangé lors des transactions U

        Ancienne version (non-IRIS) :
        - Incluait une dissipation thermodynamique (friction 2%)
        - Réduisait D_regulatrice à chaque transaction
        - Mécanisme artificiel de "refroidissement"

        Nouvelle version (conforme IRIS) :
        - U circule sans friction
        - D n'est réduit que par : amortissement δ_m, CR, burns, catastrophes
        - Le RAD régule via κ et η, pas via friction

        Args:
            from_id: Agent émetteur (qui paye)
            to_id: Agent récepteur (qui reçoit)
            amount: Montant en U à transférer

        Returns:
            True si la transaction a réussi, False sinon
        """
        # Vérifie que les deux agents existent
        from_agent = self.agents.get(from_id)
        to_agent = self.agents.get(to_id)

        # Vérifie que l'émetteur a assez de U
        if not from_agent or not to_agent or from_agent.U_balance < amount:
            return False  # Transaction impossible

        # TRANSFERT PUR : pas de friction, pas de dissipation
        from_agent.U_balance -= amount
        to_agent.U_balance += amount

        # D reste inchangé (pas de modification de D_regulatrice)
        # La régulation se fait via κ, η et l'amortissement global δ_m

        return True

    def distribute_universal_income(self) -> None:
        """
        Distribution du revenu universel basé sur V_on (valeur en circulation)
        AVEC MODULATION κ ET CONTRAINTES DE VARIATION

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        Le RU est calculé à partir de V_on(t-1), la valeur "vivante" en circulation,
        excluant les parts immobilisées (NFT financiers, réserves).

        C'EST LE MÉCANISME DE JUSTICE SOCIALE D'IRIS !

        Formule IRIS avec modulation contracyclique :
        RU_t = κ_t × (V_on(t-1) × τ) / N_agents

        Où :
        - κ_t : Coefficient de liquidité (ajusté par le RAD selon θ)
        - V_on(t-1) : Valeur vivante en circulation au cycle précédent
        - τ : Taux de RU (universal_income_rate, 1% par défaut annuel)
        - N_agents : Nombre d'agents bénéficiaires

        RÔLE CENTRAL DE κ (RÉGULATION CONTRACYCLIQUE) :
        κ module l'injection de liquidité pour maintenir l'équilibre thermodynamique :
        • κ = 1.0 si θ = 1 (équilibre) → RU nominal
        • κ < 1.0 si θ > 1 (surchauffe) → RU réduit, freine l'économie
        • κ > 1.0 si θ < 1 (sous-régime) → RU augmenté, stimule l'économie

        CONTRAINTES DE VARIATION (stabilité) :
        1. Contrainte α_RU : |RU_t - RU_{t-1}| ≤ α_RU × RU_{t-1}
           - Empêche les variations brutales du RU
           - α_RU = 0.1 (10% max de variation par cycle)
        2. Extinction de U non dépensé :
           - U non utilisé est périodiquement détruit
           - Encourage la circulation de la monnaie
           - Période : tous les 12 cycles

        Différence avec les systèmes traditionnels :
        - PAS de création monétaire ex nihilo
        - PAS d'endettement pour financer
        - Redistribution de la valeur dissipée naturellement
        - Basé sur V_on PROUVÉ (pas sur des promesses)
        - Non-accumulabilité de U (extinction périodique)
        - Mécanisme CONTRACYCLIQUE (RU varie avec V_on)

        Impact :
        - Réduit les inégalités (coefficient de Gini ↓)
        - Maintient le pouvoir d'achat de tous
        - Compense la dissipation thermodynamique
        - Crée une boucle de redistribution automatique
        - Stabilise le RU (pas de chocs violents)

        Note d'implémentation :
        Dans la théorie, il existe une symétrie entre la somme des rémunérations
        vivantes (salaires CE) et le RU total. Cette symétrie peut être vérifiée
        en post-traitement mais n'est pas forcée dans cette version du simulateur.
        """
        if len(self.agents) == 0:
            return

        # ÉTAPE 1 : Calcule V_on (valeur vivante en circulation)
        # CONFORME À LA THÉORIE : RU basé sur V_on, pas sur V+U total
        V_on = self.get_V_on()

        # ═══════════════════════════════════════════════════════════════════════════
        # κ MODULE ICI LA LIQUIDITÉ (MONTANT DE RU DISTRIBUÉ)
        # ═══════════════════════════════════════════════════════════════════════════
        # ÉTAPE 2 : Calcule le revenu universel théorique par agent
        # Formule IRIS avec modulation κ : RU = κ × (V_on × τ) / N_agents
        # Où :
        # • V_on : Valeur vivante en circulation
        # • τ : Taux de RU (universal_income_rate = 1% par défaut, annuel)
        # • κ : COEFFICIENT DE LIQUIDITÉ (ajusté par le RAD selon θ)
        # • N_agents : Nombre d'agents
        #
        # RÔLE DE κ DANS LE RU (CONTRACYCLIQUE) :
        # • κ = 1.0 en équilibre (θ = 1) → RU nominal
        # • κ < 1.0 si θ > 1 (surchauffe) → RU réduit, FREINE l'injection de liquidité
        # • κ > 1.0 si θ < 1 (sous-régime) → RU augmenté, STIMULE l'injection de liquidité
        #
        # C'est le MÉCANISME CONTRACYCLIQUE : κ régule l'injection de liquidité via le RU
        # pour maintenir θ proche de 1 (équilibre thermodynamique)
        income_theoretical = self.rad.kappa * V_on * self.universal_income_rate / len(self.agents)

        # ÉTAPE 3 : CONTRAINTE DE VARIATION α_RU
        # |RU_t - RU_{t-1}| ≤ α_RU × RU_{t-1}
        # Limite les variations brutales du RU pour stabilité
        if self.last_RU_per_agent > 0:
            max_variation = self.alpha_RU * self.last_RU_per_agent
            max_RU = self.last_RU_per_agent + max_variation
            min_RU = self.last_RU_per_agent - max_variation

            # Applique la contrainte de variation
            income_per_agent = max(min_RU, min(max_RU, income_theoretical))
        else:
            # Premier RU : pas de contrainte de variation
            income_per_agent = income_theoretical

        # CORRECTION B: BORNES ABSOLUES (anti-explosion / anti-effondrement)
        # Appliquées APRÈS la contrainte de variation pour garantir stabilité absolue
        income_per_agent = max(self.RU_min_absolute, min(self.RU_max_absolute, income_per_agent))

        # ÉTAPE 4 : Distribue le revenu universel à TOUS les agents équitablement
        for agent in self.agents.values():
            agent.U_balance += income_per_agent  # Crédite en liquidité (U)

        # ÉTAPE 5 : Enregistre le RU distribué pour la prochaine fois
        self.last_RU_per_agent = income_per_agent

        # Note sur D_regulatrice :
        # La redistribution RU est thermodynamiquement neutre dans cette version.
        # Dans une version future, on pourrait traquer l'impact sur D_regulatrice
        # pour refléter complètement le mécanisme de la Chambre de Relance.

    def regulate(self) -> tuple[bool, bool]:
        """
        Mécanisme de régulation du RAD (Régulateur Automatique Décentralisé)
        ARCHITECTURE MULTI-COUCHES (Phase C)

        C'EST LE CŒUR DU SYSTÈME IRIS - LE "THERMOSTAT" DE L'ÉCONOMIE !

        Le RAD opère sur TROIS COUCHES complémentaires avec CAPTEURS :

        CAPTEURS (mis à jour à chaque cycle) :
        - r_ic : Taux inflation/contraction (variation θ)
        - ν_eff : Vélocité effective (circulation U/V)
        - τ_eng : Taux engagement (staking D_engagement/D)

        COUCHE 1 (C1) - RÉGULATION CONTINUE (chaque cycle) :
           - Ajuste κ (kappa) : conversion V→U selon θ
           - Ajuste η (eta) : efficacité selon capteurs
           - Réduction cyclique D (borne 0.1041666%)
           - Rétroaction négative instantanée

        COUCHE 2 (C2) - RÉGULATION PROFONDE (tous les T=12 cycles = 1 an) :
           - Activation conditionnelle si |I| > 15%
           - Ajuste τ (dissipation) selon r_ic et ν_eff
           - Recalibre paramètres structurels
           - Permet adaptation long terme

        COUCHE 3 (C3) - REBALANCEMENT D'URGENCE (si |I| > 30%) :
           - Intervention directe sur D_regulatrice
           - Rebalancement thermodynamique progressif
           - Mécanisme de dernier recours
           - Évite divergences critiques
           - HARMONISATION : Limité à C3_max_duration cycles consécutifs (défaut: 5)

        Le système est ENTIÈREMENT AUTOMATIQUE et DÉCENTRALISÉ.
        Aucune décision humaine n'est requise. C'est une cybernétique pure.

        Returns:
            Tuple (C2_activated, C3_activated) pour traçabilité
        """
        # RÉDUCTION CYCLIQUE DE D : 0.1041666% par cycle (borne anti-divergence)
        # Appliqué à toutes les composantes de la dette thermométrique
        # Facteur de réduction : 1 - 0.001041666 = 0.998958334
        D_REDUCTION_FACTOR = 0.998958334
        self.rad.D_materielle *= D_REDUCTION_FACTOR
        self.rad.D_services *= D_REDUCTION_FACTOR
        self.rad.D_contractuelle *= D_REDUCTION_FACTOR
        self.rad.D_engagement *= D_REDUCTION_FACTOR
        self.rad.D_regulatrice *= D_REDUCTION_FACTOR

        # MESURE DES INDICATEURS
        theta = self.thermometer()
        indicator = self.indicator()
        total_U = sum(agent.U_balance for agent in self.agents.values())
        V_on = self.get_V_on()  # Valeur vivante en circulation (CONFORME À LA THÉORIE)

        # MISE À JOUR DES CAPTEURS (avec V_on, pas V total)
        self.rad.update_sensors(theta, total_U, V_on)

        # Flags d'activation des couches (pour traçabilité)
        C2_activated = False
        C3_activated = False

        # ═══════════════════════════════════════════════════════════════════
        # COUCHE 1 (C1) : RÉGULATION CONTINUE
        # ═══════════════════════════════════════════════════════════════════
        # CORRECTION A: SYSTÈME TRI-CAPTEUR (r_t, ν_eff, τ_eng)
        # Calcul des trois capteurs selon THÉORIE §3.3.1
        r_t = theta  # Thermomètre (cible = 1.0)
        nu_eff = self.rad.calculate_nu_eff(total_U, V_on)  # Vélocité (cible = 0.20)
        tau_eng = self.rad.calculate_tau_eng()  # Engagement (cible = 0.35)

        # Ajustement κ (kappa) avec TRI-CAPTEUR
        # Formule : Δκ_t = α_κ×(ν_target-ν) - β_κ×(τ_eng-τ_target) + γ_κ×(1-r)
        self.rad.update_kappa(r_t, nu_eff, tau_eng)

        # Ajustement η (eta) avec TRI-CAPTEUR
        # Formule : Δη_t = α_η×(1-r) + β_η×(ν_target-ν) - γ_η×(τ_eng-τ_target)
        # - Surchauffe (θ > 1) → η diminue → freine production de V
        # - Sous-régime (θ < 1) → η augmente → stimule production de V
        # - Équilibre (θ = 1) → η se stabilise autour de 1
        self.rad.update_eta(r_t, nu_eff, tau_eng)

        # ═══════════════════════════════════════════════════════════════════
        # COUCHE 2 (C2) : RÉGULATION PROFONDE (période T=12 cycles)
        # ═══════════════════════════════════════════════════════════════════
        if self.time % self.rad.T_period == 0:
            # Activation conditionnelle : seulement si |I| > seuil
            if abs(indicator) > self.rad.C2_activation_threshold:
                # C2 ACTIVÉE : système instable, ajustements profonds nécessaires
                C2_activated = True

                # SUPPRIMÉ : Ajustement dissipation_rate (mécanisme non-IRIS)
                # Dans IRIS conforme, il n'y a PAS de friction sur U
                # La régulation se fait UNIQUEMENT via κ, η et δₘ

        # ═══════════════════════════════════════════════════════════════════
        # COUCHE 3 (C3) : REBALANCEMENT D'URGENCE
        # ═══════════════════════════════════════════════════════════════════
        # HARMONISATION : Gestion de la durée d'intervention et cooldown

        # Vérifie si on est en période de cooldown (repos après C3)
        if self.rad.C3_cooldown_counter > 0:
            self.rad.C3_cooldown_counter -= 1
            # Pendant le cooldown, on ne peut pas réactiver C3
            # mais on peut sortir de crise si l'indicateur se normalise
            if abs(indicator) <= self.rad.C3_activation_threshold:
                # Crise résolue pendant le cooldown : réinitialise tout
                self.rad.C3_crisis_counter = 0
                self.rad.C3_cooldown_counter = 0

        # Vérifie si la crise nécessite intervention C3
        elif abs(indicator) > self.rad.C3_activation_threshold:
            # Crise détectée : vérifie si on peut encore intervenir
            if self.rad.C3_crisis_counter < self.rad.C3_max_duration:
                # C3 ACTIVÉE : crise systémique, intervention directe sur D
                C3_activated = True
                self.rad.C3_crisis_counter += 1

                # Utilise V_on (valeur vivante) pour le rebalancement (CONFORME À LA THÉORIE)
                # V_on déjà calculé plus haut

                # La cible est D = V_on pour avoir θ = D/V_on = 1
                target_D = V_on
                current_D = self.rad.total_D()

                # Calcule l'ajustement nécessaire (progressif : 10% par cycle)
                # On ne corrige pas d'un coup pour éviter les chocs brutaux
                adjustment = (target_D - current_D) * 0.1

                # Applique l'ajustement sur D_regulatrice (chambre de relance)
                # C'est la composante "flexible" de D, utilisée pour la régulation
                self.rad.D_regulatrice += adjustment
            else:
                # Durée maximale atteinte : entre en cooldown
                # Cooldown = même durée que l'intervention (self.rad.C3_max_duration cycles)
                self.rad.C3_cooldown_counter = self.rad.C3_max_duration
                self.rad.C3_crisis_counter = 0  # Reset pour la prochaine crise
        else:
            # Pas de crise : réinitialise le compteur
            if self.rad.C3_crisis_counter > 0:
                self.rad.C3_crisis_counter = 0

        # ═══════════════════════════════════════════════════════════════════
        # CALIBRATION AUTOMATIQUE (optionnelle, périodique)
        # ═══════════════════════════════════════════════════════════════════
        # Ajuste automatiquement les paramètres de sensibilité (alpha, beta)
        # pour stabiliser le système selon les oscillations observées de θ
        calibration_adjustments = self.rad.auto_calibrate(self.time)

        # Affiche les ajustements si significatifs
        if calibration_adjustments and 'status' not in calibration_adjustments:
            print(f"[CALIBRATION AUTO t={self.time}] Ajustements: "
                  f"η_α={calibration_adjustments.get('eta_alpha', 0.0):+.4f}, "
                  f"κ_β={calibration_adjustments.get('kappa_beta', 0.0):+.4f}, "
                  f"θ_std={calibration_adjustments.get('theta_std', 0.0):.4f}")

        return (C2_activated, C3_activated)

    def reconvert_U_to_V(self, agent_id: str, amount: float) -> bool:
        """
        Reconversion de U (usage) en V (épargne/investissement)
        Permet aux agents de "cristalliser" leur liquidité en actifs

        AMÉLIORATION v2.1 :
        Utilise le coefficient κ (kappa) pour la conversion INVERSE V←U
        Principe MIROIR de convert_V_to_U :

        - V→U : U = V × κ
        - U→V : V = U / κ (conversion inverse)

        Logique thermodynamique :
        - Si κ < 1 (surchauffe, θ > 1) :
          → V→U coûteux (peu de U obtenu)
          → U→V avantageux (beaucoup de V obtenu)
          → Encourage l'épargne, décourage la liquidation

        - Si κ > 1 (sous-régime, θ < 1) :
          → V→U facile (beaucoup de U obtenu)
          → U→V coûteux (peu de V obtenu)
          → Encourage la liquidation, décourage l'épargne

        Ce mécanisme CONTRACYCLIQUE aide à stabiliser le système.

        Args:
            agent_id: Identifiant de l'agent
            amount: Montant de U à reconvertir

        Returns:
            True si la conversion a réussi
        """
        agent = self.agents.get(agent_id)
        if not agent or agent.U_balance < amount:
            return False

        # RECONVERSION THERMODYNAMIQUE : U → V via coefficient κ
        # V = U / κ (conversion inverse miroir de V→U)
        # Sécurité : éviter division par zéro (ne devrait jamais arriver)
        kappa = max(0.5, self.rad.kappa)  # Plancher de sécurité
        V_amount = amount / kappa

        # Débite le U de l'agent
        agent.U_balance -= amount
        # Crédite le V de l'agent (selon κ)
        agent.V_balance += V_amount

        # Ajustement de D pour maintenir l'équilibre thermodynamique
        # Quand on cristallise U en V, on crée de la dette matérielle
        # (car on transforme liquidité en patrimoine ancré)
        self.rad.D_materielle += V_amount

        return True

    def step(self, n_transactions: int = 10) -> None:
        """
        Avance la simulation d'un pas de temps

        ÉCHELLE TEMPORELLE : 1 step = 1 mois
        Les mécanismes à fréquence annuelle sont déclenchés tous les STEPS_PER_YEAR = 12 steps

        Args:
            n_transactions: Nombre de transactions à simuler
        """
        self.time += 1

        # Variables de suivi démographique pour cette étape
        births_this_step = 0
        deaths_this_step = 0
        catastrophes_this_step = 0

        # 0a. Vieillissement de la population (tous les 12 steps = 1 fois/an)
        if self.enable_demographics and self.time % STEPS_PER_YEAR == 0:
            if self.mode_population == "object":
                self.agent_ages = self.demographics.age_population(self.agent_ages)
            # En mode vectorisé, le vieillissement est géré dans process_vectorized()

        # 0b. Catastrophes aléatoires (déclenchement potentiel chaque step, probabilité annuelle)
        if self.enable_catastrophes and self.time % STEPS_PER_YEAR == 0:
            new_events = self.catastrophe_manager.update(
                self.time, self.agents, self.agent_ages, self
            )
            catastrophes_this_step = len(new_events)

        # === TRANSACTIONS ÉCONOMIQUES ===
        # En mode objet : transactions individuelles
        # En mode vectorisé : opérations vectorielles
        if self.mode_population == "object":
            agent_ids = list(self.agents.keys())
            if not agent_ids:  # Sécurité : arrête si plus d'agents
                return

            # 1. Conversions V -> U aléatoires (agents activent leur patrimoine)
            # CORRECTION : Réduit la fréquence et le montant pour éviter vidange de V
            for _ in range(max(1, n_transactions // 10)):  # Beaucoup moins de conversions
                agent_id = np.random.choice(agent_ids)
                agent = self.agents[agent_id]

                # Seulement si l'agent a besoin de liquidité (U faible)
                if agent.V_balance > 0 and agent.U_balance < agent.V_balance * 0.1:
                    # Conversion modérée : 2% du V au lieu de 10%
                    convert_amount = agent.V_balance * 0.02
                    self.convert_V_to_U(agent_id, convert_amount)

            # 2. Reconversions U -> V (épargne/investissement)
            for _ in range(max(1, n_transactions // 10)):
                agent_id = np.random.choice(agent_ids)
                agent = self.agents[agent_id]

                # Épargne si l'agent a beaucoup de liquidité
                if agent.U_balance > agent.V_balance * 0.2:
                    save_amount = agent.U_balance * 0.05
                    self.reconvert_U_to_V(agent_id, save_amount)

            # 3. Transactions U entre agents
            for _ in range(n_transactions):
                agent_ids = list(self.agents.keys())
                if len(agent_ids) < 2:
                    break
                from_id = np.random.choice(agent_ids)
                to_id = np.random.choice(agent_ids)
                if from_id != to_id:
                    from_agent = self.agents[from_id]
                    if from_agent.U_balance > 1.0:  # Seuil minimum
                        amount = min(from_agent.U_balance * 0.1, from_agent.U_balance * 0.5)
                        self.transaction(from_id, to_id, amount)

            # 4. Distribution du revenu universel (tous les 12 steps = 1 fois/an)
            if self.time % STEPS_PER_YEAR == 0:
                self.distribute_universal_income()

        elif self.mode_population == "vectorized":
            # === MODE VECTORISÉ : opérations économiques par arrays ===
            if self.population.total_population() == 0:
                return

            alive = self.population.is_alive

            # 1. Conversions V -> U (agents avec peu de U activent leur patrimoine)
            needs_liquidity = (self.population.V > 0) & (self.population.U < self.population.V * 0.1) & alive
            convert_amount = self.population.V[needs_liquidity] * 0.02
            self.population.V[needs_liquidity] -= convert_amount
            self.population.U[needs_liquidity] += convert_amount

            # 2. Reconversions U -> V (épargne si beaucoup de liquidité)
            has_liquidity = (self.population.U > self.population.V * 0.2) & alive
            save_amount_U = self.population.U[has_liquidity] * 0.05

            # CORRECTION THERMODYNAMIQUE: U→V doit créer D_materielle (conservation)
            # Formule: V = U / κ (comme dans reconvert_U_to_V)
            kappa = max(0.5, self.rad.kappa)
            save_amount_V = save_amount_U / kappa

            self.population.U[has_liquidity] -= save_amount_U
            self.population.V[has_liquidity] += save_amount_V

            # CRÉATION DE D_materielle pour maintenir l'équilibre thermodynamique
            # Quand on cristallise U en V, on crée de la dette matérielle
            total_V_created = np.sum(save_amount_V)
            self.rad.D_materielle += total_V_created

            # 3. Transactions U entre agents (vectorisé via random_transfers_U)
            # Utilise la méthode optimisée de VectorizedPopulation
            rng = np.random.default_rng(self.seed + self.time if self.seed is not None else None)
            self.population.random_transfers_U(
                rng=rng,
                n_transfers=n_transactions * 10,
                max_fraction=0.1
            )

            # 4. Distribution du revenu universel (tous les 12 steps = 1 fois/an)
            if self.time % STEPS_PER_YEAR == 0:
                # Applique le revenu universel à tous les agents vivants
                ru_amount = self.universal_income_rate * self.population.total_V() / max(1, self.population.total_population())
                self.population.apply_universal_income(ru_amount)

            # Mise à jour de la richesse
            self.population.update_wealth()

        # 4a. COMBUSTION entreprises : S + U → V, puis distribution ORGANIQUE 40/60 (chaque step = 1 fois/mois)
        # ALIGNEMENT THÉORIQUE : 40% → masse salariale, 60% → trésorerie
        # NOUVEAU : Application du coefficient η (ETA) de rendement
        # CONDITIONNÉ PAR enable_business_combustion
        business_masse_salariale_total = 0.0
        business_NFT_created_count = 0

        if self.enable_business_combustion:
            # ═════════════════════════════════════════════════════════════════════
            # CORRECTION D+E : VRAIE COMBUSTION S+U→V avec bornes (THÉORIE §2.3.2.6)
            # ═════════════════════════════════════════════════════════════════════
            # CHANGEMENT MAJEUR par rapport à l'ancien code:
            # 1. DESTRUCTION effective de S et U (conservation énergétique)
            # 2. CRÉATION de V = η × E_t avec E_t = w_S×S_burn + w_U×U_burn
            # 3. PLAFOND V_max basé sur la population (CORRECTION D+G)
            # 4. CRÉATION de D à 100% (CORRECTION E, conservation thermodynamique)

            eta = self.rad.eta  # Coefficient de rendement (déjà mis à jour par regulate())

            # CORRECTION D+G: V_max proportionnel à N_agents
            # Empêche V d'exploser indéfiniment
            V_max_per_agent = 10000.0  # V maximum par agent (ajustable)
            V_max_total = len(self.agents) * V_max_per_agent

            # V total actuel (pour vérifier le plafond)
            V_total_actuel = sum(a.V_balance for a in self.agents.values())

            # Simule la VRAIE COMBUSTION (S + U → V) pour les entreprises
            nb_enterprises = len(self.registre_entreprises.comptes)

            # WORKAROUND: Injection continue de S et U pour simuler l'activité économique
            # TODO: Remplacer par de vraies transactions agent→entreprise
            # Pour chaque entreprise, on injecte mensuellement une fraction du V_entreprise
            injection_rate = 0.04  # 4% du capital par mois en S+U (doublé pour plus de combustion)
            for compte in self.registre_entreprises.comptes.values():
                V_entreprise = compte.V_entreprise
                injection_S = V_entreprise * injection_rate * 0.6  # 60% en S
                injection_U = V_entreprise * injection_rate * 0.4  # 40% en U
                compte.S_balance += injection_S
                compte.U_operationnel += injection_U

            for business_id in list(self.registre_entreprises.comptes.keys()):
                compte = self.registre_entreprises.get_compte(business_id)
                if compte:
                    # VRAIE COMBUSTION: on DÉTRUIT S et U pour CRÉER V
                    # Pas de génération ex nihilo comme avant !

                    # Stipulat (S) et Liquidité (U) disponibles
                    S_disponible = getattr(compte, 'S_balance', 0.0)
                    U_disponible = getattr(compte, 'U_operationnel', 0.0)

                    # Taux de combustion mensuel : 5% de min(S, U)
                    burn_rate = 0.05
                    combustible = min(S_disponible, U_disponible)

                    # Quantités brûlées (pondération 60% S, 40% U)
                    S_burn = combustible * 0.6
                    U_burn = combustible * 0.4

                    # DESTRUCTION de S et U (CONSERVATION ÉNERGÉTIQUE)
                    if hasattr(compte, 'S_balance'):
                        compte.S_balance -= S_burn
                    if hasattr(compte, 'U_operationnel'):
                        compte.U_operationnel -= U_burn

                    # CRÉATION de V selon FORMULE THÉORIQUE (§2.3.2.6):
                    # ΔV_t = η_t × Δt × E_t
                    # avec E_t = w_S × S_burn + w_U × U_burn
                    E_t = 0.6 * S_burn + 0.4 * U_burn
                    V_genere_brut = eta * E_t

                    # CORRECTION D: PLAFOND V_max_total
                    # Si V_total + V_genere > V_max, on limite la génération
                    if V_total_actuel + V_genere_brut > V_max_total:
                        V_genere_brut = max(0.0, V_max_total - V_total_actuel)

                    # Distribution ORGANIQUE 40/60
                    # 40% → masse salariale (en U)
                    # 60% → trésorerie (en V_operationnel)
                    masse_salariale_U = V_genere_brut * 0.4
                    V_operationnel = V_genere_brut * 0.6

                    # Crédite la trésorerie de l'entreprise
                    if hasattr(compte, 'V_operationnel'):
                        compte.V_operationnel += V_operationnel
                    else:
                        compte.V_entreprise += V_operationnel

                    business_masse_salariale_total += masse_salariale_U
                    V_total_actuel += V_genere_brut  # Met à jour le total pour le prochain

                    # CORRECTION E (FIX v2): CRÉER D sur 100% de la valeur générée
                    # PRINCIPE THERMODYNAMIQUE CORRECT:
                    # - V_genere_brut représente la VALEUR TOTALE créée (patrimoine + salaires)
                    # - V_operationnel (60%) → patrimoine entreprise → entre directement dans V_on
                    # - masse_salariale_U (40%) → salaires agents → se transforme en V_agents via transactions → entre dans V_on
                    # - Les DEUX finissent dans V_on au fil du temps
                    # → On DOIT créer D sur 100% de V_genere_brut, pas seulement 60%
                    # ANCIEN (bug v1): D_contractuelle += V_operationnel (60%) → D croissait trop lentement
                    # NOUVEAU (correct v2): D_contractuelle += V_genere_brut (100%)
                    self.rad.D_contractuelle += V_genere_brut * 1.0  # 100% de la valeur créée

            # Distribution de la masse salariale des entreprises (en U)
            # IMPORTANT : Ce sont des SALAIRES (revenus productifs), pas du RU.
            # Dans cette version simplifiée, on redistribue aux agents comme proxy.
            if business_masse_salariale_total > 0 and len(self.agents) > 0:
                montant_U_par_agent = business_masse_salariale_total / len(self.agents)
                for agent in self.agents.values():
                    agent.U_balance += montant_U_par_agent

        # 4b. Redistribution Chambre de Relance (tous les 12 steps = 1 fois/an)
        # CONDITIONNÉ PAR enable_chambre_relance
        if self.enable_chambre_relance and self.time % STEPS_PER_YEAR == 0 and len(self.agents) > 0:
            montant_RU_CR, delta_D_CR, invest, gov = self.chambre_relance.redistribute_pool(
                cycle=self.time,
                nb_beneficiaires_RU=len(self.agents),
                timestamp=self.time
            )
            # Distribution du RU provenant de la Chambre de Relance
            for agent in self.agents.values():
                agent.U_balance += montant_RU_CR

            # CORRECTION F: Réduction de D global (impact déflationniste de la CR)
            # La Chambre de Relance réduit TOUTES les composantes de D proportionnellement
            # (pas seulement D_regulatrice), pour refléter la liquidation thermodynamique
            if delta_D_CR < 0:
                total_D_before_CR = self.rad.total_D()
                if total_D_before_CR > 0:
                    # Calcul du ratio de réduction : (D - |delta_D_CR|) / D
                    reduction_amount = abs(delta_D_CR)
                    ratio_CR = max(0.0, (total_D_before_CR - reduction_amount) / total_D_before_CR)

                    # Application proportionnelle sur TOUTES les composantes de D
                    self.rad.D_materielle *= ratio_CR
                    self.rad.D_services *= ratio_CR
                    self.rad.D_contractuelle *= ratio_CR
                    self.rad.D_engagement *= ratio_CR
                    self.rad.D_regulatrice *= ratio_CR

        # 5. Régulation automatique
        C2_activated, C3_activated = self.regulate()

        # 5b. Amortissement global de la dette thermométrique D (conforme IRIS)
        # Document IRIS impose : δ_m = 0.001041666 par mois ≈ 0.104%/mois ≈ 1.25%/an
        # Appliqué à chaque step (1 step = 1 mois)
        total_D_before = self.rad.total_D()
        if total_D_before > 0:
            # Amortissement mensuel : δ_m = 0.104%/mois
            effective_delta = self.rad.delta_m

            # Calcul de l'amortissement
            amort = effective_delta * total_D_before
            ratio = (total_D_before - amort) / total_D_before

            # Application proportionnelle sur toutes les composantes de D
            self.rad.D_materielle *= ratio
            self.rad.D_services *= ratio
            self.rad.D_contractuelle *= ratio
            self.rad.D_engagement *= ratio
            self.rad.D_regulatrice *= ratio

        # Initialize demographic tracking variables
        D_lifetime_this_step = 0.0
        births_this_step = 0
        deaths_this_step = 0

        # 6. Démographie : décès et naissances (tous les 12 steps = 1 fois/an)
        if self.enable_demographics and self.time % STEPS_PER_YEAR == 0:
            if self.mode_population == "object":
                # === MODE OBJET : traitement individuel des agents ===
                # 6a. Accumulation annuelle des biens de consommation
                consumption_per_year = getattr(self.demographics, "consumption_D_per_year", 0.0)
                if consumption_per_year > 0:
                    for agent in self.agents.values():
                        agent.consumables += consumption_per_year

                # 6b. Traitement des décès
                deceased_ids = self.demographics.process_deaths(
                    self.agents, self.agent_ages, self.time
                )
                deaths_this_step = len(deceased_ids)

                # 6c. Héritage et suppression des agents décédés
                for deceased_id in deceased_ids:
                    if deceased_id in self.agents:
                        deceased_agent = self.agents[deceased_id]

                        # NEW : D de consommation de toute la vie de l'agent
                        age_at_death = self.agent_ages.get(
                            deceased_id,
                            self.demographics.life_expectancy
                        )
                        D_life = age_at_death * getattr(
                            self.demographics,
                            "consumption_D_per_year",
                            0.0
                        )

                        if D_life > 0:
                            # On considère la consommation comme un flux de services
                            self.rad.D_services += D_life
                            D_lifetime_this_step += D_life

                        # Transfert du patrimoine à un héritier OU à la Chambre de Relance
                        if len(self.agents) > 1:
                            heir_id = self.demographics.inherit_wealth(
                                deceased_id, self.agents, self.agent_ages
                            )
                            # Note: inherit_wealth gère déjà le transfert V+U
                        else:
                            # Dernier agent : tous les actifs vont à la Chambre de Relance
                            heir_id = None

                        # Si pas d'héritier OU si l'agent a des actifs non transférés,
                        # envoyer les actifs orphelins à la Chambre de Relance
                        if heir_id is None or len(deceased_agent.assets) > 0:
                            for asset in deceased_agent.assets:
                                self.chambre_relance.add_orphan_asset(
                                    asset_id=asset.id,
                                    asset_type=asset.asset_type.value,
                                    V_initial=asset.V_initial,
                                    D_initial=asset.D_initial,
                                    reason=OrphanReason.DECES_SANS_HERITIER,
                                    timestamp_orphelin=self.time,
                                    age_asset=self.time - asset.creation_time,
                                    etat_physique=1.0  # Par défaut
                                )

                        # Envoyer les biens de consommation accumulés à la Chambre de Relance
                        if deceased_agent.consumables > 0:
                            self.chambre_relance.add_orphan_asset(
                                asset_id=f"consumables_{deceased_id}_{self.time}",
                                asset_type="service",  # Les consumables sont des biens de consommation/services
                                V_initial=deceased_agent.consumables,
                                D_initial=deceased_agent.consumables,
                                reason=OrphanReason.DECES_SANS_HERITIER,
                                timestamp_orphelin=self.time,
                                age_asset=age_at_death,
                                etat_physique=1.0  # Biens de consommation "neufs"
                            )

                        # Suppression de l'agent décédé
                        del self.agents[deceased_id]
                        if deceased_id in self.agent_ages:
                            del self.agent_ages[deceased_id]

                # 6d. Traitement des naissances
                new_agents = self.demographics.process_births(
                    self.agents, self.agent_ages, self.assets, self.time
                )
                births_this_step = len(new_agents)

                # Ajout des nouveaux agents au système
                for new_agent in new_agents:
                    self.agents[new_agent.id] = new_agent
                    self.agent_ages[new_agent.id] = 0  # Les nouveau-nés ont 0 ans

                    # CORRECTION CRITIQUE: Créer D pour les actifs des nouveau-nés
                    # Conservation thermodynamique: V₀ = D₀ pour chaque actif
                    for asset in new_agent.assets:
                        asset_type = asset.asset_type
                        if asset_type == AssetType.IMMOBILIER or asset_type == AssetType.MOBILIER:
                            self.rad.D_materielle += asset.D_initial
                        elif asset_type == AssetType.SERVICE:
                            self.rad.D_services += asset.D_initial
                        elif asset_type == AssetType.ENTREPRISE:
                            self.rad.D_contractuelle += asset.D_initial
                        else:
                            self.rad.D_materielle += asset.D_initial

                # CORRECTION G: Vérification V_max après naissances (cohérence démographique)
                # Les nouveau-nés créent de nouveaux actifs, ce qui augmente V total
                # On doit s'assurer que V_total ne dépasse pas V_max_total
                if new_agents:
                    V_max_per_agent = 10000.0
                    V_max_total = len(self.agents) * V_max_per_agent
                    V_total_actuel = sum(a.V_balance for a in self.agents.values())

                    # Si V dépasse le plafond, réduire proportionnellement les balances des nouveau-nés
                    if V_total_actuel > V_max_total:
                        excess_V = V_total_actuel - V_max_total
                        newborn_V_total = sum(a.V_balance for a in new_agents)

                        if newborn_V_total > 0:
                            # Réduction proportionnelle du patrimoine des nouveau-nés
                            reduction_ratio = max(0.0, (newborn_V_total - excess_V) / newborn_V_total)
                            for new_agent in new_agents:
                                new_agent.V_balance *= reduction_ratio

            elif self.mode_population == "vectorized":
                # === MODE VECTORISÉ : traitement par arrays NumPy ===
                # Toute la démographie (vieillissement, morts, naissances) en une seule passe
                rng = np.random.default_rng(self.seed if hasattr(self, 'seed') else None)
                births_this_step, deaths_this_step = self.demographics.process_vectorized(
                    self.population, self.time, rng
                )

                # En mode vectorisé, pas de D_lifetime détaillé (approximation)
                D_lifetime_this_step = deaths_this_step * self.demographics.life_expectancy * \
                                      getattr(self.demographics, "consumption_D_per_year", 0.0)
                if D_lifetime_this_step > 0:
                    self.rad.D_services += D_lifetime_this_step

        # 6b. Mise à jour des prix (si price_discovery activé)
        if self.enable_price_discovery and self.price_manager:
            # Appeler price_manager.step() avec signals
            self.price_manager.step({
                "theta": self.thermometer(),
                "shock": 0.0,  # TODO: ajouter choc de catastrophes si nécessaire
                "noise_amplitude": 0.01,
                "drift_coeff": 0.02
            })

        # 7. Enregistrement des métriques
        self._record_metrics(births_this_step, deaths_this_step, catastrophes_this_step,
                            business_masse_salariale=business_masse_salariale_total,
                            business_NFT=business_NFT_created_count,
                            C2_activated=C2_activated,
                            C3_activated=C3_activated,
                            D_lifetime=D_lifetime_this_step,
                            creations_entreprises=0,
                            faillites_entreprises=0)

    def _simulate_price_based_transactions(self, n_transactions: int) -> None:
        """
        Simule des transactions basées sur les prix explicites

        Args:
            n_transactions: Nombre de transactions
        """
        if not self.enable_price_discovery or not self.price_manager:
            return

        agent_ids = list(self.agents.keys())
        if len(agent_ids) < 2:
            return

        for _ in range(n_transactions):
            # Sélectionne acheteur et vendeur
            buyer_id = np.random.choice(agent_ids)
            seller_id = np.random.choice(agent_ids)

            if buyer_id == seller_id:
                continue

            buyer = self.agents[buyer_id]
            seller = self.agents[seller_id]

            # Type de bien échangé
            good_type = np.random.choice(list(GoodType))

            # Quantité aléatoire
            quantite = np.random.uniform(0.5, 5.0)

            # Prix actuel
            prix = self.price_manager.get_prix(good_type)

            # Montant total
            montant_total = prix * quantite

            # Transaction si l'acheteur a assez de U
            if buyer.U_balance >= montant_total:
                # Enregistre dans le marché
                self.price_manager.transact(good_type, quantite, is_achat=True)

                # Transaction en U (pure, sans friction)
                self.transaction(buyer_id, seller_id, montant_total)

    def _simulate_classic_transactions(self, n_transactions: int) -> None:
        """
        Simule des transactions classiques (sans prix)

        Args:
            n_transactions: Nombre de transactions
        """
        agent_ids = list(self.agents.keys())

        # Conversions V→U
        for _ in range(max(1, n_transactions // 10)):
            if not agent_ids:
                break
            agent_id = np.random.choice(agent_ids)
            agent = self.agents[agent_id]

            if agent.V_balance > 0 and agent.U_balance < agent.V_balance * 0.1:
                convert_amount = agent.V_balance * 0.02
                self.convert_V_to_U(agent_id, convert_amount)

        # Reconversions U→V
        for _ in range(max(1, n_transactions // 10)):
            if not agent_ids:
                break
            agent_id = np.random.choice(agent_ids)
            agent = self.agents[agent_id]

            if agent.U_balance > agent.V_balance * 0.2:
                save_amount = agent.U_balance * 0.05
                self.reconvert_U_to_V(agent_id, save_amount)

        # Transactions U
        for _ in range(n_transactions):
            if len(agent_ids) < 2:
                break
            from_id = np.random.choice(agent_ids)
            to_id = np.random.choice(agent_ids)
            if from_id != to_id:
                from_agent = self.agents[from_id]
                if from_agent.U_balance > 1.0:
                    amount = min(from_agent.U_balance * 0.1, from_agent.U_balance * 0.5)
                    self.transaction(from_id, to_id, amount)

    def _record_metrics(self, births: int = 0, deaths: int = 0, catastrophes: int = 0,
                       business_masse_salariale: float = 0.0, business_NFT: int = 0,
                       C2_activated: bool = False, C3_activated: bool = False,
                       D_lifetime: float = 0.0,
                       creations_entreprises: int = 0,
                       faillites_entreprises: int = 0) -> None:
        """
        Enregistre les métriques du système pour analyse (version unifiée v2.1)

        ALIGNEMENT THÉORIQUE :
        Distingue clairement RU (basé sur V_on) et masse salariale (40% organique).
        Trace les activations des couches RAD (C2, C3) pour analyse de régulation.
        Enregistre les métriques v2.1 (prix, inflation, entreprises).

        Args:
            births: Nombre de naissances à cet instant
            deaths: Nombre de décès à cet instant
            catastrophes: Nombre de catastrophes à cet instant
            business_masse_salariale: Masse salariale des entreprises (40% organique)
            business_NFT: Nombre de NFT financiers créés
            C2_activated: Activation de la couche C2 (régulation profonde)
            C3_activated: Activation de la couche C3 (rebalancement d'urgence)
            D_lifetime: D de consommation versée au RAD au décès des agents
        """
        self.history['time'].append(self.time)
        self.history['total_V'].append(sum(a.V_balance for a in self.agents.values()))
        self.history['total_U'].append(sum(a.U_balance for a in self.agents.values()))
        self.history['total_D'].append(self.rad.total_D())
        self.history['thermometer'].append(self.thermometer())
        self.history['indicator'].append(self.indicator())
        self.history['kappa'].append(self.rad.kappa)  # Coefficient de conversion V→U
        self.history['eta'].append(self.rad.eta)  # Coefficient de rendement combustion S+U→V
        self.history['gini_coefficient'].append(self.gini_coefficient())
        self.history['circulation_rate'].append(self.circulation_rate())

        # Métriques démographiques
        self.history['population'].append(len(self.agents))
        if self.enable_demographics and self.agent_ages:
            avg_age = sum(self.agent_ages.values()) / len(self.agent_ages)
            self.history['avg_age'].append(avg_age)
        else:
            self.history['avg_age'].append(0)

        self.history['births'].append(births)
        self.history['deaths'].append(deaths)
        self.history['catastrophes'].append(catastrophes)
        self.history['RU_distribue'].append(self.last_RU_per_agent)

        # Métriques entreprises (ALIGNEMENT THÉORIQUE)
        self.history['business_masse_salariale'].append(business_masse_salariale)
        self.history['business_NFT_created'].append(business_NFT)

        # Métriques activation RAD (harmonisation C1, C2, C3)
        self.history['C2_activated'].append(1 if C2_activated else 0)
        self.history['C3_activated'].append(1 if C3_activated else 0)
        self.history['C3_crisis_duration'].append(self.rad.C3_crisis_counter)

        # Métrique D de consommation de vie
        self.history['D_lifetime'].append(D_lifetime)

        # Métriques v2.1 supplémentaires
        if self.enable_price_discovery and self.price_manager:
            # Prix moyen pondéré (nouvelle API log-prices)
            mean_price = self.price_manager.mean_price()
            self.history['prix_moyen'].append(mean_price)

            # Inflation (variation prix moyen depuis cycle précédent)
            prev_mean_price = self.history['prix_moyen'][-2] if len(self.history['prix_moyen']) >= 2 else mean_price
            inflation = self.price_manager.inflation(prev_mean_price)
            self.history['inflation'].append(inflation)
        else:
            self.history['prix_moyen'].append(0.0)
            self.history['inflation'].append(0.0)

        # Entreprises
        if self.enable_dynamic_business and self.entreprise_manager:
            nb_entreprises = len(self.entreprise_manager.entreprises_actives)
            self.history['nb_entreprises'].append(nb_entreprises)
            self.history['creations_entreprises'].append(creations_entreprises)
            self.history['faillites_entreprises'].append(faillites_entreprises)
        else:
            nb_entreprises = len(self.registre_entreprises.comptes)
            self.history['nb_entreprises'].append(nb_entreprises)
            self.history['creations_entreprises'].append(0)
            self.history['faillites_entreprises'].append(0)

    def simulate(self, steps: int = 1000, n_transactions: int = 10) -> None:
        """
        Exécute la simulation sur plusieurs pas de temps

        Args:
            steps: Nombre de pas de simulation
            n_transactions: Transactions par pas
        """
        print(f"\nDémarrage de la simulation IRIS ({steps} pas)...")

        for i in range(steps):
            self.step(n_transactions)

            if (i + 1) % 100 == 0:
                theta = self.thermometer()
                indicator = self.indicator()
                gini = self.gini_coefficient()
                print(f"  Pas {i+1}/{steps} - θ={theta:.4f}, I={indicator:.4f}, Gini={gini:.4f}")

        print("OK: Simulation terminée\n")

    def inject_shock(self, shock_type: str, magnitude: float) -> None:
        """
        Injecte un choc économique pour tester la résilience

        Args:
            shock_type: Type de choc ('wealth_loss', 'demand_surge', 'supply_shock')
            magnitude: Intensité du choc (0-1)
        """
        print(f"\nATTENTION: Injection d'un choc : {shock_type} (magnitude={magnitude:.2f})")

        if shock_type == 'wealth_loss':
            # Destruction d'une partie du patrimoine (catastrophe naturelle, etc.)
            for agent in self.agents.values():
                loss = agent.V_balance * magnitude
                agent.V_balance -= loss
                # Réduction correspondante de D
                self.rad.D_materielle -= loss

        elif shock_type == 'demand_surge':
            # Augmentation soudaine de la demande (conversion massive V -> U)
            for agent in self.agents.values():
                if agent.V_balance > 0:
                    convert = agent.V_balance * magnitude
                    self.convert_V_to_U(agent.id, convert)

        elif shock_type == 'supply_shock':
            # Choc d'offre : réduction temporaire de la production/combustion
            # Note : Dans une version complète, ceci affecterait les taux de production
            # Pour cette simulation simplifiée, on réduit légèrement η temporairement
            # (ce qui sera recalibré par le RAD au prochain cycle)
            self.rad.eta = max(self.rad.eta_min, self.rad.eta * (1 - magnitude * 0.5))

        print(f"  Thermomètre après choc : {self.thermometer():.4f}")
        print(f"  Indicateur après choc : {self.indicator():.4f}")
