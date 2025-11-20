"""
IRIS Economic System - Catastrophes Module
============================================

Module de gestion des catastrophes et chocs aleatoires pour tester la resilience
du systeme IRIS sur le long terme.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Types de catastrophes :
- Naturelles : tremblements de terre, inondations, pandemies
- Economiques : krachs boursiers, pics d'inflation, crises de liquidite
- Politiques : guerres, changements de regime, sanctions
- Technologiques : cyberattaques, pannes systemiques

Echelles :
- Locale : affecte 10-20% de la population
- Regionale : affecte 30-50% de la population
- Globale : affecte 80-100% de la population
"""

import numpy as np
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass


class CatastropheType(Enum):
    """Types de catastrophes possibles"""
    # Catastrophes naturelles
    EARTHQUAKE = "tremblement_de_terre"
    FLOOD = "inondation"
    PANDEMIC = "pandemie"
    DROUGHT = "secheresse"

    # Catastrophes economiques
    MARKET_CRASH = "krach_boursier"
    INFLATION_SPIKE = "pic_inflation"
    LIQUIDITY_CRISIS = "crise_liquidite"
    BANKING_CRISIS = "crise_bancaire"

    # Catastrophes politiques
    WAR = "guerre"
    REGIME_CHANGE = "changement_regime"
    SANCTIONS = "sanctions"
    CIVIL_UNREST = "troubles_civils"

    # Catastrophes technologiques
    CYBERATTACK = "cyberattaque"
    SYSTEM_FAILURE = "panne_systemique"
    DATA_BREACH = "violation_donnees"


class CatastropheScale(Enum):
    """Echelles d'impact des catastrophes"""
    LOCAL = "locale"       # 10-20% de la population
    REGIONAL = "regionale"  # 30-50% de la population
    GLOBAL = "globale"      # 80-100% de la population


@dataclass
class CatastropheEvent:
    """
    Represente un evenement catastrophique

    Attributes:
        catastrophe_type: Type de catastrophe
        scale: Echelle d'impact
        year: Annee de l'evenement
        magnitude: Intensite (0.0 - 1.0)
        affected_agents: Pourcentage d'agents affectes
        duration: Duree en annees
    """
    catastrophe_type: CatastropheType
    scale: CatastropheScale
    year: int
    magnitude: float  # 0.0 - 1.0
    affected_agents: float  # Pourcentage (0.0 - 1.0)
    duration: int  # En annees

    def __str__(self):
        return (f"{self.catastrophe_type.value} ({self.scale.value}) - "
                f"Annee {self.year}, Magnitude {self.magnitude:.2f}, "
                f"Affecte {self.affected_agents*100:.0f}% pendant {self.duration} an(s)")


