"""
IRIS Economic System - Demographics Module
==========================================

Module de démographie pour la simulation IRIS sur le long terme.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Mécanismes démographiques :
- Naissance d'agents (taux de natalité)
- Mort d'agents (espérance de vie)
- Vieillissement de la population
- Transmission de patrimoine (héritage)
- Création de nouveaux actifs
"""

import numpy as np
from typing import Dict, List
from .iris_model import Agent, Asset, AssetType


class Demographics:
    """
    Gère la démographie de la population IRIS

    Paramètres réalistes :
    - Espérance de vie : ~80 ans
    - Taux de natalité : ~1.5% par an
    - Âge de reproduction : 20-45 ans
    - Âge de retraite : 65 ans
    """

    def __init__(self,
                 life_expectancy: float = 80.0,
                 birth_rate: float = 0.0414,
                 min_reproduction_age: int = 18,
                 max_reproduction_age: int = 50,
                 retirement_age: int = 65,
                 wealth_influence: bool = True,
                 max_population: int = 10000,
                 consumption_D_per_year: float = 0.5):
        """
        Initialise le module démographique

        Args:
            life_expectancy: Espérance de vie en années
            birth_rate: Taux de natalité annuel (4.14% calibré: 4069→~6900 agents, âge moyen ~35 ans sur 80 ans sans catastrophes)
            min_reproduction_age: Âge minimum de reproduction
            max_reproduction_age: Âge maximum de reproduction
            retirement_age: Âge de la retraite
            wealth_influence: Si True, la richesse influence natalité/mortalité
            max_population: Population maximale (0 = illimité, >0 = plafond activé, défaut: 10000)
            consumption_D_per_year: Quantité de D de consommation par an et par personne
        """
        self.life_expectancy = life_expectancy
        self.birth_rate = birth_rate
        self.min_reproduction_age = min_reproduction_age
        self.max_reproduction_age = max_reproduction_age
        self.retirement_age = retirement_age
        self.wealth_influence = wealth_influence
        self.max_population = max_population

        # NEW : quantité de D de consommation générée par an et par personne
        self.consumption_D_per_year = float(consumption_D_per_year)

        # Compteurs pour statistiques
        self.total_births = 0
        self.total_deaths = 0
        self.next_agent_id = 0

    def initialize_ages(self, agents: Dict[str, Agent]) -> Dict[str, int]:
        """
        Initialise les âges de tous les agents (distribution réaliste)

        Distribution pyramide des âges :
        - Beaucoup de jeunes (0-30 ans)
        - Population active (30-65 ans)
        - Retraités (65-80 ans)

        Args:
            agents: Dictionnaire des agents

        Returns:
            Dictionnaire {agent_id: age}
        """
        ages = {}

        for agent_id in agents.keys():
            # Distribution triangulaire : population plus âgée pour âge moyen proche de 38 ans
            # Mode à 51 ans (au lieu de 30) pour vieillir la population
            age = int(np.random.triangular(0, 51, self.life_expectancy))
            ages[agent_id] = age

        return ages

    def age_population(self, ages: Dict[str, int]) -> Dict[str, int]:
        """
        Vieillit toute la population d'un an

        Args:
            ages: Dictionnaire des âges actuels

        Returns:
            Dictionnaire des âges mis à jour
        """
        # Tout le monde vieillit d'un an
        return {agent_id: age + 1 for agent_id, age in ages.items()}

    def _calculate_wealth_modifier(self,
                                   agent: Agent,
                                   avg_wealth: float) -> float:
        """
        Calcule un modificateur basé sur la richesse relative de l'agent

        Agent plus riche que la moyenne → meilleure santé, plus de naissances
        Agent plus pauvre → santé précaire, moins de naissances

        Args:
            agent: Agent concerné
            avg_wealth: Richesse moyenne de la population

        Returns:
            Modificateur entre 0.5 (très pauvre) et 1.5 (très riche)
        """
        if not self.wealth_influence or avg_wealth == 0:
            return 1.0

        # Richesse totale de l'agent
        agent_wealth = agent.V_balance + agent.U_balance

        # Sécurité : éviter les richesses négatives
        agent_wealth = max(0.0, agent_wealth)

        # Ratio richesse relative
        wealth_ratio = agent_wealth / max(avg_wealth, 1.0)

        # Sécurité : s'assurer que wealth_ratio est positif et fini
        wealth_ratio = max(0.0, wealth_ratio)
        if not np.isfinite(wealth_ratio):
            return 1.0

        # Modification logarithmique (évite les extrêmes)
        # Réduit l'influence de la richesse pour éviter spirale de pauvreté
        # wealth_ratio = 0.1 → modifier ≈ 0.85
        # wealth_ratio = 1.0 → modifier = 1.0
        # wealth_ratio = 10.0 → modifier ≈ 1.15
        modifier = 0.7 + 0.3 * np.log(wealth_ratio + 1) / np.log(11)

        # Clamp entre 0.7 et 1.3 (réduit l'écart)
        return np.clip(modifier, 0.7, 1.3)

    def process_deaths(self,
                       agents: Dict[str, Agent],
                       ages: Dict[str, int],
                       year: int) -> List[str]:
        """
        Gère les morts d'agents selon deux composantes distinctes

        NOUVEAU MODÈLE DE MORTALITÉ :
        1. Mortalité par maladie (liée principalement à l'âge) :
           - < 60 ans : 0.1%/an
           - 60-70 ans : 0.4%/an
           - 70-80 ans : 1.8%/an
           - 80-90 ans : 6%/an
           - > 90 ans : 15%/an
           - Modulée par richesse : riche vit mieux, pauvre a moins d'accès aux soins

        2. Mortalité par accident/précarité (liée principalement à la pauvreté) :
           - Base : 0.1%/an
           - Fortement augmentée par pauvreté (ratio pauvre/riche jusqu'à 3x)
           - Légèrement augmentée par l'âge

        Args:
            agents: Dictionnaire des agents
            ages: Dictionnaire des âges
            year: Année courante (pour stats)

        Returns:
            Liste des IDs des agents décédés
        """
        deceased = []

        # Calcul de la richesse moyenne (pour modificateur)
        if self.wealth_influence:
            total_wealth = sum(a.V_balance + a.U_balance for a in agents.values())
            avg_wealth = total_wealth / max(len(agents), 1)
        else:
            avg_wealth = 0.0

        for agent_id, age in list(ages.items()):
            agent = agents[agent_id]

            # === COMPOSANTE 1 : MORTALITÉ PAR MALADIE (liée à l'âge) ===
            # Probabilité de base selon l'âge (très réduite pour augmenter âge moyen à ~38 ans)
            if age < 60:
                base_disease = 0.001   # 0.1% / an
            elif age < 70:
                base_disease = 0.003   # 0.3% / an (réduit de 0.4%)
            elif age < 80:
                base_disease = 0.012   # 1.2% / an (réduit de 1.8%)
            elif age < 90:
                base_disease = 0.03    # 3% / an (réduit de 4%)
            else:
                base_disease = 0.08    # 8% / an (réduit de 10%)

            # Calcul du facteur de richesse
            if self.wealth_influence:
                wealth = agent.V_balance + agent.U_balance
                wealth = max(wealth, 1e-6)
                wealth_factor = np.clip(wealth / (avg_wealth + 1e-6), 0.3, 1.7)

                # Riche → moins de maladie ; pauvre → plus
                p_disease = base_disease * (2.0 - wealth_factor)
            else:
                p_disease = base_disease

            # === COMPOSANTE 2 : MORTALITÉ PAR ACCIDENT/PRÉCARITÉ (liée à la pauvreté) ===
            p_accident_base = 0.001  # 0.1% / an de base

            if self.wealth_influence:
                # Plus wealth est faible, plus poverty_ratio est grand
                poverty_ratio = np.clip((avg_wealth + 1e-6) / wealth, 0.5, 3.0)

                # Accidents un peu plus probables chez les plus âgés
                age_factor = 1.0 + (age / 100.0)

                p_accident = p_accident_base * poverty_ratio * age_factor
            else:
                p_accident = p_accident_base

            # === COMBINAISON DES DEUX RISQUES ===
            # Probabilité de survie = (1 - p_disease) × (1 - p_accident)
            p_survival = (1.0 - p_disease) * (1.0 - p_accident)
            p_death = 1.0 - p_survival
            p_death = max(0.0, min(1.0, p_death))

            # Tirage aléatoire
            if np.random.random() < p_death:
                deceased.append(agent_id)
                self.total_deaths += 1

        return deceased

    def inherit_wealth(self,
                      deceased_id: str,
                      agents: Dict[str, Agent],
                      ages: Dict[str, int]) -> str:
        """
        Gère l'héritage : transfert du patrimoine du défunt

        Règles d'héritage :
        - Transfert à un agent plus jeune (simulation enfants)
        - Si pas d'héritier, patrimoine redistribué aléatoirement

        Args:
            deceased_id: ID de l'agent décédé
            agents: Dictionnaire des agents
            ages: Dictionnaire des âges

        Returns:
            ID de l'héritier
        """
        deceased = agents[deceased_id]

        # Cherche un héritier potentiel (plus jeune)
        deceased_age = ages[deceased_id]
        potential_heirs = [
            aid for aid, age in ages.items()
            if age < deceased_age - 20 and aid != deceased_id
        ]

        # S'il y a des héritiers potentiels
        if potential_heirs:
            heir_id = np.random.choice(potential_heirs)
        else:
            # Sinon, héritier aléatoire
            heir_id = np.random.choice([aid for aid in agents.keys() if aid != deceased_id])

        # Transfert du patrimoine
        heir = agents[heir_id]
        heir.V_balance += deceased.V_balance
        heir.U_balance += deceased.U_balance
        heir.assets.extend(deceased.assets)

        return heir_id

    def process_births(self,
                      agents: Dict[str, Agent],
                      ages: Dict[str, int],
                      assets_registry: Dict[str, Asset],
                      year: int) -> List[Agent]:
        """
        Gère les naissances d'agents avec influence de la richesse

        Mécanisme :
        - Agents en âge de procréer (20-45 ans) ont une probabilité de "créer" un nouvel agent
        - Le nouvel agent hérite d'une partie du patrimoine de ses "parents"
        - Simule la création de richesse intergénérationnelle
        - NOUVEAU: La pauvreté augmente le taux de natalité (effet inversé) :
          * Agent pauvre (modifier=0.7) → +86% de naissances (inverse=1.3)
          * Agent riche (modifier=1.3) → -46% de naissances (inverse=0.7)

        Args:
            agents: Dictionnaire des agents
            ages: Dictionnaire des âges
            assets_registry: Registre des actifs
            year: Année courante

        Returns:
            Liste des nouveaux agents créés
        """
        new_agents = []

        # Compte les agents en âge de procréer
        reproductive_agents = [
            agent_id for agent_id, age in ages.items()
            if self.min_reproduction_age <= age <= self.max_reproduction_age
        ]

        # Calcul de la richesse moyenne (pour modificateur)
        if self.wealth_influence:
            total_wealth = sum(a.V_balance + a.U_balance for a in agents.values())
            avg_wealth = total_wealth / max(len(agents), 1)
        else:
            avg_wealth = 0.0

        # Calcul du taux de natalité ajusté par la richesse
        # NOUVEAU: Effet inversé - pauvres ont plus d'enfants, riches moins
        if self.wealth_influence and reproductive_agents:
            # Calcul du modificateur moyen pour les agents reproductifs
            wealth_mods = [
                self._calculate_wealth_modifier(agents[aid], avg_wealth)
                for aid in reproductive_agents
            ]
            # Inversion : riches (1.3) → 0.7, pauvres (0.7) → 1.3
            inverse_mods = [2.0 - m for m in wealth_mods]
            avg_inverse_mod = float(np.mean(inverse_mods)) if inverse_mods else 1.0
            adjusted_birth_rate = self.birth_rate * avg_inverse_mod
        else:
            adjusted_birth_rate = self.birth_rate

        # Sécurité : s'assurer que le taux est positif et valide
        adjusted_birth_rate = max(0.0, float(adjusted_birth_rate))
        if not np.isfinite(adjusted_birth_rate):
            adjusted_birth_rate = self.birth_rate

        # Calcul du nombre de naissances attendues
        expected_births = len(reproductive_agents) * adjusted_birth_rate

        # Sécurité : valider expected_births avant Poisson
        expected_births = max(0.0, float(expected_births))
        if not np.isfinite(expected_births):
            expected_births = 0.0

        # Limiter la croissance pour éviter explosion démographique
        # Plafond à 10% de la population reproductrice par an
        max_births = int(len(reproductive_agents) * 0.1)
        expected_births = min(expected_births, max_births)

        actual_births = np.random.poisson(expected_births) if expected_births > 0 else 0

        # Contrôle de population : limiter aux places disponibles
        if self.max_population > 0:
            current_pop = len(agents)
            available_slots = max(0, self.max_population - current_pop)
            actual_births = min(actual_births, available_slots)
            if actual_births == 0 and current_pop >= self.max_population:
                # Population au maximum, pas de naissances
                return new_agents

        for _ in range(actual_births):
            # Sélectionne un "parent" aléatoire
            if not reproductive_agents:
                break

            parent_id = np.random.choice(reproductive_agents)
            parent = agents[parent_id]

            # Crée le nouvel agent
            new_id = f"agent_{year}_{self.next_agent_id}"
            self.next_agent_id += 1

            new_agent = Agent(id=new_id)

            # Héritage partiel : le nouveau agent reçoit une dotation raisonnable
            # (simule l'aide familiale et la transmission intergénérationnelle)
            inheritance_rate = 0.20  # 20% du patrimoine parental

            # Transfert patrimonial
            inherited_V = parent.V_balance * inheritance_rate
            inherited_U = parent.U_balance * inheritance_rate

            parent.V_balance -= inherited_V
            parent.U_balance -= inherited_U

            new_agent.V_balance = inherited_V
            new_agent.U_balance = inherited_U

            # Le nouvel agent peut aussi créer de petits actifs
            # (simule l'entrée dans la vie active)
            n_initial_assets = np.random.poisson(1.5)  # Quelques actifs au départ

            for j in range(n_initial_assets):
                asset_type = np.random.choice(list(AssetType))
                # CORRECTION: Petites valeurs VRAIMENT petites pour un jeune
                # Ancien: lognormal(8, 1.0) ≈ exp(8) = 3000 (trop élevé!)
                # Nouveau: lognormal(1.5, 0.8) ≈ exp(1.5) = 4.5 (cohérent avec économie)
                real_value = np.random.lognormal(1.5, 0.8)  # Beaucoup plus petit que la moyenne

                asset = Asset(
                    id=f"asset_{new_id}_{j}",
                    asset_type=asset_type,
                    real_value=real_value,
                    owner_id=new_id,
                    auth_factor=1.0,
                    creation_time=year
                )

                new_agent.add_asset(asset)
                assets_registry[asset.id] = asset

            new_agents.append(new_agent)
            self.total_births += 1

        return new_agents

    def get_age_distribution(self, ages: Dict[str, int]) -> Dict[str, int]:
        """
        Calcule la distribution par tranches d'âge

        Args:
            ages: Dictionnaire des âges

        Returns:
            Dictionnaire {tranche: nombre}
        """
        distribution = {
            '0-20': 0,
            '20-40': 0,
            '40-60': 0,
            '60-80': 0,
            '80+': 0
        }

        for age in ages.values():
            if age < 20:
                distribution['0-20'] += 1
            elif age < 40:
                distribution['20-40'] += 1
            elif age < 60:
                distribution['40-60'] += 1
            elif age < 80:
                distribution['60-80'] += 1
            else:
                distribution['80+'] += 1

        return distribution

    def get_statistics(self, ages: Dict[str, int]) -> Dict[str, float]:
        """
        Calcule les statistiques démographiques

        Args:
            ages: Dictionnaire des âges

        Returns:
            Dictionnaire de statistiques
        """
        ages_list = list(ages.values())

        return {
            'population': len(ages),
            'age_moyen': np.mean(ages_list) if ages_list else 0,
            'age_median': np.median(ages_list) if ages_list else 0,
            'age_min': min(ages_list) if ages_list else 0,
            'age_max': max(ages_list) if ages_list else 0,
            'total_naissances': self.total_births,
            'total_deces': self.total_deaths,
            'taux_croissance': (self.total_births - self.total_deaths) / max(1, self.total_births + self.total_deaths)
        }

    def process_vectorized(self, population, current_year: int, rng=None):
        """
        Traite la démographie en mode vectorisé (vieillissement, morts, naissances)

        Cette méthode remplace process_deaths, age_population et process_births
        en mode vectorisé. Elle opère directement sur les arrays NumPy de la
        VectorizedPopulation.

        Args:
            population: Instance de VectorizedPopulation
            current_year: Année courante de la simulation
            rng: Générateur aléatoire NumPy (si None, utilise default_rng)

        Returns:
            Tuple (nb_births, nb_deaths) pour les statistiques
        """
        if rng is None:
            rng = np.random.default_rng()

        # === VIEILLISSEMENT ===
        # Utilise la méthode optimisée age_one_year()
        population.age_one_year()

        # === MORTALITÉ ===
        nb_deaths = 0
        alive_mask = population.is_alive
        alive_indices = np.where(alive_mask)[0]

        if len(alive_indices) > 0:
            # Calcul de la richesse moyenne pour les modificateurs
            alive_wealth = population.wealth[alive_indices]
            avg_wealth = float(np.mean(alive_wealth)) if len(alive_wealth) > 0 else 1.0

            ages = population.age[alive_indices]
            wealth = population.wealth[alive_indices]

            # === COMPOSANTE 1 : MORTALITÉ PAR MALADIE (liée à l'âge) ===
            base_disease = np.zeros_like(ages)
            base_disease[ages < 60] = 0.001
            base_disease[(ages >= 60) & (ages < 70)] = 0.003
            base_disease[(ages >= 70) & (ages < 80)] = 0.012
            base_disease[(ages >= 80) & (ages < 90)] = 0.03
            base_disease[ages >= 90] = 0.08

            if self.wealth_influence:
                # Facteur de richesse : riche vit mieux, pauvre souffre plus
                wealth_factor = np.clip(wealth / (avg_wealth + 1e-6), 0.3, 1.7)
                p_disease = base_disease * (2.0 - wealth_factor)
            else:
                p_disease = base_disease

            # === COMPOSANTE 2 : MORTALITÉ PAR ACCIDENT/PRÉCARITÉ ===
            p_accident_base = 0.001

            if self.wealth_influence:
                # Pauvreté augmente les accidents
                poverty_ratio = np.clip((avg_wealth + 1e-6) / (wealth + 1e-6), 0.5, 3.0)
                age_factor = 1.0 + (ages / 100.0)
                p_accident = p_accident_base * poverty_ratio * age_factor
            else:
                p_accident = np.full_like(ages, p_accident_base)

            # === COMBINAISON DES RISQUES ===
            p_survival = (1.0 - p_disease) * (1.0 - p_accident)
            p_death = 1.0 - p_survival
            p_death = np.clip(p_death, 0.0, 1.0)

            # Tirage aléatoire vectorisé
            death_rolls = rng.random(len(alive_indices))
            deaths_mask = death_rolls < p_death

            # Application des morts
            dead_indices = alive_indices[deaths_mask]
            population.is_alive[dead_indices] = False
            nb_deaths = len(dead_indices)
            self.total_deaths += nb_deaths

            # En mode vectorisé, on ne transfère pas l'héritage individuellement
            # On redistribue la richesse des morts proportionnellement aux vivants
            if nb_deaths > 0:
                total_V_dead = float(population.V[dead_indices].sum())
                total_U_dead = float(population.U[dead_indices].sum())

                # Marque la richesse des morts à 0
                population.V[dead_indices] = 0.0
                population.U[dead_indices] = 0.0

                # Redistribue aux vivants proportionnellement à leur richesse
                new_alive_mask = population.is_alive
                new_alive_indices = np.where(new_alive_mask)[0]

                if len(new_alive_indices) > 0:
                    alive_wealth_total = population.wealth[new_alive_indices].sum()
                    if alive_wealth_total > 0:
                        # Redistribution proportionnelle
                        wealth_shares = population.wealth[new_alive_indices] / alive_wealth_total
                        population.V[new_alive_indices] += total_V_dead * wealth_shares
                        population.U[new_alive_indices] += total_U_dead * wealth_shares
                    else:
                        # Distribution égale si pas de richesse
                        population.V[new_alive_indices] += total_V_dead / len(new_alive_indices)
                        population.U[new_alive_indices] += total_U_dead / len(new_alive_indices)

        # === NAISSANCES ===
        nb_births = 0
        alive_mask = population.is_alive
        alive_indices = np.where(alive_mask)[0]

        if len(alive_indices) > 0:
            ages = population.age[alive_indices]

            # Agents en âge de procréer
            reproductive_mask = (ages >= self.min_reproduction_age) & (ages <= self.max_reproduction_age)
            reproductive_indices = alive_indices[reproductive_mask]

            if len(reproductive_indices) > 0:
                # Calcul de la richesse moyenne
                alive_wealth_total = population.wealth[alive_indices]
                avg_wealth = float(np.mean(alive_wealth_total)) if len(alive_wealth_total) > 0 else 1.0

                # Taux de natalité ajusté par richesse (effet inversé)
                if self.wealth_influence:
                    reproductive_wealth = population.wealth[reproductive_indices]
                    wealth_ratios = reproductive_wealth / max(avg_wealth, 1.0)
                    wealth_ratios = np.clip(wealth_ratios, 0.0, 10.0)

                    # Modificateurs de richesse
                    wealth_mods = 0.7 + 0.3 * np.log(wealth_ratios + 1) / np.log(11)
                    wealth_mods = np.clip(wealth_mods, 0.7, 1.3)

                    # Inversion : pauvres ont plus d'enfants
                    inverse_mods = 2.0 - wealth_mods
                    avg_inverse_mod = float(np.mean(inverse_mods))
                    adjusted_birth_rate = self.birth_rate * avg_inverse_mod
                else:
                    adjusted_birth_rate = self.birth_rate

                adjusted_birth_rate = max(0.0, float(adjusted_birth_rate))

                # Nombre de naissances attendues
                expected_births = len(reproductive_indices) * adjusted_birth_rate
                max_births = int(len(reproductive_indices) * 0.1)
                expected_births = min(expected_births, max_births)

                # Contrôle de population
                current_pop = int(population.is_alive.sum())
                if self.max_population > 0:
                    available_slots = max(0, self.max_population - current_pop)
                    expected_births = min(expected_births, available_slots)

                # Tirage du nombre de naissances
                actual_births = rng.poisson(expected_births) if expected_births > 0 else 0
                actual_births = int(actual_births)

                if actual_births > 0 and current_pop < population.n_agents:
                    # Trouve les slots disponibles (agents morts qu'on peut réutiliser)
                    dead_mask = ~population.is_alive
                    dead_indices = np.where(dead_mask)[0]

                    # Limite au nombre de slots disponibles
                    actual_births = min(actual_births, len(dead_indices))

                    if actual_births > 0:
                        # Sélectionne des parents aléatoirement
                        parent_indices = rng.choice(reproductive_indices, size=actual_births, replace=True)

                        # Réutilise les indices des morts pour les nouveaux nés
                        newborn_indices = dead_indices[:actual_births]

                        # Initialisation des nouveaux-nés
                        population.is_alive[newborn_indices] = True
                        population.age[newborn_indices] = 0.0

                        # Héritage partiel des parents (20%)
                        inheritance_rate = 0.20
                        inherited_V = population.V[parent_indices] * inheritance_rate
                        inherited_U = population.U[parent_indices] * inheritance_rate

                        # Transfert de richesse
                        population.V[parent_indices] -= inherited_V
                        population.U[parent_indices] -= inherited_U
                        population.V[newborn_indices] = inherited_V
                        population.U[newborn_indices] = inherited_U
                        population.S[newborn_indices] = 0.0

                        nb_births = actual_births
                        self.total_births += nb_births

        # Mise à jour de la richesse totale
        population.update_wealth()

        return nb_births, nb_deaths
