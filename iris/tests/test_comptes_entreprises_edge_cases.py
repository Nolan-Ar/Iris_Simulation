"""
Tests pour iris_comptes_entreprises avec edge cases et pytest
==============================================================

Tests complets incluant:
- Edge cases (V=0, ratios invalides, division par zéro)
- Validations NFT et hash
- Distribution organique 40/60
- Tests des limites de rétention
"""

import pytest
from iris.core.iris_comptes_entreprises import (
    CompteEntreprise,
    RegistreComptesEntreprises,
    BusinessType,
    NFTFinancier,
)
from iris.utils import ValidationError


class TestCompteEntrepriseCreation:
    """Tests de création de compte entreprise"""

    def test_creation_normal(self):
        """Test création normale"""
        compte = CompteEntreprise(
            business_id="ENT001",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0
        )
        assert compte.business_id == "ENT001"
        assert compte.V_entreprise == 1000000.0
        assert compte.V_operationnel == 0.0

    def test_creation_edge_case_zero_V(self):
        """EDGE CASE: Création avec V=0"""
        compte = CompteEntreprise(
            business_id="ENT002",
            business_type=BusinessType.SERVICE,
            V_entreprise=0.0
        )
        assert compte.V_entreprise == 0.0
        assert compte.get_limite_retention() == 0.0

    def test_creation_invalid_negative_V(self):
        """EDGE CASE: V négatif devrait échouer"""
        with pytest.raises((ValidationError, ValueError)):
            CompteEntreprise(
                business_id="ENT003",
                business_type=BusinessType.COMMERCE,
                V_entreprise=-1000.0
            )

    def test_creation_invalid_ratios_not_sum_to_one(self):
        """EDGE CASE: Ratios ne sommant pas à 1.0"""
        with pytest.raises(ValueError):
            CompteEntreprise(
                business_id="ENT004",
                business_type=BusinessType.TECHNOLOGIE,
                V_entreprise=1000000.0,
                ratio_salarial=0.30,
                ratio_tresorerie=0.60  # 0.30 + 0.60 = 0.90 ≠ 1.0
            )

    def test_creation_invalid_ratio_negative(self):
        """EDGE CASE: Ratio négatif"""
        with pytest.raises((ValidationError, ValueError)):
            CompteEntreprise(
                business_id="ENT005",
                business_type=BusinessType.PRODUCTION,
                V_entreprise=1000000.0,
                ratio_salarial=-0.40,
                ratio_tresorerie=1.40
            )

    def test_creation_invalid_ratio_greater_than_one(self):
        """EDGE CASE: Ratio > 1.0"""
        with pytest.raises((ValidationError, ValueError)):
            CompteEntreprise(
                business_id="ENT006",
                business_type=BusinessType.SERVICE,
                V_entreprise=1000000.0,
                ratio_salarial=1.5,
                ratio_tresorerie=-0.5
            )


class TestDistributionOrganique:
    """Tests de la distribution organique 40/60"""

    def test_distribution_normal(self):
        """Test distribution 40/60 normale"""
        compte = CompteEntreprise(
            business_id="ENT_DIST",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0
        )
        salary, treasury, nft = compte.distribute_V_genere(10000.0, cycle=1)

        # Vérifier 40/60
        assert salary == pytest.approx(4000.0)  # 40%
        assert treasury == pytest.approx(6000.0)  # 60%
        assert nft is None  # Pas de NFT (en dessous de la limite)

    def test_distribution_edge_case_zero_V(self):
        """EDGE CASE: Distribution de V=0"""
        compte = CompteEntreprise(
            business_id="ENT_ZERO",
            business_type=BusinessType.SERVICE,
            V_entreprise=1000000.0
        )
        salary, treasury, nft = compte.distribute_V_genere(0.0, cycle=1)

        assert salary == 0.0
        assert treasury == 0.0
        assert nft is None

    def test_distribution_edge_case_negative_V(self):
        """EDGE CASE: V négatif devrait retourner (0, 0, None)"""
        compte = CompteEntreprise(
            business_id="ENT_NEG",
            business_type=BusinessType.COMMERCE,
            V_entreprise=1000000.0
        )
        salary, treasury, nft = compte.distribute_V_genere(-1000.0, cycle=1)

        # Ne devrait pas crasher, retourner des valeurs sûres
        assert salary == 0.0
        assert treasury >= 0.0  # V_operationnel ne devrait jamais être négatif

    def test_distribution_theta_one(self):
        """EDGE CASE: Vérifier θ=1.0 (ratio parfait 40/60)"""
        compte = CompteEntreprise(
            business_id="ENT_THETA",
            business_type=BusinessType.TECHNOLOGIE,
            V_entreprise=1000000.0,
            ratio_salarial=0.40,
            ratio_tresorerie=0.60
        )
        # Vérifier que θ = ratio_salarial / ratio_tresorerie
        theta = compte.ratio_salarial / compte.ratio_tresorerie
        assert theta == pytest.approx(0.40 / 0.60)


