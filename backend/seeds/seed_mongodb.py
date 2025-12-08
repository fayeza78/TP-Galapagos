"""
Script de seed pour MongoDB avec des données réalistes sur les Galapagos
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

# Connexion MongoDB
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "galapagos"


async def seed_data():
    """Insérer les données de seed dans MongoDB"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print(" Début du seed MongoDB ")

    # Supprime les données existantes
    print(" Suppression des données existantes")
    await db.hydravions.delete_many({})
    await db.clients.delete_many({})
    await db.produits.delete_many({})
    await db.commandes.delete_many({})
    await db.stocks.delete_many({})
    await db.lockers.delete_many({})
    await db.livraisons.delete_many({})

    # ========== Hydravions ==========
    print(" Création des hydravions ")
    hydravions_data = [
        {
            "nom": "Albatros-1",
            "modele": "petit",
            "capacite_caisses": 50,
            "consommation_carburant": 15.0,
            "statut": "entrepot",
            "position": {"latitude": -0.7406, "longitude": -90.3120},
            "port_actuel": "Puerto Baquerizo Moreno",
            "carburant_actuel": 100.0
        },
        {
            "nom": "Frégate-2",
            "modele": "moyen",
            "capacite_caisses": 100,
            "consommation_carburant": 20.0,
            "statut": "port",
            "position": {"latitude": -0.4528, "longitude": -90.3120},
            "port_actuel": "Puerto Ayora",
            "carburant_actuel": 85.0
        },
        {
            "nom": "Pélican-3",
            "modele": "grand",
            "capacite_caisses": 150,
            "consommation_carburant": 25.0,
            "statut": "entrepot",
            "position": {"latitude": -0.7406, "longitude": -90.3120},
            "port_actuel": "Puerto Baquerizo Moreno",
            "carburant_actuel": 100.0
        },
        {
            "nom": "Cormoran-4",
            "modele": "petit",
            "capacite_caisses": 50,
            "consommation_carburant": 15.0,
            "statut": "maintenance",
            "position": None,
            "port_actuel": None,
            "carburant_actuel": 45.0
        },
        {
            "nom": "Mouette-5",
            "modele": "moyen",
            "capacite_caisses": 100,
            "consommation_carburant": 20.0,
            "statut": "en_vol",
            "position": {"latitude": -0.6000, "longitude": -90.5000},
            "port_actuel": None,
            "carburant_actuel": 70.0
        }
    ]
    result = await db.hydravions.insert_many(hydravions_data)
    hydravion_ids = result.inserted_ids
    print(f" {len(hydravion_ids)} hydravions créés")

    # ========== Clients ==========
    print(" Création des clients ")
    clients_data = [
        {
            "nom": "Darwin",
            "prenom": "Charles",
            "email": "c.darwin@galapagos-research.org",
            "telephone": "+593-987-654-321",
            "role": "biologiste_marin",
            "organisation": "Charles Darwin Research Station",
            "ile_principale": "Santa Cruz"
        },
        {
            "nom": "Rodriguez",
            "prenom": "Maria",
            "email": "m.rodriguez@volcanic-institute.ec",
            "telephone": "+593-987-654-322",
            "role": "volcanologue",
            "organisation": "Instituto Geofísico - Ecuador",
            "ile_principale": "Isabela"
        },
        {
            "nom": "Thompson",
            "prenom": "James",
            "email": "j.thompson@wildlife-conservation.org",
            "telephone": "+593-987-654-323",
            "role": "zoologue",
            "organisation": "Galapagos Conservancy",
            "ile_principale": "San Cristóbal"
        },
        {
            "nom": "Sanchez",
            "prenom": "Elena",
            "email": "e.sanchez@marine-biology.ec",
            "telephone": "+593-987-654-324",
            "role": "biologiste_marin",
            "organisation": "Universidad San Francisco de Quito",
            "ile_principale": "Floreana"
        },
        {
            "nom": "Williams",
            "prenom": "Robert",
            "email": "r.williams@botanical-research.org",
            "telephone": "+593-987-654-325",
            "role": "botaniste",
            "organisation": "Galapagos National Park Service",
            "ile_principale": "Santa Cruz"
        },
        {
            "nom": "Garcia",
            "prenom": "Luis",
            "email": "l.garcia@geology.ec",
            "telephone": "+593-987-654-326",
            "role": "geologue",
            "organisation": "Escuela Politécnica Nacional",
            "ile_principale": "Isabela"
        }
    ]
    result = await db.clients.insert_many(clients_data)
    client_ids = result.inserted_ids
    print(f" {len(client_ids)} clients créés")

    # ========== Produits ==========
    print(" Création des produits ")
    produits_data = [
        {
            "nom": "Équipement de plongée profonde",
            "description": "Kit complet de plongée pour exploration marine jusqu'à 40m",
            "categorie": "equipement_plongee",
            "poids": 25.5,
            "dimensions": {"hauteur": 80.0, "largeur": 60.0, "profondeur": 40.0},
            "stock_disponible": 15
        },
        {
            "nom": "Microscope binoculaire portable",
            "description": "Microscope haute résolution pour analyse sur le terrain",
            "categorie": "materiel_laboratoire",
            "poids": 8.2,
            "dimensions": {"hauteur": 45.0, "largeur": 30.0, "profondeur": 25.0},
            "stock_disponible": 8
        },
        {
            "nom": "Caméra thermique infrarouge",
            "description": "Caméra pour surveillance volcanique et faune nocturne",
            "categorie": "equipement_observation",
            "poids": 3.5,
            "dimensions": {"hauteur": 25.0, "largeur": 20.0, "profondeur": 15.0},
            "stock_disponible": 6
        },
        {
            "nom": "Tente expedition 4 saisons",
            "description": "Tente résistante pour camping en conditions extrêmes",
            "categorie": "materiel_camping",
            "poids": 12.0,
            "dimensions": {"hauteur": 50.0, "largeur": 50.0, "profondeur": 20.0},
            "stock_disponible": 20
        },
        {
            "nom": "Kit prélèvement échantillons marins",
            "description": "Conteneurs et outils pour échantillons biologiques",
            "categorie": "echantillons",
            "poids": 5.0,
            "dimensions": {"hauteur": 30.0, "largeur": 40.0, "profondeur": 25.0},
            "stock_disponible": 25
        },
        {
            "nom": "Trousse médicale d'urgence",
            "description": "Kit médical complet pour intervention sur le terrain",
            "categorie": "medicaments",
            "poids": 4.5,
            "dimensions": {"hauteur": 35.0, "largeur": 25.0, "profondeur": 15.0},
            "stock_disponible": 12
        },
        {
            "nom": "Sismographe portable",
            "description": "Capteur sismique pour surveillance volcanique",
            "categorie": "materiel_laboratoire",
            "poids": 15.0,
            "dimensions": {"hauteur": 40.0, "largeur": 30.0, "profondeur": 30.0},
            "stock_disponible": 4
        },
        {
            "nom": "Jumelles vision nocturne",
            "description": "Jumelles haute définition pour observation nocturne faune",
            "categorie": "equipement_observation",
            "poids": 2.8,
            "dimensions": {"hauteur": 20.0, "largeur": 15.0, "profondeur": 10.0},
            "stock_disponible": 10
        }
    ]
    result = await db.produits.insert_many(produits_data)
    produit_ids = result.inserted_ids
    print(f"   ✅ {len(produit_ids)} produits créés")

    # ========== Stocks ==========
    print(" Création des stocks ")
    stocks_data = []
    for i, produit_id in enumerate(produit_ids):
        stock = {
            "produit_id": str(produit_id),
            "quantite_disponible": produits_data[i]["stock_disponible"],
            "quantite_reservee": random.randint(0, 5),
            "seuil_alerte": 5,
            "derniere_mise_a_jour": datetime.now()
        }
        stocks_data.append(stock)
    await db.stocks.insert_many(stocks_data)
    print(f"{len(stocks_data)} stocks créés")

    # ========== Lockers ==========
    print(" Création des lockers ")
    ports_lockers = [
        {"ile": "San Cristóbal", "port": "Puerto Baquerizo Moreno", "nombre": 50},
        {"ile": "Santa Cruz", "port": "Puerto Ayora", "nombre": 80},
        {"ile": "Isabela", "port": "Puerto Villamil", "nombre": 40},
        {"ile": "Floreana", "port": "Puerto Velasco Ibarra", "nombre": 25},
        {"ile": "San Cristóbal", "port": "Wreck Bay", "nombre": 20},
        {"ile": "Santa Cruz", "port": "Academy Bay", "nombre": 30},
    ]

    lockers_data = []
    for port_info in ports_lockers:
        for i in range(1, port_info["nombre"] + 1):
            locker = {
                "numero": i,
                "ile": port_info["ile"],
                "port": port_info["port"],
                "taille_caisse": 1,
                "statut": random.choice(["vide", "vide", "vide", "plein", "reserve"]),
                "commande_id": None,
                "date_remplissage": None
            }
            lockers_data.append(locker)
    await db.lockers.insert_many(lockers_data)
    print(f" {len(lockers_data)} lockers créés")

    # ========== Commandes ==========
    print(" Création des commandes ")
    commandes_data = []
    for i in range(10):
        # Sélectionne un client aléatoire
        client_id = str(random.choice(client_ids))

        # Sélectionne 1-3 produits aléatoires
        nb_produits = random.randint(1, 3)
        produits_commande = []
        for _ in range(nb_produits):
            produits_commande.append({
                "produit_id": str(random.choice(produit_ids)),
                "quantite": random.randint(1, 3)
            })

        nombre_caisses = sum(p["quantite"] for p in produits_commande)

        commande = {
            "client_id": client_id,
            "produits": produits_commande,
            "port_destination": random.choice([
                "Puerto Ayora", "Puerto Baquerizo Moreno", "Puerto Villamil",
                "Puerto Velasco Ibarra", "Wreck Bay", "Academy Bay"
            ]),
            "nombre_caisses_requises": nombre_caisses,
            "date_commande": datetime.now() - timedelta(days=random.randint(0, 30)),
            "date_livraison_souhaitee": datetime.now() + timedelta(days=random.randint(1, 15)),
            "statut": random.choice(["en_attente", "en_preparation", "prete", "en_livraison", "livree"]),
            "priorite": random.randint(1, 5)
        }
        commandes_data.append(commande)

    result = await db.commandes.insert_many(commandes_data)
    commande_ids = result.inserted_ids
    print(f" {len(commande_ids)} commandes créées")

    # ========== Livraisons ==========
    print(" Création des livraisons ")
    livraisons_data = []
    for i in range(5):
        commande_id = str(commande_ids[i])
        hydravion_id = str(random.choice(hydravion_ids))

        itineraire = [
            "Puerto Baquerizo Moreno",
            random.choice(["Puerto Ayora", "Puerto Villamil", "Wreck Bay"])
        ]

        distance_totale = random.uniform(50, 200)
        consommation_estimee = distance_totale * 0.20

        livraison = {
            "commande_id": commande_id,
            "hydravion_id": hydravion_id,
            "itineraire": itineraire,
            "caisses_livrees": random.randint(1, 5),
            "distance_totale": distance_totale,
            "consommation_estimee": consommation_estimee,
            "date_depart": datetime.now() - timedelta(hours=random.randint(1, 48)),
            "date_arrivee_estimee": datetime.now() + timedelta(hours=random.randint(1, 24)),
            "date_arrivee_reelle": None if random.random() > 0.5 else datetime.now() - timedelta(hours=random.randint(1, 12)),
            "statut": random.choice(["en_cours", "en_vol", "livree", "en_attente"])
        }
        livraisons_data.append(livraison)

    await db.livraisons.insert_many(livraisons_data)
    print(f" {len(livraisons_data)} livraisons créées")

    print(" Seed MongoDB terminé avec succès!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
