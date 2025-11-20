"""
IRIS Chambre de Relance - Gestion des Patrimoines Orphelins
===========================================================

Module de la Chambre de Relance (CR) : liquidation et redistribution
des actifs orphelins selon le principe de justice économique d'IRIS.

La Chambre de Relance traite les patrimoines qui ne peuvent plus être
gérés par leurs propriétaires :
- Décès sans héritier
- Actifs abandonnés
- Entreprises en faillite
- Destructions d'actifs

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Principes fondamentaux :
-----------------------
1. COLLECTE : Récupération des actifs orphelins
2. LIQUIDATION : Conversion en V_CR selon facteurs d'ajustement
3. REDISTRIBUTION : 60% RU / 30% Investissements / 10% Gouvernance
4. RÉDUCTION D : ΔD_CR < 0 (la redistribution réduit la dette thermométrique)

Formules clés :
--------------
V_CR_i = V_actif × Φ_état × Φ_obsolescence

où :
- Φ_état : Facteur d'état physique (0.0-1.0, dégradation)
- Φ_obsolescence : Facteur d'obsolescence temporelle (décroissance exponentielle)

Redistribution :
---------------
Pool_CR = ΣV_CR_i (somme de tous les actifs liquidés)

Allocation :
- 60% → Revenu universel (distribution équitable)
- 30% → Investissements collectifs (infrastructure, biens communs)
- 10% → Gouvernance (fonctionnement, recherche, développement)

Impact sur D :
-------------
ΔD_CR = -0.3 × Pool_CR (réduction de 30% de D)

Cette réduction est une caractéristique unique d'IRIS : la redistribution
des patrimoines orphelins RÉDUIT la dette thermométrique globale,
créant un mécanisme déflationniste naturel.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class OrphanReason(Enum):
    """Raison pour laquelle un actif devient orphelin"""
    DECES_SANS_HERITIER = "deces_sans_heritier"  # Décès sans héritier
    ABANDON = "abandon"  # Actif abandonné volontairement
    FAILLITE = "faillite"  # Entreprise en faillite
    DESTRUCTION = "destruction"  # Destruction physique (catastrophe, etc.)
    INACTIVITE = "inactivite"  # Inactivité prolongée du propriétaire


@dataclass
class OrphanAsset:
    """
    Représente un actif orphelin collecté par la Chambre de Relance

    Un actif orphelin est un bien qui n'a plus de propriétaire actif
    et doit être liquidé par le système.
    """
    asset_id: str
    asset_type: str
    V_initial: float  # Valeur V d'origine
    D_initial: float  # Dette D associée
    reason: OrphanReason  # Raison de l'orphelinat
    timestamp_orphelin: int  # Moment où l'actif devient orphelin
    age_asset: int = 0  # Âge de l'actif en cycles (pour obsolescence)
    etat_physique: float = 1.0  # État physique (0.0-1.0)


@dataclass
class RedistributionEvent:
    """
    Événement de redistribution de la Chambre de Relance

    Chaque redistribution crée un événement documenté
    pour traçabilité et analyse.
    """
    cycle: int
    pool_CR: float  # Montant total du pool
    allocation_RU: float  # 60% vers revenu universel
    allocation_investissement: float  # 30% vers investissements collectifs
    allocation_gouvernance: float  # 10% vers gouvernance
    delta_D_CR: float  # Réduction de D (négatif)
    nb_actifs_liquides: int  # Nombre d'actifs liquidés
    nb_beneficiaires_RU: int  # Nombre d'agents recevant RU
    timestamp: int


class ChambreRelance:
    """
    Chambre de Relance IRIS

    La Chambre de Relance est le mécanisme de justice sociale et de
    régulation structurelle d'IRIS. Elle :

    1. COLLECTE les actifs orphelins (sans propriétaire actif)
    2. LIQUIDE ces actifs selon facteurs d'état et obsolescence
    3. REDISTRIBUE la valeur selon le schéma 60/30/10
    4. RÉDUIT D globalement (effet déflationniste)

    Principe : "Rien ne se perd, tout se transforme en bien commun"

    La CR assure que :
    - Les patrimoines orphelins retournent à la collectivité
    - La redistribution est transparente et équitable
    - Le système maintient son équilibre thermodynamique
    - La concentration de richesse est limitée structurellement
    """

    def __init__(self,
                 ratio_RU: float = 0.60,
                 ratio_investissement: float = 0.30,
                 ratio_gouvernance: float = 0.10,
                 tau_obsolescence: float = 0.01,
                 delta_D_factor: float = 0.30):
        """
        Initialise la Chambre de Relance

        Args:
            ratio_RU: Part du pool vers revenu universel (60% par défaut)
            ratio_investissement: Part vers investissements (30% par défaut)
            ratio_gouvernance: Part vers gouvernance (10% par défaut)
            tau_obsolescence: Taux d'obsolescence annuel (1% par défaut)
            delta_D_factor: Facteur de réduction de D (30% par défaut)
        """
        # Validation des ratios
        assert abs(ratio_RU + ratio_investissement + ratio_gouvernance - 1.0) < 1e-6, \
            "Les ratios de redistribution doivent sommer à 1.0"

        self.ratio_RU = ratio_RU
        self.ratio_investissement = ratio_investissement
        self.ratio_gouvernance = ratio_gouvernance
        self.tau_obsolescence = tau_obsolescence
        self.delta_D_factor = delta_D_factor

        # Pool des actifs orphelins en attente de liquidation
        self.orphan_pool: Dict[str, OrphanAsset] = {}

        # Historique des redistributions
        self.redistribution_history: List[RedistributionEvent] = []

        # Accumulateurs pour investissements et gouvernance
        self.fonds_investissement: float = 0.0
        self.fonds_gouvernance: float = 0.0

        # Statistiques
        self.total_V_collecte = 0.0
        self.total_V_redistribue = 0.0
        self.total_D_reduit = 0.0
        self.nb_actifs_traites = 0

    def calculate_phi_etat(self, etat_physique: float) -> float:
        """
        Calcule le facteur Φ_état selon l'état physique de l'actif

        Φ_état représente la dégradation physique de l'actif :
        - 1.0 : État neuf/excellent
        - 0.8 : Bon état
        - 0.5 : État moyen
        - 0.2 : Mauvais état
        - 0.0 : Détruit/inutilisable

        Args:
            etat_physique: État physique (0.0-1.0)

        Returns:
            Φ_état (0.0-1.0)
        """
        return max(0.0, min(1.0, etat_physique))

    def calculate_phi_obsolescence(self, age_asset: int) -> float:
        """
        Calcule le facteur Φ_obsolescence selon l'âge de l'actif

        L'obsolescence suit une décroissance exponentielle :
        Φ_obs = exp(-τ × age)

        où τ (tau) est le taux d'obsolescence annuel.

        Args:
            age_asset: Âge de l'actif en cycles

        Returns:
            Φ_obsolescence (0.0-1.0)
        """
        return np.exp(-self.tau_obsolescence * age_asset)

    def add_orphan_asset(self,
                        asset_id: str,
                        asset_type: str,
                        V_initial: float,
                        D_initial: float,
                        reason: OrphanReason,
                        timestamp_orphelin: int,
                        age_asset: int = 0,
                        etat_physique: float = 1.0) -> bool:
        """
        Ajoute un actif orphelin au pool de la Chambre de Relance

        Cette fonction est appelée lorsqu'un actif perd son propriétaire actif.

        Args:
            asset_id: Identifiant unique de l'actif
            asset_type: Type d'actif
            V_initial: Valeur V de l'actif
            D_initial: Dette D associée
            reason: Raison de l'orphelinat
            timestamp_orphelin: Timestamp où l'actif devient orphelin
            age_asset: Âge de l'actif (pour obsolescence)
            etat_physique: État physique (0.0-1.0)

        Returns:
            True si ajouté avec succès, False si déjà présent
        """
        if asset_id in self.orphan_pool:
            return False  # Déjà dans le pool

        orphan = OrphanAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            V_initial=V_initial,
            D_initial=D_initial,
            reason=reason,
            timestamp_orphelin=timestamp_orphelin,
            age_asset=age_asset,
            etat_physique=etat_physique
        )

        self.orphan_pool[asset_id] = orphan
        self.total_V_collecte += V_initial

        return True

    def liquidate_orphan(self, orphan: OrphanAsset) -> float:
        """
        Liquide un actif orphelin en V_CR

        Formule :
        V_CR = V_initial × Φ_état × Φ_obsolescence

        La liquidation tient compte de :
        - La dégradation physique (Φ_état)
        - L'obsolescence temporelle (Φ_obsolescence)

        Args:
            orphan: Actif orphelin à liquider

        Returns:
            V_CR : Valeur liquidée
        """
        phi_etat = self.calculate_phi_etat(orphan.etat_physique)
        phi_obs = self.calculate_phi_obsolescence(orphan.age_asset)

        V_CR = orphan.V_initial * phi_etat * phi_obs

        return V_CR

    def redistribute_pool(self,
                         cycle: int,
                         nb_beneficiaires_RU: int,
                         timestamp: int) -> Tuple[float, float, float, float]:
        """
        Redistribue le pool des actifs orphelins selon le schéma 60/30/10

        C'EST LE CŒUR DE LA CHAMBRE DE RELANCE !

        Processus :
        1. LIQUIDATION : Convertir tous les orphelins en V_CR
        2. ALLOCATION :
           - 60% → Distribution immédiate (RU)
           - 30% → Fonds d'investissement
           - 10% → Fonds de gouvernance
        3. RÉDUCTION D : ΔD_CR = -30% × Pool_CR

        Args:
            cycle: Numéro du cycle actuel
            nb_beneficiaires_RU: Nombre d'agents pour distribution RU
            timestamp: Timestamp de la redistribution

        Returns:
            Tuple (montant_RU_par_agent, delta_D_CR, total_investissement, total_gouvernance)
        """
        if not self.orphan_pool:
            # Pas d'orphelins à redistribuer
            return (0.0, 0.0, 0.0, 0.0)

        # ÉTAPE 1 : LIQUIDATION de tous les actifs orphelins
        pool_CR = 0.0
        nb_actifs = len(self.orphan_pool)

        for orphan in self.orphan_pool.values():
            V_CR = self.liquidate_orphan(orphan)
            pool_CR += V_CR

        # ÉTAPE 2 : ALLOCATION selon le schéma 60/30/10
        allocation_RU = pool_CR * self.ratio_RU
        allocation_investissement = pool_CR * self.ratio_investissement
        allocation_gouvernance = pool_CR * self.ratio_gouvernance

        # Distribution du RU par agent
        montant_RU_par_agent = (allocation_RU / nb_beneficiaires_RU
                                if nb_beneficiaires_RU > 0 else 0.0)

        # Accumulation des fonds
        self.fonds_investissement += allocation_investissement
        self.fonds_gouvernance += allocation_gouvernance

        # ÉTAPE 3 : RÉDUCTION DE D
        # Principe unique d'IRIS : la redistribution RÉDUIT la dette thermométrique
        # ΔD_CR = -30% × Pool_CR (valeur négative)
        delta_D_CR = -self.delta_D_factor * pool_CR

        # ÉTAPE 4 : ENREGISTREMENT
        event = RedistributionEvent(
            cycle=cycle,
            pool_CR=pool_CR,
            allocation_RU=allocation_RU,
            allocation_investissement=allocation_investissement,
            allocation_gouvernance=allocation_gouvernance,
            delta_D_CR=delta_D_CR,
            nb_actifs_liquides=nb_actifs,
            nb_beneficiaires_RU=nb_beneficiaires_RU,
            timestamp=timestamp
        )
        self.redistribution_history.append(event)

        # Mise à jour statistiques
        self.total_V_redistribue += pool_CR
        self.total_D_reduit += abs(delta_D_CR)
        self.nb_actifs_traites += nb_actifs

        # Vider le pool d'orphelins (tous liquidés)
        self.orphan_pool.clear()

        return (montant_RU_par_agent, delta_D_CR, allocation_investissement, allocation_gouvernance)

    def get_pool_value(self) -> float:
        """
        Calcule la valeur totale actuelle du pool d'orphelins

        Returns:
            Valeur totale V_CR du pool
        """
        total = 0.0
        for orphan in self.orphan_pool.values():
            V_CR = self.liquidate_orphan(orphan)
            total += V_CR
        return total

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques de la Chambre de Relance

        Returns:
            Dictionnaire avec statistiques complètes
        """
        return {
            'nb_orphelins_en_attente': len(self.orphan_pool),
            'valeur_pool_actuel': self.get_pool_value(),
            'total_V_collecte': self.total_V_collecte,
            'total_V_redistribue': self.total_V_redistribue,
            'total_D_reduit': self.total_D_reduit,
            'nb_actifs_traites': self.nb_actifs_traites,
            'nb_redistributions': len(self.redistribution_history),
            'fonds_investissement': self.fonds_investissement,
            'fonds_gouvernance': self.fonds_gouvernance,
            'efficacite_liquidation': (self.total_V_redistribue / self.total_V_collecte * 100
                                      if self.total_V_collecte > 0 else 0.0)
        }

    def use_fonds_investissement(self, montant: float) -> bool:
        """
        Utilise une partie du fonds d'investissement

        Permet d'allouer les fonds pour :
        - Infrastructure collective
        - Biens communs
        - Projets d'intérêt général

        Args:
            montant: Montant à utiliser

        Returns:
            True si utilisation réussie, False si fonds insuffisant
        """
        if montant > self.fonds_investissement:
            return False

        self.fonds_investissement -= montant
        return True

    def use_fonds_gouvernance(self, montant: float) -> bool:
        """
        Utilise une partie du fonds de gouvernance

        Permet de financer :
        - Fonctionnement du système
        - Recherche et développement
        - Amélioration des protocoles
        - Audits et vérifications

        Args:
            montant: Montant à utiliser

        Returns:
            True si utilisation réussie, False si fonds insuffisant
        """
        if montant > self.fonds_gouvernance:
            return False

        self.fonds_gouvernance -= montant
        return True

    def get_last_redistribution(self) -> Optional[RedistributionEvent]:
        """
        Retourne le dernier événement de redistribution

        Returns:
            RedistributionEvent ou None si aucune redistribution
        """
        if not self.redistribution_history:
            return None
        return self.redistribution_history[-1]