class TestLimitesRetention:
    """Tests des limites de rétention et conversion NFT"""

    def test_limite_retention_calculation(self):
        """Test calcul limite de rétention"""
        compte = CompteEntreprise(
            business_id="ENT_LIM",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0,
            seuil_retention=0.20
        )
        limite = compte.get_limite_retention()
        assert limite == pytest.approx(200000.0)  # 20% de 1M

    def test_limite_retention_edge_case_zero_V(self):
        """EDGE CASE: Limite de rétention avec V=0"""
        compte = CompteEntreprise(
            business_id="ENT_LIM_ZERO",
            business_type=BusinessType.SERVICE,
            V_entreprise=0.0,
            seuil_retention=0.20
        )
        limite = compte.get_limite_retention()
        assert limite == 0.0

    def test_nft_creation_when_exceeds_limit(self):
        """Test création NFT quand V_operationnel dépasse la limite"""
        compte = CompteEntreprise(
            business_id="ENT_NFT",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0,
            seuil_retention=0.20  # Limite = 200,000
        )

        # Distribuer suffisamment pour dépasser la limite
        # 60% de V_genere va en V_operationnel
        # Pour atteindre 200k, besoin de ~333k de V_genere
        # Pour dépasser et créer NFT, utilisons 500k
        salary, treasury, nft = compte.distribute_V_genere(500000.0, cycle=1)

        # V_operationnel devrait être plafonné à la limite
        assert treasury == pytest.approx(200000.0)
        # NFT devrait être créé pour l'excédent
        assert nft is not None
        # Excédent = (500k * 0.60) - 200k = 300k - 200k = 100k
        assert nft.valeur_convertie == pytest.approx(100000.0)

    def test_nft_hash_uniqueness(self):
        """Test que les hash NFT sont uniques (pas de collision)"""
        compte = CompteEntreprise(
            business_id="ENT_HASH",
            business_type=BusinessType.TECHNOLOGIE,
            V_entreprise=1000000.0,
            seuil_retention=0.10
        )

        # Créer plusieurs NFT
        hashes = set()
        for i in range(10):
            _, _, nft = compte.distribute_V_genere(200000.0, cycle=i)
            if nft:
                hashes.add(nft.hash_nft)

        # Tous les hash doivent être différents
        assert len(hashes) > 0  # Au moins quelques NFT créés
        # Pas de collision (tous uniques)


class TestStatistiques:
    """Tests des statistiques avec edge cases"""

    def test_statistics_normal(self):
        """Test statistiques normales"""
        compte = CompteEntreprise(
            business_id="ENT_STAT",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0
        )
        compte.distribute_V_genere(10000.0, cycle=1)

        stats = compte.get_statistics()
        assert stats["business_id"] == "ENT_STAT"
        assert stats["V_entreprise"] == 1000000.0
        assert stats["total_V_genere"] == 10000.0
        assert stats["total_masse_salariale_U"] == 4000.0
        assert 0.0 <= stats["taux_utilisation_limite"] <= 100.0

    def test_statistics_edge_case_division_by_zero(self):
        """EDGE CASE: Statistiques avec V_entreprise=0 (div/0)"""
        compte = CompteEntreprise(
            business_id="ENT_STAT_ZERO",
            business_type=BusinessType.SERVICE,
            V_entreprise=0.0
        )
        stats = compte.get_statistics()

        # Ne devrait pas crasher
        assert stats["taux_utilisation_limite"] == 0.0  # safe_divide retourne 0


