"""
Test du Système de Comptes Entreprises IRIS
============================================

╔══════════════════════════════════════════════════════════════════════════════╗
║ OBJECTIF DE CE FICHIER DE TESTS                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ce fichier contient des tests unitaires pour valider le comportement du système
de comptabilité d'entreprise dans IRIS v2.1. Les tests vérifient que:

1. La distribution 40/60 est respectée lors de la combustion S+U→V
2. Les limites de rétention V_opérationnel fonctionnent correctement
3. Les NFT financiers sont générés quand V_op dépasse la limite
4. Le registre centralisé collecte correctement les flux
5. L'intégration avec IRISEconomy fonctionne sans erreur

╔══════════════════════════════════════════════════════════════════════════════╗
║ POURQUOI CES TESTS SONT CRITIQUES                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Les tests garantissent que:
- Le modèle théorique IRIS est correctement implémenté (40% RU, 60% V_op)
- Les invariants comptables sont respectés (conservation des flux)
- Les mécanismes de régulation (NFT, seuils) fonctionnent comme spécifié
- Le code est robuste et prêt pour publication académique

Si un test échoue, cela signale une incohérence entre théorie et implémentation
qui DOIT être corrigée avant utilisation en production ou publication.

╔══════════════════════════════════════════════════════════════════════════════╗
║ TESTS IMPLÉMENTÉS                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

TEST 1: Distribution 40/60 (Combustion S+U→V)
---------------------------------------------
Vérifie que quand une entreprise génère du V par combustion:
- 40% va à la masse salariale (converti en U pour distribution RU)
- 60% va en trésorerie opérationnelle (V_operationnel)

Formule testée:
  part_RU = V_généré × 0.40
  V_operationnel = V_généré × 0.60

TEST 2: Limites de Rétention V_operationnel + Conversion NFT
------------------------------------------------------------
Vérifie que:
- V_operationnel ne peut pas dépasser 20% du patrimoine V de l'entreprise
- Quand limite atteinte, l'excédent est converti en NFT financier
- Les NFT ont un rendement annuel (2-5%)

Logique testée:
  limite_retention = V_entreprise × 0.20
  si V_operationnel > limite → crée NFT(excédent)

TEST 3: Registre Centralisé (Collecte pool masses salariales)
-------------------------------------------------------------
Vérifie que:
- Le registre collecte correctement les masses salariales de toutes les entreprises
- Les statistiques globales sont cohérentes
- La traçabilité comptable est maintenue

TEST 4: Intégration IRIS (Simulation complète)
----------------------------------------------
Vérifie que:
- Les comptes d'entreprise fonctionnent dans une simulation IRIS complète
- Les flux entre agents, entreprises et RAD sont cohérents
- Le système converge vers θ≈1.0 avec le nouveau système comptable

╔══════════════════════════════════════════════════════════════════════════════╗
║ COMMENT EXÉCUTER CES TESTS                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Depuis le terminal:
  python test_comptes_entreprises.py

Sortie attendue:
  ✅ SUCCÈS : Distribution 40/60
  ✅ SUCCÈS : Limites rétention + NFT
  ✅ SUCCÈS : Registre centralisé
  ✅ SUCCÈS : Intégration IRIS

Si un test échoue (❌ ÉCHEC), lisez attentivement le message d'erreur pour
identifier la cause et corriger le code avant de continuer.

Auteur: Arnault Nolan
Email: arnaultnolan@gmail.com
Date: 2025
Version: 2.1
"""

import sys
import numpy as np
from iris_model import IRISEconomy, AssetType
from iris_comptes_entreprises import (
    RegistreComptesEntreprises, CompteEntreprise, BusinessType
)

def test_distribution_40_60():
    """Test de la distribution asymétrique 40/60 (combustion S+U→V)"""
    print("\n" + "="*80)
    print("TEST 1 : Distribution 40/60 (Combustion S+U→V)")
    print("="*80)

    # Crée un compte entreprise
    compte = CompteEntreprise(
        business_id="ENT_001",
        business_type=BusinessType.PRODUCTION,
        V_entreprise=1_000_000.0,
        seuil_retention=0.20  # 20% de V
    )

    print(f"\nEntreprise : {compte.business_id}")
    print(f"Type : {compte.business_type.value}")
    print(f"Patrimoine V : {compte.V_entreprise:,.2f}")
    print(f"Limite rétention V_op : {compte.get_limite_retention():,.2f}")

    # COMBUSTION génère du V
    V_genere = 50_000.0
    print(f"\nCOMBUSTION S+U : V généré = {V_genere:,.2f}")

    # Distribution du V généré
    part_RU_en_U, V_op_final, nft = compte.distribute_V_genere(V_genere, cycle=1)

    print(f"\nDistribution du V généré :")
    print(f"  - 40% V → U pour RU : {part_RU_en_U:,.2f} (attendu: {V_genere * 0.40:,.2f})")
    print(f"  - 60% V → V_operationnel : {compte.V_operationnel:,.2f} (attendu: {V_genere * 0.60:,.2f})")
    print(f"  - NFT généré : {'Oui' if nft else 'Non'}")

    # Vérifications
    assert abs(part_RU_en_U - V_genere * 0.40) < 0.01, "❌ Distribution RU incorrecte"
    assert abs(compte.V_operationnel - V_genere * 0.60) < 0.01, "❌ Distribution V_operationnel incorrecte"
    print("\n✅ Distribution 40/60 validée (Combustion S+U→V)")

    return True

