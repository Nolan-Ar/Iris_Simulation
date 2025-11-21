"""
IRIS Types - Dataclasses partagées
==================================

Ce fichier contient les dataclasses utilisées par plusieurs modules
pour éviter les imports circulaires.

Auteur: Arnault Nolan
Date: 2025
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class AssetType(Enum):
    """Types d'actifs dans le système IRIS"""
    IMMOBILIER = "immobilier"
    MOBILIER = "mobilier"
    ENTREPRISE = "entreprise"
    INTELLECTUEL = "intellectuel"
    SERVICE = "service"


class DebtComponent(Enum):
    """Composantes de la dette thermométrique D (§1.1.3)"""
    MATERIELLE = "materielle"      # Biens et immobilisations
    SERVICES = "services"          # Flux d'entretien
    CONTRACTUELLE = "contractuelle"  # Titres à promesse productive
    ENGAGEMENT = "engagement"      # Staking
    REGULATRICE = "regulatrice"    # Chambre de Relance


@dataclass
class Asset:
    """
    Représente un actif dans le système IRIS

    Chaque actif génère :
    - Un Verum (V₀) : mémoire de valeur
    - Un miroir thermométrique (D₀) : indicateur de régulation
    - Un NFT fondateur : preuve cryptographique d'existence unique
    """
    id: str
    asset_type: AssetType
    real_value: float
    V_initial: float = 0.0
    D_initial: float = 0.0
    owner_id: str = ""
    nft_hash: str = ""
    auth_factor: float = 1.0
    creation_time: int = 0

    def __post_init__(self):
        if self.V_initial == 0.0:
            self.V_initial = self.real_value * self.auth_factor
            self.D_initial = self.V_initial


@dataclass
class Agent:
    """
    Représente un agent économique dans le système IRIS

    Possède:
    - V_balance : patrimoine (Verum)
    - U_balance : liquidité (Usage)
    - assets : liste des actifs
    """
    id: str
    V_balance: float = 0.0
    U_balance: float = 0.0
    assets: List[Asset] = field(default_factory=list)
    contribution_score: float = 0.0
    consumables: float = 0.0

    def add_asset(self, asset: Asset) -> None:
        """Ajoute un actif à l'agent et met à jour son patrimoine"""
        self.assets.append(asset)
        self.V_balance += asset.V_initial

    def remove_asset(self, asset_id: str) -> None:
        """Retire un actif de l'agent et met à jour son patrimoine"""
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
        """
        return self.V_balance + self.U_balance