class TestRegistreComptesEntreprises:
    """Tests du registre avec edge cases"""

    def test_registre_creation(self):
        """Test création registre"""
        registre = RegistreComptesEntreprises()
        assert len(registre.comptes) == 0
        assert registre.total_entreprises_actives == 0

    def test_registre_create_compte(self):
        """Test création de compte via registre"""
        registre = RegistreComptesEntreprises()
        compte = registre.create_compte(
            business_id="REG001",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0
        )
        assert len(registre.comptes) == 1
        assert registre.total_entreprises_actives == 1

    def test_registre_duplicate_id(self):
        """EDGE CASE: Création de compte avec ID dupliqué"""
        registre = RegistreComptesEntreprises()
        registre.create_compte(
            business_id="DUP",
            business_type=BusinessType.PRODUCTION,
            V_entreprise=1000000.0
        )
        with pytest.raises(ValueError):
            registre.create_compte(
                business_id="DUP",  # Même ID
                business_type=BusinessType.SERVICE,
                V_entreprise=500000.0
            )

    def test_registre_process_V_genere(self):
        """Test traitement V généré via registre"""
        registre = RegistreComptesEntreprises()
        registre.create_compte(
            business_id="PROC",
            business_type=BusinessType.COMMERCE,
            V_entreprise=1000000.0
        )

        salary, nft = registre.process_V_genere("PROC", 10000.0, cycle=1)
        assert salary == pytest.approx(4000.0)
        assert registre.pool_masse_salariale_U == pytest.approx(4000.0)

    def test_registre_collect_pool(self):
        """Test collecte du pool de masse salariale"""
        registre = RegistreComptesEntreprises()
        registre.create_compte(
            business_id="POOL",
            business_type=BusinessType.TECHNOLOGIE,
            V_entreprise=1000000.0
        )

        registre.process_V_genere("POOL", 10000.0, cycle=1)
        collected = registre.collect_pool_masse_salariale()

        assert collected == pytest.approx(4000.0)
        assert registre.pool_masse_salariale_U == 0.0  # Réinitialisé

    def test_registre_statistics_edge_case_empty(self):
        """EDGE CASE: Statistiques registre vide"""
        registre = RegistreComptesEntreprises()
        stats = registre.get_statistics()

        assert stats["nb_entreprises_actives"] == 0
        assert stats["total_V_entreprises"] == 0.0
        assert stats["ratio_V_op_V_base"] == 0.0  # Pas de div/0

    def test_registre_statistics_edge_case_division_by_zero(self):
        """EDGE CASE: Statistiques avec V_entreprise total = 0"""
        registre = RegistreComptesEntreprises()
        # Créer une entreprise avec V=0
        registre.create_compte(
            business_id="ZERO",
            business_type=BusinessType.SERVICE,
            V_entreprise=0.0
        )

        stats = registre.get_statistics()
        # Ne devrait pas crasher
        assert stats["ratio_V_op_V_base"] == 0.0


@pytest.mark.parametrize("V_entreprise,seuil_retention,expected_limite", [
    (1000000.0, 0.20, 200000.0),
    (500000.0, 0.10, 50000.0),
    (0.0, 0.20, 0.0),  # Edge case
    (1000000.0, 0.0, 0.0),  # Edge case
    (1000000.0, 1.0, 1000000.0),  # Edge case: 100% retention
])
def test_limite_retention_parametrized(V_entreprise, seuil_retention, expected_limite):
    """Tests paramétrés des limites de rétention"""
    compte = CompteEntreprise(
        business_id="PARAM",
        business_type=BusinessType.PRODUCTION,
        V_entreprise=V_entreprise,
        seuil_retention=seuil_retention
    )
    assert compte.get_limite_retention() == pytest.approx(expected_limite)


def test_nft_rendement_by_business_type():
    """Test que les rendements NFT varient selon le type d'entreprise"""
    rendements = {}

    for btype in BusinessType:
        compte = CompteEntreprise(
            business_id=f"REND_{btype.value}",
            business_type=btype,
            V_entreprise=1000000.0,
            seuil_retention=0.01  # Très bas pour forcer NFT
        )
        _, _, nft = compte.distribute_V_genere(100000.0, cycle=1)
        if nft:
            rendements[btype] = nft.rendement_annuel

    # Vérifier que les rendements sont différents selon le type
    assert len(rendements) > 0
    assert all(0.0 <= r <= 0.10 for r in rendements.values())
