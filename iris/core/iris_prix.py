"""
IRIS v2.1 - Mécanisme de Prix Explicites
==========================================

Module de gestion des prix explicites dans le système IRIS.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Principes :
-----------
1. DÉCOUVERTE DE PRIX : Les prix émergent de l'offre et la demande
2. MARCHÉS SECTORIELS : Prix différents par type d'actif/bien
3. ÉLASTICITÉ : Les prix s'ajustent selon les transactions
4. THERMOMÉTRIQUE : Les prix influencent et sont influencés par θ

Types de biens :
---------------
- ALIMENTATION : Biens alimentaires (essentiels)
- LOGEMENT : Immobilier, loyers
- TRANSPORT : Mobilité, véhicules
- ÉNERGIE : Électricité, carburants
- SERVICES : Services professionnels
- BIENS_DURABLES : Électroménager, meubles
- CULTURE : Loisirs, éducation

Formules clés :
--------------
Prix d'équilibre :
P_t = P_{t-1} × (1 + α × (D - O) / O)

où :
- P_t : Prix au temps t
- D : Demande (quantité demandée)
- O : Offre (quantité offerte)
- α : Coefficient d'ajustement (élasticité)

Impact thermométrique :
θ = D_total / V_circulation
→ Si θ↑ (demande élevée) → P↑ (prix augmentent)
→ Si θ↓ (demande faible) → P↓ (prix baissent)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
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


@dataclass
class Good:
    """
    Représente un bien échangeable

    Attributes:
        good_type: Type de bien
        nom: Nom du bien
        prix_base: Prix de référence initial (en U)
        elasticite: Élasticité prix-demande (-1.0 = élastique, -0.5 = inélastique)
    """
    good_type: GoodType
    nom: str
    prix_base: float
    elasticite: float = -0.8  # Par défaut : assez élastique

    def __post_init__(self):
        """Validation"""
        assert self.prix_base > 0, "Le prix de base doit être positif"
        assert -2.0 <= self.elasticite <= 0.0, "L'élasticité doit être négative"


@dataclass
class MarketData:
    """
    Données d'un marché sectoriel

    Un marché suit l'offre, la demande et le prix d'un type de bien.
    """
    good_type: GoodType
    prix_actuel: float  # Prix en U (monnaie d'usage)
    offre: float = 0.0  # Quantité offerte ce cycle
    demande: float = 0.0  # Quantité demandée ce cycle
    historique_prix: List[float] = field(default_factory=list)
    historique_offre: List[float] = field(default_factory=list)
    historique_demande: List[float] = field(default_factory=list)

    # Paramètres d'ajustement
    alpha_ajustement: float = 0.1  # Vitesse d'ajustement du prix
    prix_plancher: float = 0.1  # Prix minimum (évite prix nuls)

    def reset_cycle(self):
        """Réinitialise offre/demande pour un nouveau cycle"""
        self.offre = 0.0
        self.demande = 0.0

    def add_offre(self, quantite: float):
        """Ajoute de l'offre"""
        self.offre += quantite

    def add_demande(self, quantite: float):
        """Ajoute de la demande"""
        self.demande += quantite

    def ajuster_prix(self) -> float:
        """
        Ajuste le prix selon offre/demande

        Principe :
        - Si demande > offre → Prix monte
        - Si demande < offre → Prix baisse

        Formule :
        P_nouveau = P_actuel × (1 + α × (D - O) / max(O, 1))

        Returns:
            Nouveau prix
        """
        if self.offre < 1e-6:
            # Pas d'offre : prix reste stable (ou monte légèrement)
            self.prix_actuel *= 1.01
        else:
            # Calcul du déséquilibre
            desequilibre = (self.demande - self.offre) / self.offre

            # Ajustement proportionnel
            ajustement = self.alpha_ajustement * desequilibre

            # Nouveau prix
            self.prix_actuel *= (1 + ajustement)

            # Applique le plancher
            self.prix_actuel = max(self.prix_plancher, self.prix_actuel)

        # Enregistre l'historique
        self.historique_prix.append(self.prix_actuel)
        self.historique_offre.append(self.offre)
        self.historique_demande.append(self.demande)

        # Limite l'historique à 100 dernières valeurs
        if len(self.historique_prix) > 100:
            self.historique_prix.pop(0)
            self.historique_offre.pop(0)
            self.historique_demande.pop(0)

        return self.prix_actuel

    def get_inflation(self) -> float:
        """
        Calcule le taux d'inflation depuis le dernier cycle

        Returns:
            Taux d'inflation (0.02 = 2% d'inflation)
        """
        if len(self.historique_prix) < 2:
            return 0.0

        prix_precedent = self.historique_prix[-2]
        if prix_precedent == 0:
            return 0.0

        return (self.prix_actuel - prix_precedent) / prix_precedent


