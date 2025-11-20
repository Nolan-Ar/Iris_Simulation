"""
IRIS Oracle - Système d'Émission Cadastrale
===========================================

Module de l'Oracle IRIS : gestion de l'ancrage des actifs réels dans le système
via une procédure d'émission cadastrale formelle.

L'Oracle est le point d'entrée unique pour l'ancrage de valeur dans IRIS.
Il combine deux flux complémentaires :
- Flux officiel : sources certifiées (cadastre, autorités)
- Flux auto-intégratif : auto-déclarations des agents

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Formules fondamentales :
-----------------------
V₀_bien = Valeur_estimée × Φ_or × (1 − r_zone/100) × Φ_auth

où :
- Φ_or : Facteur or de zone (équivalent or local, typiquement ~1.0)
- r_zone : Risque de zone en % (géopolitique, climatique, économique)
- Φ_auth : Facteur d'authentification (1.0 = source officielle, <1.0 = auto-déclaration)

NFT Fondateur :
--------------
Chaque actif ancré génère un NFT fondateur unique avec :
- Hash SHA-256 : preuve cryptographique d'existence
- Métadonnées : type, valeur, propriétaire, timestamp
- Unicité garantie : vérification anti-doublon
"""

import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np


class FluxType(Enum):
    """Type de flux d'émission"""
    OFFICIEL = "officiel"  # Source certifiée (cadastre, autorité)
    AUTO_INTEGRATIF = "auto_integratif"  # Auto-déclaration agent


class VerificationStatus(Enum):
    """Statut de vérification d'un actif"""
    PENDING = "pending"  # En attente de vérification
    VERIFIED = "verified"  # Vérifié et accepté
    REJECTED = "rejected"  # Rejeté (doublon, fraude, etc.)


@dataclass
class NFTMetadata:
    """
    Métadonnées du NFT fondateur

    Le NFT est la preuve cryptographique immuable de l'existence unique
    d'un actif dans le système IRIS.
    """
    asset_id: str
    asset_type: str
    owner_id: str
    valeur_estimee: float
    V_initial: float
    D_initial: float
    phi_or: float
    r_zone: float
    phi_auth: float
    flux_type: FluxType
    timestamp: int
    hash_nft: str
    verification_status: VerificationStatus = VerificationStatus.PENDING


