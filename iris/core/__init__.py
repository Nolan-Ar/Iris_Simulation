"""
IRIS Core - IRIS V2 Economic System
====================================

IRIS (Integrative Resilience Intelligent System) V2 - Agent-based,
thermodynamically coherent economic simulation system.

Main Modules:
- iris_model: Main IRIS engine (IRISEconomy class)
- iris_demographics: Demographics system (births, deaths, inheritance)
- iris_entreprises: Enterprise system (production, combustion)
- iris_comptes_entreprises: Enterprise accounting
- iris_rad: RAD thermodynamic regulator (κ, η, θ, D components)
- iris_oracle: Oracle/Exchange system
- iris_prix: Price system
- iris_catastrophes: Catastrophes system
- iris_chambre_relance: Governance and stimulus chamber
- iris_validation: Validation utilities
- iris_scenarios: Scenario definitions

Key Concepts:
- V (Verum): Long-term patrimonial value
- U (Usage): Short-term liquidity
- S (Stock): Material/biomass stocks
- D (Debt mirror): Thermodynamic mirror with multiple components
- θ (theta): Thermometer = D_total / V_on
- κ (kappa): Regulates V↔U conversions (countercyclical)
- η (eta): Regulates S+U→V combustion (countercyclical)
- RU: Universal income
- TAP: Temporary Advance on Pay (staking mechanism)
- NFT: Financial contracts
- Φ_trust: Reputation/trust score

Architecture:
Agent-based with rich individual behaviors, multiple wallet types,
staking, TAP, NFT contracts, and governance mechanisms.

Version: 2.0 (Legacy - Fully Featured)
Author: Arnault Nolan
"""

# V2 Core Modules
from .iris_model import (
    IRISEconomy,
    Agent,
    Asset,
    AssetType,
    DebtComponent,
    RADState,
)
from .iris_demographics import Demographics
from .iris_entreprises import (
    EntrepriseManager,
    EntrepriseStatus,
    EntrepriseMetrics,
)
from .iris_comptes_entreprises import (
    RegistreComptesEntreprises,
    CompteEntreprise,
    NFTFinancier,
    FluxEntreprise,
    BusinessType,
)
from .iris_rad import RADState as RAD
from .iris_oracle import (
    Oracle,
    NFTMetadata,
    FluxType,
    VerificationStatus,
)
from .iris_prix import (
    PriceManager,
    Good,
    GoodType,
    MarketData,
)
from .iris_catastrophes import (
    CatastropheManager,
    CatastropheEvent,
    CatastropheType,
    CatastropheScale,
)
from .iris_chambre_relance import (
    ChambreRelance,
    OrphanAsset,
    OrphanReason,
    RedistributionEvent,
)
from .iris_validation import (
    IRISValidator,
    MonteCarloResults,
    SensitivityResults,
)
from .iris_scenarios import ScenarioRunner

__all__ = [
    # Main model
    'IRISEconomy',
    'Agent',
    'Asset',
    'AssetType',
    'DebtComponent',
    'RADState',

    # Core components
    'Demographics',
    'EntrepriseManager',
    'EntrepriseStatus',
    'EntrepriseMetrics',
    'RegistreComptesEntreprises',
    'CompteEntreprise',
    'NFTFinancier',
    'FluxEntreprise',
    'BusinessType',
    'RAD',
    'Oracle',
    'NFTMetadata',
    'FluxType',
    'VerificationStatus',
    'PriceManager',
    'Good',
    'GoodType',
    'MarketData',
    'CatastropheManager',
    'CatastropheEvent',
    'CatastropheType',
    'CatastropheScale',
    'ChambreRelance',
    'OrphanAsset',
    'OrphanReason',
    'RedistributionEvent',
    'IRISValidator',
    'MonteCarloResults',
    'SensitivityResults',
    'ScenarioRunner',
]

__version__ = '2.0.0'
