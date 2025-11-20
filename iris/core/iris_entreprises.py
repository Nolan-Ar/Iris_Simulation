"""
IRIS v2.1 - Entreprises Évolutives (Créations/Faillites)
==========================================================

Module de gestion dynamique des entreprises avec créations, croissance et faillites.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025

Principes :
-----------
1. CRÉATION : Nouvelles entreprises émergent (entrepreneurs, innovation)
2. CROISSANCE : Entreprises prospères augmentent leur V_entreprise
3. FAILLITE : Entreprises non viables disparaissent
4. CYCLE DE VIE : Naissance → Croissance → Maturité → Déclin/Faillite

Mécanismes :
-----------
CRÉATION D'ENTREPRISE :
- Taux de création basé sur la richesse des agents
- Apport initial en V (capital de départ)
- Type d'entreprise aléatoire ou choisi

CROISSANCE :
- Revenus (V généré) → Augmentation V_entreprise
- Seuil de rentabilité : V_généré > Coûts fixes
- Expansion : V_entreprise × (1 + taux_croissance)

FAILLITE :
- Solvabilité : Si V_operationnel < 0 pendant N cycles → faillite
- Rentabilité : Si V_généré trop faible pendant N cycles → faillite
- Catastrophes : Destruction V_entreprise → faillite
- Liquidation : Actifs redistribués (Chambre de Relance)

Statistiques :
-------------
- Nombre d'entreprises actives
- Taux de création/faillite
- Espérance de vie des entreprises
- Distribution par secteur
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from iris.core.iris_comptes_entreprises import (
    CompteEntreprise, BusinessType, RegistreComptesEntreprises, NFTFinancier
)


class EntrepriseStatus(Enum):
    """Statut d'une entreprise"""
    CREATION = "creation"  # Vient d'être créée
    CROISSANCE = "croissance"  # En phase de croissance
    MATURITE = "maturite"  # Phase mature
    DECLIN = "declin"  # En déclin
    FAILLITE = "faillite"  # En faillite


@dataclass
class EntrepriseMetrics:
    """
    Métriques de performance d'une entreprise

    Utilisées pour détecter croissance ou déclin.
    """
    business_id: str
    age: int = 0  # Âge en cycles
    V_genere_total: float = 0.0  # V total généré
    V_genere_recent: List[float] = field(default_factory=list)  # Derniers cycles
    cycles_deficit: int = 0  # Nombre de cycles en déficit
    cycles_survie: int = 0  # Cycles depuis création
    status: EntrepriseStatus = EntrepriseStatus.CREATION

    def add_V_genere(self, V_genere: float):
        """Enregistre un V généré"""
        self.V_genere_total += V_genere
        self.V_genere_recent.append(V_genere)

        # Garde seulement les 12 derniers cycles (1 an)
        if len(self.V_genere_recent) > 12:
            self.V_genere_recent.pop(0)

    def get_V_moyen_recent(self) -> float:
        """Retourne le V généré moyen récent"""
        if not self.V_genere_recent:
            return 0.0
        return np.mean(self.V_genere_recent)

    def is_rentable(self, seuil_rentabilite: float) -> bool:
        """
        Vérifie si l'entreprise est rentable

        Args:
            seuil_rentabilite: V minimum à générer par cycle

        Returns:
            True si rentable
        """
        V_moyen = self.get_V_moyen_recent()
        return V_moyen >= seuil_rentabilite

    def update_status(self, seuil_rentabilite: float):
        """
        Met à jour le statut selon les performances

        Args:
            seuil_rentabilite: Seuil de rentabilité
        """
        V_moyen = self.get_V_moyen_recent()

        if self.age < 12:
            # Phase de création (première année)
            self.status = EntrepriseStatus.CREATION
        elif V_moyen > seuil_rentabilite * 1.5:
            # Forte rentabilité → croissance
            self.status = EntrepriseStatus.CROISSANCE
        elif V_moyen > seuil_rentabilite:
            # Rentabilité normale → maturité
            self.status = EntrepriseStatus.MATURITE
        elif V_moyen > seuil_rentabilite * 0.5:
            # Faible rentabilité → déclin
            self.status = EntrepriseStatus.DECLIN
        else:
            # Pas rentable → risque de faillite
            self.cycles_deficit += 1