class Oracle:
    """
    Oracle IRIS - Système d'Émission Cadastrale

    L'Oracle est le gardien de l'intégrité du système. Il :
    1. Vérifie l'unicité de chaque actif (anti-doublon)
    2. Calcule V₀ selon les paramètres de zone
    3. Génère les NFT fondateurs
    4. Maintient le registre cadastral
    5. Assure l'équilibre initial ΣV₀ = ΣD₀

    Principe : "Un actif réel = un NFT = un V₀ = un D₀"

    L'Oracle empêche :
    - La double émission (même bien ancré deux fois)
    - La création monétaire ex nihilo (V₀ = D₀ toujours)
    - Les valorisations arbitraires (formule stricte)
    """

    def __init__(self,
                 phi_or_default: float = 1.0,
                 r_zone_default: float = 0.0,
                 phi_auth_officiel: float = 1.0,
                 phi_auth_auto: float = 0.85):
        """
        Initialise l'Oracle

        Args:
            phi_or_default: Facteur or de zone par défaut
            r_zone_default: Risque de zone par défaut (en %)
            phi_auth_officiel: Facteur authentification flux officiel (1.0)
            phi_auth_auto: Facteur authentification flux auto-intégratif (0.85 par défaut)
        """
        self.phi_or_default = phi_or_default
        self.r_zone_default = r_zone_default
        self.phi_auth_officiel = phi_auth_officiel
        self.phi_auth_auto = phi_auth_auto

        # Registre cadastral : hash_nft -> NFTMetadata
        self.registre_cadastral: Dict[str, NFTMetadata] = {}

        # Index par asset_id pour vérification rapide
        self.asset_id_index: Dict[str, str] = {}  # asset_id -> hash_nft

        # Statistiques
        self.total_emissions = 0
        self.total_rejections = 0
        self.total_V_emis = 0.0
        self.total_D_emis = 0.0

    def generate_nft_hash(self,
                          asset_id: str,
                          owner_id: str,
                          valeur_estimee: float,
                          timestamp: int) -> str:
        """
        Génère le hash SHA-256 unique du NFT fondateur

        Le hash est calculé sur :
        - ID de l'actif
        - ID du propriétaire
        - Valeur estimée
        - Timestamp d'émission

        Cela garantit l'unicité cryptographique du NFT.

        Args:
            asset_id: Identifiant unique de l'actif
            owner_id: Identifiant du propriétaire
            valeur_estimee: Valeur estimée de l'actif
            timestamp: Timestamp d'émission

        Returns:
            Hash SHA-256 hexadécimal (64 caractères)
        """
        data = f"{asset_id}|{owner_id}|{valeur_estimee}|{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_uniqueness(self, asset_id: str) -> bool:
        """
        Vérifie qu'un actif n'est pas déjà ancré dans le système

        Protection anti-doublon : un bien réel ne peut être ancré qu'une fois.

        Args:
            asset_id: Identifiant de l'actif à vérifier

        Returns:
            True si l'actif est unique, False s'il existe déjà
        """
        return asset_id not in self.asset_id_index

    def calculate_V0(self,
                    valeur_estimee: float,
                    flux_type: FluxType = FluxType.OFFICIEL,
                    phi_or: Optional[float] = None,
                    r_zone: Optional[float] = None,
                    phi_auth: Optional[float] = None) -> float:
        """
        Calcule V₀ selon la formule IRIS

        Formule :
        V₀ = Valeur_estimée × Φ_or × (1 − r_zone/100) × Φ_auth

        Cette formule intègre :
        - La parité or locale (Φ_or)
        - Le risque géopolitique/climatique (r_zone)
        - Le niveau d'authentification (Φ_auth)

        Args:
            valeur_estimee: Valeur estimée de l'actif (en monnaie locale)
            flux_type: Type de flux (officiel ou auto-intégratif)
            phi_or: Facteur or (défaut: self.phi_or_default)
            r_zone: Risque de zone en % (défaut: self.r_zone_default)
            phi_auth: Facteur authentification (défaut: selon flux_type)

        Returns:
            V₀ : Verum d'initialisation
        """
        # Paramètres par défaut
        if phi_or is None:
            phi_or = self.phi_or_default
        if r_zone is None:
            r_zone = self.r_zone_default
        if phi_auth is None:
            phi_auth = (self.phi_auth_officiel if flux_type == FluxType.OFFICIEL
                       else self.phi_auth_auto)

        # Calcul V₀
        V0 = valeur_estimee * phi_or * (1 - r_zone/100) * phi_auth

        return V0

    def emit_asset(self,
                   asset_id: str,
                   asset_type: str,
                   owner_id: str,
                   valeur_estimee: float,
                   flux_type: FluxType = FluxType.OFFICIEL,
                   phi_or: Optional[float] = None,
                   r_zone: Optional[float] = None,
                   phi_auth: Optional[float] = None,
                   timestamp: Optional[int] = None) -> Tuple[bool, Optional[NFTMetadata], str]:
        """
        Émet un nouvel actif dans le système IRIS (procédure d'émission cadastrale)

        Cette fonction est LE CŒUR de l'Oracle. Elle :
        1. Vérifie l'unicité de l'actif (anti-doublon)
        2. Calcule V₀ et D₀ (V₀ = D₀ toujours)
        3. Génère le NFT fondateur
        4. Enregistre dans le cadastre

        Args:
            asset_id: Identifiant unique de l'actif
            asset_type: Type d'actif (immobilier, mobilier, etc.)
            owner_id: Identifiant du propriétaire
            valeur_estimee: Valeur estimée de l'actif
            flux_type: Type de flux (officiel ou auto-intégratif)
            phi_or: Facteur or (optionnel)
            r_zone: Risque de zone (optionnel)
            phi_auth: Facteur authentification (optionnel)
            timestamp: Timestamp d'émission (optionnel, généré si absent)

        Returns:
            Tuple (success, nft_metadata, message)
            - success: True si émission réussie
            - nft_metadata: Métadonnées du NFT si success=True, None sinon
            - message: Message d'information ou d'erreur
        """
        # Vérification unicité
        if not self.verify_uniqueness(asset_id):
            self.total_rejections += 1
            return (False, None, f"REJET: Actif {asset_id} déjà ancré dans le système (doublon)")

        # Timestamp
        if timestamp is None:
            timestamp = int(time.time())

        # Calcul V₀
        V0 = self.calculate_V0(valeur_estimee, flux_type, phi_or, r_zone, phi_auth)

        # D₀ = V₀ (équilibre initial fondamental)
        D0 = V0

        # Génération NFT hash
        hash_nft = self.generate_nft_hash(asset_id, owner_id, valeur_estimee, timestamp)

        # Paramètres effectifs utilisés
        phi_or_eff = phi_or if phi_or is not None else self.phi_or_default
        r_zone_eff = r_zone if r_zone is not None else self.r_zone_default
        phi_auth_eff = phi_auth if phi_auth is not None else (
            self.phi_auth_officiel if flux_type == FluxType.OFFICIEL else self.phi_auth_auto
        )

        # Création métadonnées NFT
        nft_metadata = NFTMetadata(
            asset_id=asset_id,
            asset_type=asset_type,
            owner_id=owner_id,
            valeur_estimee=valeur_estimee,
            V_initial=V0,
            D_initial=D0,
            phi_or=phi_or_eff,
            r_zone=r_zone_eff,
            phi_auth=phi_auth_eff,
            flux_type=flux_type,
            timestamp=timestamp,
            hash_nft=hash_nft,
            verification_status=VerificationStatus.VERIFIED
        )

        # Enregistrement dans le cadastre
        self.registre_cadastral[hash_nft] = nft_metadata
        self.asset_id_index[asset_id] = hash_nft

        # Mise à jour statistiques
        self.total_emissions += 1
        self.total_V_emis += V0
        self.total_D_emis += D0

        return (True, nft_metadata, f"OK: Actif {asset_id} ancré avec succès (V₀={V0:.2f}, NFT={hash_nft[:16]}...)")

    def get_nft_by_asset(self, asset_id: str) -> Optional[NFTMetadata]:
        """
        Récupère les métadonnées NFT d'un actif

        Args:
            asset_id: Identifiant de l'actif

        Returns:
            NFTMetadata si l'actif existe, None sinon
        """
        hash_nft = self.asset_id_index.get(asset_id)
        if hash_nft is None:
            return None
        return self.registre_cadastral.get(hash_nft)

    def verify_equilibrium(self) -> Tuple[bool, float, float]:
        """
        Vérifie l'équilibre fondamental : ΣV₀ = ΣD₀

        C'est la vérification critique du système IRIS.
        L'Oracle doit TOUJOURS maintenir cet équilibre.

        Returns:
            Tuple (equilibrium, total_V, total_D)
            - equilibrium: True si |ΣV - ΣD| < 1e-6
            - total_V: Somme de tous les V₀ émis
            - total_D: Somme de tous les D₀ émis
        """
        equilibrium = abs(self.total_V_emis - self.total_D_emis) < 1e-6
        return (equilibrium, self.total_V_emis, self.total_D_emis)

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques de l'Oracle

        Returns:
            Dictionnaire avec les statistiques d'émission
        """
        equilibrium, total_V, total_D = self.verify_equilibrium()

        return {
            'total_emissions': self.total_emissions,
            'total_rejections': self.total_rejections,
            'total_V_emis': total_V,
            'total_D_emis': total_D,
            'equilibrium': equilibrium,
            'taux_acceptation': (self.total_emissions / (self.total_emissions + self.total_rejections) * 100)
                               if (self.total_emissions + self.total_rejections) > 0 else 0.0,
            'assets_registered': len(self.registre_cadastral)
        }

    def emission_cadastrale_batch(self,
                                 assets_data: List[Dict]) -> Tuple[int, int, List[NFTMetadata]]:
        """
        Émission cadastrale en lot (pour initialisation ou migration)

        Permet d'ancrer plusieurs actifs d'un coup, typique lors de :
        - L'initialisation d'une nouvelle zone IRIS
        - La migration d'un système existant
        - Un cadastre officiel massif

        Args:
            assets_data: Liste de dictionnaires contenant les données d'actifs
                        Chaque dict doit avoir : asset_id, asset_type, owner_id, valeur_estimee
                        (+ optionnels : flux_type, phi_or, r_zone, phi_auth)

        Returns:
            Tuple (successes, rejections, nft_list)
            - successes: Nombre d'émissions réussies
            - rejections: Nombre de rejets
            - nft_list: Liste des NFTMetadata créés
        """
        successes = 0
        rejections = 0
        nft_list = []

        for asset_data in assets_data:
            success, nft, msg = self.emit_asset(
                asset_id=asset_data['asset_id'],
                asset_type=asset_data['asset_type'],
                owner_id=asset_data['owner_id'],
                valeur_estimee=asset_data['valeur_estimee'],
                flux_type=asset_data.get('flux_type', FluxType.OFFICIEL),
                phi_or=asset_data.get('phi_or'),
                r_zone=asset_data.get('r_zone'),
                phi_auth=asset_data.get('phi_auth'),
                timestamp=asset_data.get('timestamp')
            )

            if success:
                successes += 1
                nft_list.append(nft)
            else:
                rejections += 1

        return (successes, rejections, nft_list)