class PriceManager:
    """
    Gestionnaire de prix pour l'économie IRIS

    Gère les marchés sectoriels, la découverte de prix et l'inflation.
    """

    def __init__(self, prix_reference: Dict[GoodType, float] = None):
        """
        Initialise le gestionnaire de prix

        Args:
            prix_reference: Dictionnaire {GoodType: prix_base} optionnel
        """
        # Marchés sectoriels
        self.marches: Dict[GoodType, MarketData] = {}

        # Prix de référence par défaut (en U)
        if prix_reference is None:
            prix_reference = {
                GoodType.ALIMENTATION: 10.0,
                GoodType.LOGEMENT: 500.0,
                GoodType.TRANSPORT: 50.0,
                GoodType.ENERGIE: 30.0,
                GoodType.SERVICES: 100.0,
                GoodType.BIENS_DURABLES: 200.0,
                GoodType.CULTURE: 40.0,
                GoodType.AUTRE: 50.0
            }

        # Initialise les marchés
        for good_type, prix in prix_reference.items():
            self.marches[good_type] = MarketData(
                good_type=good_type,
                prix_actuel=prix
            )

        # Catalogue de biens
        self.catalogue: Dict[str, Good] = {}

        # Historique inflation globale
        self.historique_inflation_globale: List[float] = []

    def register_good(self, good: Good):
        """
        Enregistre un nouveau bien dans le catalogue

        Args:
            good: Bien à enregistrer
        """
        self.catalogue[good.nom] = good

    def get_prix(self, good_type: GoodType) -> float:
        """
        Retourne le prix actuel d'un type de bien

        Args:
            good_type: Type de bien

        Returns:
            Prix en U
        """
        if good_type not in self.marches:
            return 0.0
        return self.marches[good_type].prix_actuel

    def transact(self,
                good_type: GoodType,
                quantite: float,
                is_achat: bool) -> float:
        """
        Enregistre une transaction (achat ou vente)

        Args:
            good_type: Type de bien
            quantite: Quantité échangée
            is_achat: True si achat (demande), False si vente (offre)

        Returns:
            Montant total de la transaction (en U)
        """
        if good_type not in self.marches:
            return 0.0

        marche = self.marches[good_type]

        if is_achat:
            # Demande
            marche.add_demande(quantite)
        else:
            # Offre
            marche.add_offre(quantite)

        # Montant de la transaction au prix actuel
        return marche.prix_actuel * quantite

    def ajuster_tous_prix(self, thermometre: float = 1.0):
        """
        Ajuste tous les prix selon offre/demande + influence thermométrique

        Le thermomètre θ global influence tous les prix :
        - θ > 1 (excès demande) → Prix montent (×θ^0.1)
        - θ < 1 (excès offre) → Prix baissent (×θ^0.1)

        Args:
            thermometre: Thermomètre θ = D/V du système IRIS
        """
        # Facteur thermométrique (influence modérée)
        # θ = 1.0 → facteur = 1.0 (neutre)
        # θ = 1.1 → facteur ≈ 1.01 (+1%)
        # θ = 0.9 → facteur ≈ 0.99 (-1%)
        facteur_thermo = thermometre ** 0.1

        for good_type, marche in self.marches.items():
            # Ajustement local (offre/demande)
            marche.ajuster_prix()

            # Ajustement thermométrique global
            marche.prix_actuel *= facteur_thermo

            # Plancher
            marche.prix_actuel = max(marche.prix_plancher, marche.prix_actuel)

            # Reset cycle
            marche.reset_cycle()

    def get_inflation_globale(self) -> float:
        """
        Calcule l'inflation globale (moyenne pondérée des secteurs)

        Returns:
            Taux d'inflation global
        """
        if not self.marches:
            return 0.0

        # Moyenne simple des inflations sectorielles
        inflations = [marche.get_inflation() for marche in self.marches.values()]
        inflation_moyenne = np.mean(inflations)

        # Enregistre
        self.historique_inflation_globale.append(inflation_moyenne)

        # Limite l'historique
        if len(self.historique_inflation_globale) > 100:
            self.historique_inflation_globale.pop(0)

        return inflation_moyenne

    def get_indice_prix(self, reference_cycle: int = 0) -> float:
        """
        Calcule l'indice des prix par rapport à un cycle de référence

        Analogue de l'IPC (Indice des Prix à la Consommation)

        Args:
            reference_cycle: Cycle de référence (0 = début)

        Returns:
            Indice (1.0 = même niveau, 1.05 = +5%)
        """
        if not self.marches:
            return 1.0

        # Calcul de l'indice moyen
        indices = []
        for good_type, marche in self.marches.items():
            if len(marche.historique_prix) > reference_cycle:
                prix_ref = marche.historique_prix[reference_cycle]
                if prix_ref > 0:
                    indice = marche.prix_actuel / prix_ref
                    indices.append(indice)

        if not indices:
            return 1.0

        return np.mean(indices)

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques des marchés

        Returns:
            Dictionnaire de statistiques
        """
        stats = {
            'nb_marches': len(self.marches),
            'inflation_globale': self.get_inflation_globale(),
            'indice_prix': self.get_indice_prix(),
            'marches': {}
        }

        for good_type, marche in self.marches.items():
            stats['marches'][good_type.value] = {
                'prix': marche.prix_actuel,
                'offre': marche.offre,
                'demande': marche.demande,
                'inflation': marche.get_inflation(),
                'nb_transactions': len(marche.historique_prix)
            }

        return stats

    def simulate_random_transactions(self, n_transactions: int = 50):
        """
        Simule des transactions aléatoires (pour test)

        Args:
            n_transactions: Nombre de transactions à simuler
        """
        for _ in range(n_transactions):
            # Type de bien aléatoire
            good_type = np.random.choice(list(self.marches.keys()))

            # Quantité aléatoire
            quantite = np.random.uniform(0.1, 10.0)

            # Achat ou vente (50/50)
            is_achat = np.random.random() < 0.5

            # Transaction
            self.transact(good_type, quantite, is_achat)
