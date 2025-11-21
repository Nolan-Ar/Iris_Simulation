"""
IRIS Comptes Entreprises - Gestion des Revenus d'Entreprise
=============================================================

Module de gestion des comptes d'entreprise dans IRIS : distribution asymétrique
des revenus générés par COMBUSTION (S + U → V), limites de rétention, et conversion en NFT financiers.

PRINCIPE FONDAMENTAL : COMBUSTION S + U = V
Les entreprises génèrent de la VALEUR (V) par combustion :
- S (Service/Travail) + U (Usage/Liquidité) → V (Valeur patrimoniale)

ALIGNEMENT THÉORIQUE (Document IRIS) :
Les comptes entreprises sont des agents économiques spéciaux avec :
- Distribution 40/60 ORGANIQUE :
  * 40% du V → MASSE SALARIALE (rémunérations des collaborateurs en U)
  * 60% du V → TRÉSORERIE de l'entreprise (V_operationnel + réserve)
- Limites de rétention : Plafonds sur V_operationnel
- Conversion automatique : Excédents V → NFT financiers (titres productifs)
- Traçabilité complète : Registre de tous les flux

IMPORTANT - Distinction RU vs Masse Salariale :
Les 40% distribués sont des SALAIRES (revenus productifs) versés aux collaborateurs,
PAS du Revenu Universel. Le RU est calculé séparément à partir de V_on(t) et
redistribué à TOUS les agents (cf. théorème de conservation de la respiration économique).

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Principes fondamentaux :
-----------------------
1. COMBUSTION : S + U → V (génération de valeur patrimoniale)
2. DISTRIBUTION ORGANIQUE 40/60 :
   - 40% V → MASSE SALARIALE (rémunérations collaborateurs en U)
   - 60% V → TRÉSORERIE (V_operationnel + réserve régulatrice)
3. NON-THÉSAURISATION : V_operationnel limité pour éviter accumulation
4. CONVERSION NFT : Surplus V transformés en titres productifs
5. TRANSPARENCE : Traçabilité totale des flux

Formules clés :
--------------
Combustion entreprise :
S (service/travail) + U (usage) → V_généré (valeur patrimoniale)

Distribution du V_généré (DISTRIBUTION ORGANIQUE 40/60) :
- 40% → Converti en U pour MASSE SALARIALE (rémunérations collaborateurs)
- 60% → Ajouté à V_operationnel (trésorerie de l'entreprise)

Limite de rétention :
V_operationnel ≤ Seuil_retention × V_entreprise

Au-delà du seuil :
Excédent_V → Conversion en NFT_financier (titre productif)

Impact sur D :
- Distribution masse salariale : Flux vers agents (rémunérations productives)
- Conversion NFT : ΔD_contractuelle (nouveaux titres financiers)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import hashlib
import time
import logging
import secrets

from iris.utils import (
    validate_non_negative,
    validate_positive,
    validate_probability,
    safe_divide,
)

logger = logging.getLogger(__name__)


class BusinessType(Enum):
    """Type d'entreprise"""
    PRODUCTION = "production"  # Production de biens
    SERVICE = "service"  # Prestation de services
    COMMERCE = "commerce"  # Commerce et distribution
    TECHNOLOGIE = "technologie"  # Technologies et innovation
    INFRASTRUCTURE = "infrastructure"  # Infrastructure collective


@dataclass
class NFTFinancier:
    """
    NFT Financier - Titre productif issu de la conversion d'excédents V

    Un NFT financier représente une créance productive sur l'entreprise.
    Il est créé lorsque V_operationnel dépasse les limites de rétention.
    """
    nft_id: str
    business_id: str
    valeur_convertie: float  # Montant V converti en NFT
    timestamp_creation: int
    hash_nft: str
    rendement_annuel: float = 0.0  # Rendement du NFT
    maturite: int = 0  # Cycles jusqu'à maturité (0 = perpétuel)


@dataclass
class FluxEntreprise:
    """
    Flux de revenus d'une entreprise (combustion)

    ALIGNEMENT THÉORIQUE :
    Enregistre tous les mouvements de valeur pour traçabilité, incluant
    la distribution organique 40/60 (masse salariale vs trésorerie).
    """
    cycle: int
    business_id: str
    V_genere: float  # V généré par combustion S + U → V
    part_salariale_en_U: float  # 40% du V converti en U (masse salariale collaborateurs)
    part_V_operationnel: float  # 60% du V ajouté à V_operationnel (trésorerie)
    exces_V_converti: float  # Excédent V converti en NFT
    nft_genere_id: Optional[str] = None  # ID du NFT si conversion