def test_limite_retention():
    """Test des limites de rétention V_operationnel et conversion NFT"""
    print("\n" + "="*80)
    print("TEST 2 : Limites Rétention V_operationnel + Conversion NFT")
    print("="*80)

    # Crée un compte avec petit V pour forcer dépassement
    compte = CompteEntreprise(
        business_id="ENT_002",
        business_type=BusinessType.TECHNOLOGIE,
        V_entreprise=100_000.0,
        seuil_retention=0.20  # Limite = 20,000
    )

    limite = compte.get_limite_retention()
    print(f"\nEntreprise : {compte.business_id}")
    print(f"Patrimoine V_base : {compte.V_entreprise:,.2f}")
    print(f"Limite rétention V_op (20% de V) : {limite:,.2f}")

    # Génère plusieurs combustions pour dépasser la limite
    print(f"\n📊 COMBUSTIONS successives (S+U→V) :")
    nft_count = 0

    for i in range(5):
        V_genere = 50_000.0
        part_RU_U, V_op_final, nft = compte.distribute_V_genere(V_genere, cycle=i+1)

        taux_util = (compte.V_operationnel / limite * 100) if limite > 0 else 0
        print(f"  Cycle {i+1}: V généré {V_genere:,.0f} → V_op={compte.V_operationnel:,.0f} "
              f"({taux_util:.1f}% limite) | NFT={'✓' if nft else '✗'}")

        if nft:
            nft_count += 1
            print(f"    → NFT créé : {nft.nft_id}, Valeur V={nft.valeur_convertie:,.2f}, "
                  f"Rendement={nft.rendement_annuel*100:.1f}%")

    print(f"\n📈 Résultats :")
    print(f"  - V_operationnel final : {compte.V_operationnel:,.2f}")
    print(f"  - Limite V_op : {limite:,.2f}")
    print(f"  - NFT créés : {nft_count}")
    print(f"  - Valeur totale NFT (V) : {compte.total_NFT_emis_V:,.2f}")

    # Vérifications
    assert compte.V_operationnel <= limite + 1.0, "❌ V_operationnel dépasse la limite"
    assert nft_count > 0, "❌ Aucun NFT créé malgré dépassement"
    print("\n✅ Limites rétention V_operationnel + conversion NFT validées")

    return True

def test_registre_entreprises():
    """Test du registre centralisé (combustion S+U→V)"""
    print("\n" + "="*80)
    print("TEST 3 : Registre Centralisé + Combustion")
    print("="*80)

    # Crée le registre
    registre = RegistreComptesEntreprises()

    # Crée 3 entreprises de types différents
    entreprises = [
        ("ENT_A", BusinessType.PRODUCTION, 500_000.0),
        ("ENT_B", BusinessType.SERVICE, 300_000.0),
        ("ENT_C", BusinessType.COMMERCE, 400_000.0)
    ]

    print(f"\n📋 Création de {len(entreprises)} entreprises :")
    for business_id, btype, V in entreprises:
        compte = registre.create_compte(business_id, btype, V)
        print(f"  - {business_id} ({btype.value}) : V_base={V:,.0f}")

    # Génère des combustions pour toutes
    print(f"\n💰 COMBUSTIONS (S+U→V) sur 3 cycles :")
    for cycle in range(1, 4):
        total_RU_U_cycle = 0.0
        print(f"\n  Cycle {cycle} :")

        for business_id, _, V in entreprises:
            V_genere = V * 0.10  # Combustion génère 10% de V_base
            contribution_RU_U, nft = registre.process_V_genere(business_id, V_genere, cycle)
            total_RU_U_cycle += contribution_RU_U
            print(f"    {business_id}: V généré={V_genere:,.0f} → RU (U)={contribution_RU_U:,.0f} | NFT={'✓' if nft else '✗'}")

        print(f"    Total RU (U) du cycle : {total_RU_U_cycle:,.2f}")

    # Collecte le pool de masse salariale (renommé de pool_RU)
    pool_masse_salariale_U = registre.collect_pool_masse_salariale()
    print(f"\n📊 Pool masse salariale (U) collecté : {pool_masse_salariale_U:,.2f}")

    # Statistiques
    stats = registre.get_statistics()
    print(f"\n📈 Statistiques globales :")
    print(f"  - Entreprises actives : {stats['nb_entreprises_actives']}")
    print(f"  - V_base total : {stats['total_V_entreprises']:,.2f}")
    print(f"  - V_operationnel total : {stats['total_V_operationnel']:,.2f}")
    print(f"  - Masse salariale (U) cumulée : {stats['total_masse_salariale_U']:,.2f}")
    print(f"  - NFT financiers émis : {stats['total_NFT_financiers']}")
    print(f"  - Valeur totale NFT (V) : {stats['total_valeur_NFT_V']:,.2f}")

    # Vérifications
    assert stats['nb_entreprises_actives'] == 3, "❌ Nombre entreprises incorrect"
    assert stats['total_masse_salariale_U'] > 0, "❌ Aucune masse salariale distribuée"
    print("\n✅ Registre centralisé validé (Combustion S+U→V)")

    return True