class EntrepriseManager:
    """
    Gestionnaire des entreprises dynamiques

    Gère le cycle de vie complet : création, croissance, faillite.
    """

    def __init__(self,
                 registre: RegistreComptesEntreprises,
                 taux_creation: float = 0.05,
                 taux_faillite_base: float = 0.03,
                 seuil_rentabilite_base: float = 100.0,
                 cycles_avant_faillite: int = 12):
        """
        Initialise le gestionnaire

        Args:
            registre: Registre des comptes entreprises
            taux_creation: Taux de création annuel (5% par défaut)
            taux_faillite_base: Taux de faillite de base (3% par défaut)
            seuil_rentabilite_base: V minimum à générer par cycle
            cycles_avant_faillite: Cycles de déficit avant faillite (12 = 1 an)
        """
        self.registre = registre
        self.taux_creation = taux_creation
        self.taux_faillite_base = taux_faillite_base
        self.seuil_rentabilite_base = seuil_rentabilite_base
        self.cycles_avant_faillite = cycles_avant_faillite

        # Métriques par entreprise
        self.metriques: Dict[str, EntrepriseMetrics] = {}

        # Statistiques globales
        self.next_business_id = 0
        self.total_creations = 0
        self.total_faillites = 0
        self.entreprises_actives: List[str] = []

        # Historique
        self.historique_creations: List[Tuple[int, str]] = []  # (cycle, business_id)
        self.historique_faillites: List[Tuple[int, str, str]] = []  # (cycle, business_id, raison)

    def create_entreprise(self,
                         founder_agent_id: str,
                         V_initial: float,
                         business_type: BusinessType,
                         cycle: int) -> Optional[str]:
        """
        Crée une nouvelle entreprise

        Args:
            founder_agent_id: ID de l'agent fondateur
            V_initial: Capital initial (V)
            business_type: Type d'entreprise
            cycle: Cycle de création

        Returns:
            ID de l'entreprise créée, None si échec
        """
        # Génère un ID unique
        business_id = f"business_{cycle}_{self.next_business_id}"
        self.next_business_id += 1

        try:
            # Crée le compte entreprise
            compte = self.registre.create_compte(
                business_id=business_id,
                business_type=business_type,
                V_entreprise=V_initial
            )

            # Initialise les métriques
            metrics = EntrepriseMetrics(
                business_id=business_id,
                age=0,
                status=EntrepriseStatus.CREATION
            )
            self.metriques[business_id] = metrics

            # Enregistre
            self.entreprises_actives.append(business_id)
            self.historique_creations.append((cycle, business_id))
            self.total_creations += 1

            return business_id

        except ValueError as e:
            # Entreprise existe déjà (ne devrait pas arriver)
            return None

    def process_combustion(self,
                          business_id: str,
                          V_genere: float,
                          cycle: int) -> Tuple[float, Optional[NFTFinancier]]:
        """
        Traite la combustion d'une entreprise (S + U → V)

        Args:
            business_id: ID de l'entreprise
            V_genere: V généré par combustion
            cycle: Cycle actuel

        Returns:
            Tuple (contribution_RU_U, nft_genere)
        """
        # Enregistre dans le registre
        contribution_RU, nft = self.registre.process_V_genere(
            business_id, V_genere, cycle
        )

        # Met à jour les métriques
        if business_id in self.metriques:
            metrics = self.metriques[business_id]
            metrics.add_V_genere(V_genere)
            metrics.age += 1
            metrics.cycles_survie += 1

            # Calcule le seuil de rentabilité (ajusté par taille)
            compte = self.registre.get_compte(business_id)
            if compte:
                # Seuil = base × (V_entreprise / référence)
                seuil = self.seuil_rentabilite_base * (compte.V_entreprise / 100000.0)
                metrics.update_status(seuil)

        return (contribution_RU, nft)

    def check_faillites(self, cycle: int) -> List[str]:
        """
        Vérifie et traite les faillites

        Critères de faillite :
        1. Déficit prolongé (cycles_deficit >= cycles_avant_faillite)
        2. V_operationnel < 0 (insolvabilité)
        3. V_entreprise proche de 0

        Args:
            cycle: Cycle actuel

        Returns:
            Liste des IDs en faillite
        """
        faillites = []

        for business_id in list(self.entreprises_actives):
            compte = self.registre.get_compte(business_id)
            metrics = self.metriques.get(business_id)

            if not compte or not metrics:
                continue

            raison_faillite = None

            # Critère 1 : Déficit prolongé
            if metrics.cycles_deficit >= self.cycles_avant_faillite:
                raison_faillite = "deficit_prolonge"

            # Critère 2 : Insolvabilité (V_operationnel négatif impossible normalement,
            # mais on vérifie si V_operationnel = 0 et pas de revenu)
            if compte.V_operationnel < 1.0 and metrics.get_V_moyen_recent() < 1.0:
                raison_faillite = "insolvabilite"

            # Critère 3 : Destruction du capital (V_entreprise trop faible)
            if compte.V_entreprise < self.seuil_rentabilite_base * 0.1:
                raison_faillite = "capital_insuffisant"

            # Si faillite détectée
            if raison_faillite:
                faillites.append(business_id)
                self._process_faillite(business_id, raison_faillite, cycle)

        return faillites

    def _process_faillite(self, business_id: str, raison: str, cycle: int):
        """
        Traite la faillite d'une entreprise

        Args:
            business_id: ID de l'entreprise
            raison: Raison de la faillite
            cycle: Cycle de faillite
        """
        # Retire des actives
        if business_id in self.entreprises_actives:
            self.entreprises_actives.remove(business_id)

        # Met à jour le statut
        if business_id in self.metriques:
            self.metriques[business_id].status = EntrepriseStatus.FAILLITE

        # Enregistre
        self.historique_faillites.append((cycle, business_id, raison))
        self.total_faillites += 1

        # Note : La liquidation des actifs pourrait être gérée ici
        # (transfert à la Chambre de Relance, etc.)

    def simulate_creations(self,
                          agents: Dict,
                          cycle: int,
                          thermometre: float = 1.0) -> List[str]:
        """
        Simule la création de nouvelles entreprises

        Le taux de création dépend :
        - De la richesse des agents (capital disponible)
        - Du thermomètre économique (θ proche de 1 = conditions favorables)

        Args:
            agents: Dictionnaire des agents
            cycle: Cycle actuel
            thermometre: Thermomètre θ du système

        Returns:
            Liste des IDs des entreprises créées
        """
        nouvelles_entreprises = []

        # Ajustement du taux selon θ
        # θ proche de 1 = conditions idéales pour créer
        # θ > 1.2 ou θ < 0.8 = conditions défavorables
        deviation = abs(thermometre - 1.0)
        facteur_conditions = max(0.5, 1.0 - deviation)

        taux_ajuste = self.taux_creation * facteur_conditions

        # Nombre de créations potentielles (Poisson)
        n_creations = np.random.poisson(len(agents) * taux_ajuste)

        # Limite : max 10% de nouveaux entrants par cycle
        n_creations = min(n_creations, int(len(agents) * 0.1))

        for _ in range(n_creations):
            # Sélectionne un agent fondateur aléatoire
            if not agents:
                break

            agent_id = np.random.choice(list(agents.keys()))
            agent = agents[agent_id]

            # Vérifie que l'agent a assez de richesse
            richesse = agent.V_balance + agent.U_balance
            capital_min = self.seuil_rentabilite_base * 10  # 10× le seuil de rentabilité

            if richesse < capital_min:
                continue  # Agent trop pauvre

            # Capital initial : entre 10% et 30% de la richesse de l'agent
            V_initial = richesse * np.random.uniform(0.10, 0.30)

            # Type d'entreprise aléatoire
            business_type = np.random.choice(list(BusinessType))

            # Crée l'entreprise
            business_id = self.create_entreprise(
                founder_agent_id=agent_id,
                V_initial=V_initial,
                business_type=business_type,
                cycle=cycle
            )

            if business_id:
                nouvelles_entreprises.append(business_id)

                # Déduit le capital de l'agent
                agent.V_balance -= V_initial

        return nouvelles_entreprises

    def update(self, cycle: int, agents: Dict, thermometre: float = 1.0) -> Dict:
        """
        Mise à jour complète : créations + faillites

        Args:
            cycle: Cycle actuel
            agents: Dictionnaire des agents
            thermometre: Thermomètre θ

        Returns:
            Dictionnaire {creations: [...], faillites: [...]}
        """
        # 1. Vérification des faillites
        faillites = self.check_faillites(cycle)

        # 2. Créations de nouvelles entreprises
        creations = self.simulate_creations(agents, cycle, thermometre)

        return {
            'creations': creations,
            'faillites': faillites
        }

    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques des entreprises

        Returns:
            Dictionnaire de statistiques
        """
        # Distribution par statut
        status_count = {}
        for metrics in self.metriques.values():
            status = metrics.status.value
            status_count[status] = status_count.get(status, 0) + 1

        # Espérance de vie
        ages = [m.age for m in self.metriques.values() if m.status != EntrepriseStatus.FAILLITE]
        age_moyen = np.mean(ages) if ages else 0

        # Distribution par type
        type_count = {}
        for business_id in self.entreprises_actives:
            compte = self.registre.get_compte(business_id)
            if compte:
                btype = compte.business_type.value
                type_count[btype] = type_count.get(btype, 0) + 1

        return {
            'nb_entreprises_actives': len(self.entreprises_actives),
            'total_creations': self.total_creations,
            'total_faillites': self.total_faillites,
            'taux_survie': ((self.total_creations - self.total_faillites) / max(1, self.total_creations)),
            'age_moyen': age_moyen,
            'distribution_statut': status_count,
            'distribution_type': type_count
        }