class CompteEntreprise:
    """
    Compte d'entreprise IRIS

    ALIGNEMENT THÉORIQUE (Document IRIS) :
    Un compte entreprise gère :
    1. La COMBUSTION : S + U → V (génération de valeur)
    2. La distribution ORGANIQUE 40/60 du V généré
    3. Les limites de rétention de V_operationnel
    4. La conversion automatique des excédents V en NFT financiers
    5. La traçabilité complète des flux

    Principes de distribution organique 40/60 :
    - Combustion génère V (valeur patrimoniale)
    - 40% du V → Converti en U pour MASSE SALARIALE (rémunérations collaborateurs)
    - 60% du V → V_operationnel (trésorerie de l'entreprise)
    - V_operationnel plafonné à seuil_retention × V_entreprise
    - Excédents V → NFT_financiers (titres productifs)

    IMPORTANT :
    Les 40% sont des SALAIRES (revenus productifs des collaborateurs),
    PAS du Revenu Universel. Le RU est calculé séparément et redistribué
    à tous les agents, conformément au théorème de conservation de la
    respiration économique.

    Différence avec agents individuels :
    - Génération de V par combustion (pas simple conversion V→U)
    - Distribution asymétrique organique 40/60 (vs 100% pour individus)
    - Limites de rétention strictes sur V
    - Génération de NFT financiers (titres productifs)
    - Traçabilité renforcée
    """

    def __init__(self,
                 business_id: str,
                 business_type: BusinessType,
                 V_entreprise: float,
                 ratio_salarial: float = 0.40,
                 ratio_tresorerie: float = 0.60,
                 seuil_retention: float = 0.20):
        """
        Initialise un compte d'entreprise

        ALIGNEMENT THÉORIQUE :
        Les ratios reflètent la distribution organique 40/60.

        Args:
            business_id: Identifiant unique de l'entreprise
            business_type: Type d'entreprise
            V_entreprise: Patrimoine de base de l'entreprise (V)
            ratio_salarial: Part du V généré → masse salariale en U (40% par défaut)
            ratio_tresorerie: Part du V généré → trésorerie V_operationnel (60% par défaut)
            seuil_retention: Seuil de rétention V_operationnel (20% de V_entreprise par défaut)
        """
        # SÉCURITÉ: Validations des paramètres
        try:
            validate_non_negative(V_entreprise, "V_entreprise")
            validate_probability(ratio_salarial, "ratio_salarial")
            validate_probability(ratio_tresorerie, "ratio_tresorerie")
            validate_probability(seuil_retention, "seuil_retention")
        except Exception as e:
            logger.error(f"Validation failed for CompteEntreprise {business_id}: {e}")
            raise

        # Validation ratios (distribution organique 40/60)
        if abs(ratio_salarial + ratio_tresorerie - 1.0) >= 1e-6:
            raise ValueError(
                f"Les ratios doivent sommer à 1.0 (distribution organique), "
                f"got {ratio_salarial + ratio_tresorerie}"
            )

        self.business_id = business_id
        self.business_type = business_type
        self.V_entreprise = max(0.0, V_entreprise)  # Pas de V négatif
        self.ratio_salarial = ratio_salarial  # 40% → masse salariale
        self.ratio_tresorerie = ratio_tresorerie  # 60% → trésorerie
        self.seuil_retention = seuil_retention

        # Soldes
        self.V_operationnel: float = 0.0  # Trésorerie opérationnelle (V)

        # CORRECTION: Ajout de S et U pour permettre la combustion
        # L'entreprise doit avoir du Stipulat (S) et de la liquidité (U) pour opérer
        # On initialise avec 50% du capital en S et 50% en U
        self.S_balance: float = V_entreprise * 0.5  # Stipulat (contrats/engagements)
        self.U_operationnel: float = V_entreprise * 0.5  # Liquidité opérationnelle

        # NFT financiers émis
        self.nft_financiers: Dict[str, NFTFinancier] = {}

        # Historique des flux
        self.flux_history: List[FluxEntreprise] = []

        # Statistiques
        self.total_V_genere = 0.0
        self.total_masse_salariale_U = 0.0  # Renommé de total_contribution_RU_en_U
        self.total_NFT_emis_V = 0.0
        self.nb_conversions = 0

        logger.debug(f"Created CompteEntreprise {business_id} with V={V_entreprise:.2f}")

    def get_limite_retention(self) -> float:
        """
        Calcule la limite de rétention de V_operationnel

        Formule : Limite = seuil_retention × V_entreprise

        Exemple :
        - V_entreprise = 1,000,000
        - seuil_retention = 0.20 (20%)
        - Limite = 200,000

        Returns:
            Limite maximale de V_operationnel
        """
        return self.seuil_retention * self.V_entreprise

    def distribute_V_genere(self,
                           V_genere: float,
                           cycle: int) -> Tuple[float, float, Optional[NFTFinancier]]:
        """
        Distribue le V généré par combustion selon le schéma ORGANIQUE 40/60

        ALIGNEMENT THÉORIQUE (Document IRIS) :
        C'EST LE CŒUR DU SYSTÈME DE COMPTES ENTREPRISES !

        SÉCURITÉ:
        - Validation V_genere >= 0
        - Protection contre overflow

        Args:
            V_genere: Valeur V générée par combustion (S + U → V)
            cycle: Cycle actuel

        Returns:
            Tuple (part_salariale_en_U, V_operationnel_net, nft_genere)
        """
        # SÉCURITÉ: Validation
        try:
            validate_non_negative(V_genere, "V_genere")
        except Exception as e:
            logger.error(f"Invalid V_genere in distribute_V_genere: {e}")
            return (0.0, self.V_operationnel, None)

        if V_genere == 0:
            return (0.0, self.V_operationnel, None)

        # ÉTAPE 1 : DISTRIBUTION ORGANIQUE 40/60 du V généré
        part_salariale_en_U = V_genere * self.ratio_salarial  # 40% → masse salariale
        part_V_operationnel = V_genere * self.ratio_tresorerie  # 60% → trésorerie

        # Ajoute à V_operationnel (temporairement)
        self.V_operationnel += part_V_operationnel

        # ÉTAPE 2 : VÉRIFICATION LIMITE DE RÉTENTION
        limite = self.get_limite_retention()
        nft_genere = None
        exces_V_converti = 0.0

        if self.V_operationnel > limite:
            # DÉPASSEMENT : Conversion de l'excédent V en NFT financier
            exces_V = self.V_operationnel - limite

            # Génère un NFT financier pour l'excédent V
            try:
                nft_genere = self._convert_V_to_nft_financier(exces_V, cycle)
            except Exception as e:
                logger.error(f"Failed to create NFT: {e}")
                # Continue sans NFT
                nft_genere = None

            if nft_genere:
                # Retire l'excédent de V_operationnel
                self.V_operationnel = limite
                exces_V_converti = exces_V

                # Statistiques
                self.total_NFT_emis_V += exces_V
                self.nb_conversions += 1

        # ÉTAPE 3 : TRAÇABILITÉ
        flux = FluxEntreprise(
            cycle=cycle,
            business_id=self.business_id,
            V_genere=V_genere,
            part_salariale_en_U=part_salariale_en_U,
            part_V_operationnel=part_V_operationnel - exces_V_converti,
            exces_V_converti=exces_V_converti,
            nft_genere_id=nft_genere.nft_id if nft_genere else None
        )
        self.flux_history.append(flux)

        # Mise à jour statistiques
        self.total_V_genere += V_genere
        self.total_masse_salariale_U += part_salariale_en_U

        logger.debug(
            f"Distributed V={V_genere:.2f}: salary={part_salariale_en_U:.2f}, "
            f"treasury={part_V_operationnel:.2f}, NFT={exces_V_converti:.2f}"
        )

        return (part_salariale_en_U, self.V_operationnel, nft_genere)

    def _convert_V_to_nft_financier(self,
                                    montant_V: float,
                                    cycle: int) -> NFTFinancier:
        """
        Convertit un excédent de V_operationnel en NFT financier

        SÉCURITÉ:
        - Utilise secrets pour éviter collisions de hash
        - Validation montant_V

        Args:
            montant_V: Montant de V à convertir
            cycle: Cycle de création

        Returns:
            NFT financier créé
        """
        # SÉCURITÉ: Validation
        try:
            validate_positive(montant_V, "montant_V")
        except Exception as e:
            logger.error(f"Invalid montant_V in NFT creation: {e}")
            raise

        # Génère un ID unique avec salt cryptographique
        salt = secrets.token_hex(8)
        nft_id = f"NFT_FIN_{self.business_id}_{cycle}_{len(self.nft_financiers)}_{salt}"

        # Calcule le hash cryptographique robuste
        timestamp = int(time.time() * 1000000)  # microseconds
        data = f"{nft_id}|{self.business_id}|{montant_V}|{cycle}|{timestamp}|{salt}"
        hash_nft = hashlib.sha256(data.encode()).hexdigest()

        # Rendement annuel : basé sur le type d'entreprise
        rendement_base = {
            BusinessType.PRODUCTION: 0.03,  # 3% annuel
            BusinessType.SERVICE: 0.04,  # 4% annuel
            BusinessType.COMMERCE: 0.035,  # 3.5% annuel
            BusinessType.TECHNOLOGIE: 0.05,  # 5% annuel (plus risqué)
            BusinessType.INFRASTRUCTURE: 0.025  # 2.5% annuel (très stable)
        }
        rendement = rendement_base.get(self.business_type, 0.03)

        # Crée le NFT
        nft = NFTFinancier(
            nft_id=nft_id,
            business_id=self.business_id,
            valeur_convertie=montant_V,
            timestamp_creation=cycle,
            hash_nft=hash_nft,
            rendement_annuel=rendement,
            maturite=0  # Perpétuel par défaut
        )

        # Enregistre
        self.nft_financiers[nft_id] = nft

        return nft

    def depense_V_operationnel(self, montant: float) -> bool:
        """
        Effectue une dépense sur le V_operationnel

        Args:
            montant: Montant V à dépenser

        Returns:
            True si succès, False si fonds insuffisants
        """
        if montant > self.V_operationnel:
            return False

        self.V_operationnel -= montant
        return True

    def update_V_entreprise(self, nouvelle_valeur: float):
        """
        Met à jour la valeur V de base de l'entreprise

        Cela modifie la limite de rétention dynamiquement.

        Args:
            nouvelle_valeur: Nouvelle valeur de V
        """
        self.V_entreprise = nouvelle_valeur

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques du compte entreprise

        SÉCURITÉ: Utilise safe_divide pour éviter div/0

        Returns:
            Dictionnaire avec statistiques complètes
        """
        limite = self.get_limite_retention()
        taux_utilisation = safe_divide(
            self.V_operationnel * 100,
            limite,
            default=0.0
        )

        return {
            'business_id': self.business_id,
            'business_type': self.business_type.value,
            'V_entreprise': self.V_entreprise,
            'V_operationnel': self.V_operationnel,
            'limite_retention': limite,
            'taux_utilisation_limite': taux_utilisation,
            'total_V_genere': self.total_V_genere,
            'total_masse_salariale_U': self.total_masse_salariale_U,
            'total_NFT_emis_V': self.total_NFT_emis_V,
            'nb_conversions': self.nb_conversions,
            'nb_NFT_actifs': len(self.nft_financiers),
            'nb_flux_enregistres': len(self.flux_history)
        }


class RegistreComptesEntreprises:
    """
    Registre central des comptes entreprises

    ALIGNEMENT THÉORIQUE (Document IRIS) :
    Gère l'ensemble des comptes d'entreprise dans le système IRIS.
    Centralise :
    - Création et gestion des comptes
    - Agrégation de la masse salariale (rémunérations en U)
    - Registre des NFT financiers (titres productifs)
    - Statistiques globales

    IMPORTANT :
    L'accumulateur "pool_masse_salariale_U" collecte les rémunérations
    des collaborateurs (40% de distribution organique), qui sont des
    SALAIRES, pas du RU. Le RU est calculé séparément via V_on(t).
    """

    def __init__(self):
        """Initialise le registre"""
        self.comptes: Dict[str, CompteEntreprise] = {}

        # Accumulateur pour la masse salariale (en U)
        # Représente les rémunérations des collaborateurs (40% distribution organique)
        self.pool_masse_salariale_U: float = 0.0

        # Registre global des NFT financiers
        self.nft_financiers_global: Dict[str, NFTFinancier] = {}

        # Statistiques
        self.total_entreprises_actives = 0
        self.total_masse_salariale_U = 0.0  # Renommé de total_contributions_RU_U
        self.total_NFT_globaux_V = 0.0

    def create_compte(self,
                     business_id: str,
                     business_type: BusinessType,
                     V_entreprise: float,
                     ratio_salarial: float = 0.40,
                     ratio_tresorerie: float = 0.60,
                     seuil_retention: float = 0.20) -> CompteEntreprise:
        """
        Crée un nouveau compte d'entreprise

        ALIGNEMENT THÉORIQUE :
        Les ratios reflètent la distribution organique 40/60.

        Args:
            business_id: Identifiant unique
            business_type: Type d'entreprise
            V_entreprise: Patrimoine initial
            ratio_salarial: Part masse salariale (défaut 40%)
            ratio_tresorerie: Part trésorerie (défaut 60%)
            seuil_retention: Seuil de rétention (défaut 20%)

        Returns:
            Compte créé
        """
        if business_id in self.comptes:
            raise ValueError(f"Compte entreprise {business_id} existe déjà")

        compte = CompteEntreprise(
            business_id=business_id,
            business_type=business_type,
            V_entreprise=V_entreprise,
            ratio_salarial=ratio_salarial,
            ratio_tresorerie=ratio_tresorerie,
            seuil_retention=seuil_retention
        )

        self.comptes[business_id] = compte
        self.total_entreprises_actives += 1

        return compte

    def process_V_genere(self,
                        business_id: str,
                        V_genere: float,
                        cycle: int) -> Tuple[float, Optional[NFTFinancier]]:
        """
        Traite un V généré par combustion (S + U → V) avec distribution organique 40/60

        ALIGNEMENT THÉORIQUE :
        Les 40% sont convertis en masse salariale (rémunérations collaborateurs),
        pas en RU. Le RU est calculé séparément.

        Args:
            business_id: ID de l'entreprise
            V_genere: Valeur V générée par combustion
            cycle: Cycle actuel

        Returns:
            Tuple (masse_salariale_en_U, nft_genere)
        """
        if business_id not in self.comptes:
            raise ValueError(f"Compte entreprise {business_id} introuvable")

        compte = self.comptes[business_id]

        # Distribution du V généré (organique 40/60)
        part_salariale_U, part_V_op, nft = compte.distribute_V_genere(V_genere, cycle)

        # Accumule la masse salariale (en U) dans le pool
        self.pool_masse_salariale_U += part_salariale_U
        self.total_masse_salariale_U += part_salariale_U

        # Enregistre le NFT si créé
        if nft:
            self.nft_financiers_global[nft.nft_id] = nft
            self.total_NFT_globaux_V += nft.valeur_convertie

        return (part_salariale_U, nft)

    def collect_pool_masse_salariale(self) -> float:
        """
        Collecte et réinitialise le pool de masse salariale des entreprises (en U)

        ALIGNEMENT THÉORIQUE :
        Ce montant U représente les RÉMUNÉRATIONS des collaborateurs (40% de
        la distribution organique), pas du RU. Dans cette version simplifiée,
        la masse salariale est redistribuée comme proxy des salaires réels.

        Note :
        Dans le modèle théorique complet, ces salaires seraient versés
        directement aux employés identifiés de chaque entreprise.

        Returns:
            Montant U du pool de masse salariale à redistribuer
        """
        montant = self.pool_masse_salariale_U
        self.pool_masse_salariale_U = 0.0
        return montant

    def get_compte(self, business_id: str) -> Optional[CompteEntreprise]:
        """Retourne un compte entreprise par ID"""
        return self.comptes.get(business_id)

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques globales du registre

        SÉCURITÉ: Utilise safe_divide pour éviter div/0

        Returns:
            Statistiques complètes
        """
        total_V_operationnel = sum(c.V_operationnel for c in self.comptes.values())
        total_V_entreprises = sum(c.V_entreprise for c in self.comptes.values())

        ratio_V = safe_divide(
            total_V_operationnel * 100,
            total_V_entreprises,
            default=0.0
        )

        return {
            'nb_entreprises_actives': self.total_entreprises_actives,
            'total_V_entreprises': total_V_entreprises,
            'total_V_operationnel': total_V_operationnel,
            'pool_masse_salariale_U_en_attente': self.pool_masse_salariale_U,
            'total_masse_salariale_U': self.total_masse_salariale_U,
            'total_NFT_financiers': len(self.nft_financiers_global),
            'total_valeur_NFT_V': self.total_NFT_globaux_V,
            'ratio_V_op_V_base': ratio_V
        }