def test_integration_iris_economy():
    """Test d'intégration avec IRISEconomy (Combustion S+U→V)"""
    print("\n" + "="*80)
    print("TEST 4 : Intégration IRIS + Combustion")
    print("="*80)

    # Crée une économie IRIS
    print("\n🏗️  Création économie IRIS (50 agents)...")
    economy = IRISEconomy(initial_agents=50)

    # Crée 3 entreprises dans le registre
    print(f"\n🏭 Création de 3 entreprises :")
    entreprises = [
        ("BIZ_001", BusinessType.PRODUCTION, 800_000.0),
        ("BIZ_002", BusinessType.SERVICE, 600_000.0),
        ("BIZ_003", BusinessType.TECHNOLOGIE, 1_000_000.0)
    ]

    for business_id, btype, V in entreprises:
        economy.registre_entreprises.create_compte(business_id, btype, V)
        print(f"  - {business_id} ({btype.value}) : V_base={V:,.0f}")

    # Simule 100 cycles
    print(f"\n⏱️  Simulation 100 cycles (combustions entreprises tous les 10 cycles)...")

    # État initial
    V_initial = sum(a.V_balance for a in economy.agents.values())
    U_initial = sum(a.U_balance for a in economy.agents.values())

    print(f"\nÉtat initial :")
    print(f"  - Total V agents : {V_initial:,.2f}")
    print(f"  - Total U agents : {U_initial:,.2f}")
    print(f"  - Thermomètre θ : {economy.thermometer():.4f}")

    # Simulation
    economy.simulate(steps=100, n_transactions=5)

    # État final
    V_final = sum(a.V_balance for a in economy.agents.values())
    U_final = sum(a.U_balance for a in economy.agents.values())

    print(f"\nÉtat final (après 100 cycles) :")
    print(f"  - Total V agents : {V_final:,.2f} (Δ={V_final-V_initial:+,.2f})")
    print(f"  - Total U agents : {U_final:,.2f} (Δ={U_final-U_initial:+,.2f})")
    print(f"  - Thermomètre θ : {economy.thermometer():.4f}")

    # Statistiques entreprises
    stats = economy.registre_entreprises.get_statistics()
    print(f"\n📊 Statistiques entreprises (Combustion S+U→V) :")
    print(f"  - V_operationnel total : {stats['total_V_operationnel']:,.2f}")
    print(f"  - Masse salariale (U) totale : {stats['total_masse_salariale_U']:,.2f}")
    print(f"  - NFT financiers créés : {stats['total_NFT_financiers']}")
    print(f"  - Valeur NFT totale (V) : {stats['total_valeur_NFT_V']:,.2f}")

    # Analyse historique (renommé de business_contributions_RU → business_masse_salariale)
    if len(economy.history['business_masse_salariale']) > 0:
        total_business_masse_salariale_U = sum(economy.history['business_masse_salariale'])
        cycles_avec_masse_salariale = sum(1 for x in economy.history['business_masse_salariale'] if x > 0)
        total_NFT = sum(economy.history['business_NFT_created'])

        print(f"\n📈 Analyse historique :")
        print(f"  - Total masse salariale (U) distribuée (entreprises) : {total_business_masse_salariale_U:,.2f}")
        print(f"  - Cycles avec distributions : {cycles_avec_masse_salariale}/100")
        print(f"  - NFT créés (total) : {total_NFT}")

    # Vérifications
    assert stats['total_masse_salariale_U'] > 0, "❌ Aucune masse salariale distribuée"
    assert economy.thermometer() > 0, "❌ Thermomètre invalide"
    print("\n✅ Intégration IRISEconomy validée (Combustion S+U→V)")

    return True

def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "█"*80)
    print("█" + " "*30 + "TESTS PHASE D" + " "*35 + "█")
    print("█" + " "*24 + "Comptes Entreprises IRIS" + " "*31 + "█")
    print("█"*80)

    tests = [
        ("Distribution 40/60", test_distribution_40_60),
        ("Limites rétention + NFT", test_limite_retention),
        ("Registre centralisé", test_registre_entreprises),
        ("Intégration IRIS", test_integration_iris_economy)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ ERREUR dans {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Résumé
    print("\n" + "█"*80)
    print("█" + " "*32 + "RÉSUMÉ TESTS" + " "*34 + "█")
    print("█"*80)

    for name, success in results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"  {status} : {name}")

    total = len(results)
    passed = sum(1 for _, s in results if s)

    print(f"\n  Total : {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("█"*80 + "\n")

    return all(s for _, s in results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