class CatastropheManager:
    """
    Gere les catastrophes aleatoires pendant la simulation

    Mecanisme :
    - Genere aleatoirement des catastrophes selon une distribution de Poisson
    - Chaque type a une probabilite differente
    - L'impact depend du type, de l'echelle et de la magnitude
    - Les catastrophes peuvent avoir des effets multiples (richesse, production, mortalite)
    """

    def __init__(self,
                 enable_natural: bool = True,
                 enable_economic: bool = True,
                 enable_political: bool = True,
                 enable_technological: bool = True,
                 base_frequency: float = 0.05):
        """
        Initialise le gestionnaire de catastrophes

        Args:
            enable_natural: Active les catastrophes naturelles
            enable_economic: Active les catastrophes economiques
            enable_political: Active les catastrophes politiques
            enable_technological: Active les catastrophes technologiques
            base_frequency: Probabilite de base d'une catastrophe par an (5% par defaut)
        """
        self.enable_natural = enable_natural
        self.enable_economic = enable_economic
        self.enable_political = enable_political
        self.enable_technological = enable_technological
        self.base_frequency = base_frequency

        # Historique des catastrophes
        self.history: List[CatastropheEvent] = []

        # Catastrophes actives (avec duree)
        self.active_events: List[CatastropheEvent] = []

    def should_trigger_catastrophe(self, year: int) -> bool:
        """
        Determine si une catastrophe doit se produire cette annee

        Utilise une distribution de Poisson pour modeliser des evenements rares

        Args:
            year: Annee courante

        Returns:
            True si une catastrophe doit se produire
        """
        # Tire un nombre d'evenements selon Poisson
        n_events = np.random.poisson(self.base_frequency)
        return n_events > 0

    def generate_catastrophe(self, year: int) -> CatastropheEvent:
        """
        Genere une catastrophe aleatoire

        Args:
            year: Annee de l'evenement

        Returns:
            Evenement catastrophique genere
        """
        # Selection du type selon les categories activees
        available_types = []

        if self.enable_natural:
            available_types.extend([
                CatastropheType.EARTHQUAKE,
                CatastropheType.FLOOD,
                CatastropheType.PANDEMIC,
                CatastropheType.DROUGHT
            ])

        if self.enable_economic:
            available_types.extend([
                CatastropheType.MARKET_CRASH,
                CatastropheType.INFLATION_SPIKE,
                CatastropheType.LIQUIDITY_CRISIS,
                CatastropheType.BANKING_CRISIS
            ])

        if self.enable_political:
            available_types.extend([
                CatastropheType.WAR,
                CatastropheType.REGIME_CHANGE,
                CatastropheType.SANCTIONS,
                CatastropheType.CIVIL_UNREST
            ])

        if self.enable_technological:
            available_types.extend([
                CatastropheType.CYBERATTACK,
                CatastropheType.SYSTEM_FAILURE,
                CatastropheType.DATA_BREACH
            ])

        # Tire un type au hasard
        catastrophe_type = np.random.choice(available_types)

        # Tire une echelle (plus probable d'etre locale)
        scale_probs = [0.6, 0.3, 0.1]  # Locale, Regionale, Globale
        scale = np.random.choice(list(CatastropheScale), p=scale_probs)

        # Calcule le pourcentage d'agents affectes selon l'echelle
        if scale == CatastropheScale.LOCAL:
            affected_agents = np.random.uniform(0.10, 0.20)
        elif scale == CatastropheScale.REGIONAL:
            affected_agents = np.random.uniform(0.30, 0.50)
        else:  # GLOBAL
            affected_agents = np.random.uniform(0.80, 1.00)

        # Magnitude aleatoire (distribution beta pour favoriser les catastrophes moderees)
        magnitude = np.random.beta(2, 5)  # Moyenne ~0.3, concentre sur valeurs moderees

        # Duree (la plupart durent 1 an, parfois plus)
        duration = np.random.choice([1, 1, 1, 2, 3], p=[0.6, 0.2, 0.1, 0.05, 0.05])

        event = CatastropheEvent(
            catastrophe_type=catastrophe_type,
            scale=scale,
            year=year,
            magnitude=magnitude,
            affected_agents=affected_agents,
            duration=duration
        )

        return event

    def apply_catastrophe(self,
                         event: CatastropheEvent,
                         agents: Dict,
                         ages: Dict[str, int],
                         economy) -> Dict[str, any]:
        """
        Applique les effets d'une catastrophe sur l'economie

        Effets selon le type :
        - Naturelles : destruction de richesse (V) et mortalite
        - Economiques : perte de liquidite (U), destruction d'actifs
        - Politiques : augmentation dissipation, baisse production
        - Technologiques : perte de donnees (actifs), perturbation systeme

        Args:
            event: Evenement catastrophique
            agents: Dictionnaire des agents
            ages: Dictionnaire des ages
            economy: Instance de l'economie IRIS

        Returns:
            Dictionnaire des impacts {metric: value}
        """
        impacts = {
            'wealth_loss': 0.0,
            'asset_destruction': 0,
            'liquidity_loss': 0.0,
            'deaths': 0,
            'production_impact': 0.0
        }

        # Selection des agents affectes
        agent_ids = list(agents.keys())
        n_affected = int(len(agent_ids) * event.affected_agents)
        affected_ids = np.random.choice(agent_ids, size=n_affected, replace=False)

        # Application des effets selon le type
        if event.catastrophe_type in [CatastropheType.EARTHQUAKE,
                                     CatastropheType.FLOOD,
                                     CatastropheType.DROUGHT]:
            # Catastrophes naturelles : destruction de patrimoine et mortalite
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Perte de patrimoine (V)
                wealth_loss_rate = event.magnitude * 0.5  # Max 50% de perte
                wealth_loss = agent.V_balance * wealth_loss_rate
                agent.V_balance -= wealth_loss
                impacts['wealth_loss'] += wealth_loss

                # Destruction d'actifs
                if agent.assets and np.random.random() < event.magnitude:
                    destroyed_asset = np.random.choice(agent.assets)
                    agent.remove_asset(destroyed_asset.id)
                    impacts['asset_destruction'] += 1

                # Mortalite accrue (seulement si ages disponible)
                if ages and agent_id in ages and ages[agent_id] > 50 and np.random.random() < event.magnitude * 0.1:
                    impacts['deaths'] += 1

        elif event.catastrophe_type == CatastropheType.PANDEMIC:
            # Pandemie : forte mortalite, perte economique
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Mortalite (surtout les ages) - seulement si demographie activee
                if ages and agent_id in ages:
                    age = ages[agent_id]
                    death_risk = event.magnitude * 0.2 * (1 + age / 100)
                    if np.random.random() < death_risk:
                        impacts['deaths'] += 1

                # Perte economique (baisse production)
                production_loss = event.magnitude * 0.3
                impacts['production_impact'] += production_loss

        elif event.catastrophe_type in [CatastropheType.MARKET_CRASH,
                                       CatastropheType.BANKING_CRISIS]:
            # Crises financieres : destruction de valeur d'actifs
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Perte de valeur des actifs
                for asset in agent.assets:
                    value_loss_rate = event.magnitude * 0.4  # Max 40%
                    value_loss = asset.real_value * value_loss_rate
                    asset.real_value -= value_loss
                    impacts['wealth_loss'] += value_loss

        elif event.catastrophe_type in [CatastropheType.INFLATION_SPIKE,
                                       CatastropheType.LIQUIDITY_CRISIS]:
            # Crises de liquidite : perte de U
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Perte de liquidite
                liquidity_loss_rate = event.magnitude * 0.6  # Max 60%
                liquidity_loss = agent.U_balance * liquidity_loss_rate
                agent.U_balance -= liquidity_loss
                impacts['liquidity_loss'] += liquidity_loss

        elif event.catastrophe_type in [CatastropheType.WAR,
                                       CatastropheType.CIVIL_UNREST]:
            # Conflits : destruction massive, mortalite, perturbation economique
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Destruction de richesse
                wealth_loss_rate = event.magnitude * 0.7  # Max 70%
                wealth_loss = (agent.V_balance + agent.U_balance) * wealth_loss_rate
                agent.V_balance -= agent.V_balance * wealth_loss_rate
                agent.U_balance -= agent.U_balance * wealth_loss_rate
                impacts['wealth_loss'] += wealth_loss

                # Mortalite
                if np.random.random() < event.magnitude * 0.15:
                    impacts['deaths'] += 1

                # Perturbation production
                impacts['production_impact'] += event.magnitude * 0.5

        elif event.catastrophe_type in [CatastropheType.REGIME_CHANGE,
                                       CatastropheType.SANCTIONS]:
            # Changements politiques : perturbation economique
            impacts['production_impact'] = event.magnitude * event.affected_agents * 0.4

        elif event.catastrophe_type in [CatastropheType.CYBERATTACK,
                                       CatastropheType.SYSTEM_FAILURE]:
            # Catastrophes technologiques : perte d'actifs, perturbation
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Destruction aleatoire d'actifs (corruption donnees)
                if agent.assets and np.random.random() < event.magnitude * 0.5:
                    destroyed_asset = np.random.choice(agent.assets)
                    agent.remove_asset(destroyed_asset.id)
                    impacts['asset_destruction'] += 1

                # Perturbation economique
                impacts['production_impact'] += event.magnitude * 0.3

        elif event.catastrophe_type == CatastropheType.DATA_BREACH:
            # Violation de donnees : perte de confiance, baisse valeur
            for agent_id in affected_ids:
                agent = agents[agent_id]

                # Baisse du facteur d'authentification des actifs
                for asset in agent.assets:
                    asset.auth_factor *= (1 - event.magnitude * 0.2)
                    impacts['wealth_loss'] += asset.real_value * event.magnitude * 0.2

        return impacts

    def update(self, year: int, agents: Dict, ages: Dict[str, int], economy) -> List[CatastropheEvent]:
        """
        Mise a jour : verifie si des catastrophes se produisent cette annee

        Args:
            year: Annee courante
            agents: Dictionnaire des agents
            ages: Dictionnaire des ages
            economy: Instance de l'economie

        Returns:
            Liste des evenements generes cette annee
        """
        new_events = []

        # Verifie si une catastrophe doit se produire
        if self.should_trigger_catastrophe(year):
            event = self.generate_catastrophe(year)

            # Applique la catastrophe
            impacts = self.apply_catastrophe(event, agents, ages, economy)

            # Enregistre
            self.history.append(event)
            self.active_events.append(event)
            new_events.append(event)

            print(f"\n  [CATASTROPHE] {event}")
            print(f"    Impacts: Richesse perdue={impacts['wealth_loss']:.0f}, "
                  f"Actifs detruits={impacts['asset_destruction']}, "
                  f"Deces={impacts['deaths']}")

        # Decremente la duree des evenements actifs
        self.active_events = [
            e for e in self.active_events
            if e.year + e.duration > year
        ]

        return new_events

    def get_statistics(self) -> Dict[str, any]:
        """
        Calcule les statistiques sur les catastrophes

        Returns:
            Dictionnaire de statistiques
        """
        if not self.history:
            return {
                'total_events': 0,
                'by_type': {},
                'by_scale': {},
                'avg_magnitude': 0.0
            }

        # Compte par type
        by_type = {}
        for event in self.history:
            type_name = event.catastrophe_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1

        # Compte par echelle
        by_scale = {}
        for event in self.history:
            scale_name = event.scale.value
            by_scale[scale_name] = by_scale.get(scale_name, 0) + 1

        # Magnitude moyenne
        avg_magnitude = np.mean([e.magnitude for e in self.history])

        return {
            'total_events': len(self.history),
            'by_type': by_type,
            'by_scale': by_scale,
            'avg_magnitude': avg_magnitude
        }
