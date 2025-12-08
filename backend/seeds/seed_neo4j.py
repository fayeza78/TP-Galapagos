"""
Script de seed pour Neo4J avec des données réalistes sur les îles Galapagos
Coordonnées GPS réelles des îles et ports
"""
from neo4j import GraphDatabase
import math

# Connexion Neo4J
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "galapagos2024"


def calculer_distance(lat1, lon1, lat2, lon2):
    """Calculer la distance en km entre deux points GPS (formule de Haversine)"""
    R = 6371  # Rayon de la Terre en km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def seed_neo4j():
    """Insérer les données de seed dans Neo4J"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    print(" Début du seed Neo4J")

    with driver.session() as session:
        # Supprimer toutes les données existantes
        print("Suppression des données existantes")
        session.run("MATCH (n) DETACH DELETE n")

        # ========== Îles ==========
        print("Création des îles")

        iles_data = [
            {
                "nom": "San Cristóbal",
                "latitude": -0.8406,
                "longitude": -89.4325,
                "superficie": 558.0,
                "population": 7000,
                "description": "L'île de San Cristóbal abrite la capitale provinciale Puerto Baquerizo Moreno et l'entrepôt principal de Richnou Galap."
            },
            {
                "nom": "Santa Cruz",
                "latitude": -0.6396,
                "longitude": -90.3312,
                "superficie": 986.0,
                "population": 15000,
                "description": "L'île la plus peuplée, abritant la station de recherche Charles Darwin et plusieurs ports importants."
            },
            {
                "nom": "Isabela",
                "latitude": -0.9485,
                "longitude": -91.0984,
                "superficie": 4640.0,
                "population": 2200,
                "description": "La plus grande île de l'archipel, célèbre pour ses volcans actifs. Zone d'étude privilégiée des volcanologues."
            },
            {
                "nom": "Floreana",
                "latitude": -1.2869,
                "longitude": -90.4378,
                "superficie": 173.0,
                "population": 100,
                "description": "Petite île habitée, importante pour les études de biodiversité marine."
            },
            {
                "nom": "Fernandina",
                "latitude": -0.3709,
                "longitude": -91.5523,
                "superficie": 642.0,
                "population": 0,
                "description": "Île volcanique non habitée, zone protégée pour la recherche scientifique."
            },
            {
                "nom": "Santiago",
                "latitude": -0.2569,
                "longitude": -90.7708,
                "superficie": 585.0,
                "population": 0,
                "description": "Île non habitée, importante pour les études géologiques et la faune endémique."
            },
            {
                "nom": "Española",
                "latitude": -1.3829,
                "longitude": -89.6208,
                "superficie": 60.0,
                "population": 0,
                "description": "Île la plus au sud, célèbre pour ses albatros et ses iguanes marins."
            },
            {
                "nom": "Genovesa",
                "latitude": 0.3197,
                "longitude": -89.9553,
                "superficie": 14.0,
                "population": 0,
                "description": "Petite île en forme de fer à cheval, paradis des ornithologues."
            }
        ]

        for ile in iles_data:
            query = """
            CREATE (i:Ile {
                nom: $nom,
                latitude: $latitude,
                longitude: $longitude,
                superficie: $superficie,
                population: $population,
                description: $description
            })
            """
            session.run(query, **ile)

        print(f"{len(iles_data)} îles créées")

        # ========== Ports ==========
        print("Création des ports")

        ports_data = [
            {
                "nom": "Puerto Baquerizo Moreno",
                "ile": "San Cristóbal",
                "latitude": -0.9019,
                "longitude": -89.6108,
                "nombre_lockers": 50,
                "capacite_hydravions": 5
            },
            {
                "nom": "Wreck Bay",
                "ile": "San Cristóbal",
                "latitude": -0.8950,
                "longitude": -89.6150,
                "nombre_lockers": 20,
                "capacite_hydravions": 2
            },
            {
                "nom": "Puerto Ayora",
                "ile": "Santa Cruz",
                "latitude": -0.7406,
                "longitude": -90.3120,
                "nombre_lockers": 80,
                "capacite_hydravions": 6
            },
            {
                "nom": "Academy Bay",
                "ile": "Santa Cruz",
                "latitude": -0.7350,
                "longitude": -90.3050,
                "nombre_lockers": 30,
                "capacite_hydravions": 3
            },
            {
                "nom": "Puerto Villamil",
                "ile": "Isabela",
                "latitude": -0.9572,
                "longitude": -90.9658,
                "nombre_lockers": 40,
                "capacite_hydravions": 3
            },
            {
                "nom": "Puerto Velasco Ibarra",
                "ile": "Floreana",
                "latitude": -1.2875,
                "longitude": -90.4772,
                "nombre_lockers": 25,
                "capacite_hydravions": 2
            },
            {
                "nom": "Punta Espinoza",
                "ile": "Fernandina",
                "latitude": -0.2647,
                "longitude": -91.4436,
                "nombre_lockers": 15,
                "capacite_hydravions": 1
            },
            {
                "nom": "James Bay",
                "ile": "Santiago",
                "latitude": -0.2108,
                "longitude": -90.8244,
                "nombre_lockers": 20,
                "capacite_hydravions": 2
            },
            {
                "nom": "Punta Suarez",
                "ile": "Española",
                "latitude": -1.3689,
                "longitude": -89.7319,
                "nombre_lockers": 10,
                "capacite_hydravions": 1
            },
            {
                "nom": "Darwin Bay",
                "ile": "Genovesa",
                "latitude": 0.3208,
                "longitude": -89.9647,
                "nombre_lockers": 10,
                "capacite_hydravions": 1
            }
        ]

        for port in ports_data:
            # Créer le port
            query_port = """
            CREATE (p:Port {
                nom: $nom,
                ile: $ile,
                latitude: $latitude,
                longitude: $longitude,
                nombre_lockers: $nombre_lockers,
                capacite_hydravions: $capacite_hydravions
            })
            """
            session.run(query_port, **port)

            # Lier le port à son île
            query_relation = """
            MATCH (p:Port {nom: $nom_port})
            MATCH (i:Ile {nom: $nom_ile})
            CREATE (p)-[:SITUE_SUR]->(i)
            """
            session.run(query_relation, nom_port=port["nom"], nom_ile=port["ile"])

        print(f"{len(ports_data)} ports créés")

        # ========== Routes ==========
        print(" Création des routes entre ports ")

        # Récupérer tous les ports avec leurs coordonnées
        result = session.run("MATCH (p:Port) RETURN p.nom as nom, p.latitude as lat, p.longitude as lon")
        ports_coords = {record["nom"]: (record["lat"], record["lon"]) for record in result}

        routes_count = 0
        # Créer des routes entre les ports principaux (pas toutes les combinaisons)
        routes_importantes = [
            ("Puerto Baquerizo Moreno", "Puerto Ayora"),
            ("Puerto Baquerizo Moreno", "Wreck Bay"),
            ("Puerto Ayora", "Academy Bay"),
            ("Puerto Ayora", "Puerto Villamil"),
            ("Puerto Ayora", "Puerto Velasco Ibarra"),
            ("Puerto Villamil", "Punta Espinoza"),
            ("Puerto Baquerizo Moreno", "Punta Suarez"),
            ("Puerto Ayora", "James Bay"),
            ("James Bay", "Darwin Bay"),
            ("Wreck Bay", "Puerto Ayora"),
            ("Academy Bay", "Puerto Villamil"),
            ("Puerto Baquerizo Moreno", "Puerto Villamil"),
        ]

        for port1, port2 in routes_importantes:
            if port1 in ports_coords and port2 in ports_coords:
                lat1, lon1 = ports_coords[port1]
                lat2, lon2 = ports_coords[port2]

                distance = calculer_distance(lat1, lon1, lat2, lon2)
                temps_vol_estime = (distance / 200) * 60  # Vitesse 200 km/h

                # Route aller
                query_route = """
                MATCH (p1:Port {nom: $port1})
                MATCH (p2:Port {nom: $port2})
                CREATE (p1)-[:ROUTE {
                    distance: $distance,
                    temps_vol_estime: $temps_vol_estime
                }]->(p2)
                """
                session.run(query_route, port1=port1, port2=port2, distance=distance, temps_vol_estime=temps_vol_estime)
                routes_count += 1

                # Route retour
                session.run(query_route, port1=port2, port2=port1, distance=distance, temps_vol_estime=temps_vol_estime)
                routes_count += 1

        print(f" {routes_count} routes créées")

        # ========== Vérification ==========
        print("\n Statistiques:")

        ile_count = session.run("MATCH (i:Ile) RETURN count(i) as count").single()["count"]
        print(f"   - Îles: {ile_count}")

        port_count = session.run("MATCH (p:Port) RETURN count(p) as count").single()["count"]
        print(f"   - Ports: {port_count}")

        route_count = session.run("MATCH ()-[r:ROUTE]->() RETURN count(r) as count").single()["count"]
        print(f"   - Routes: {route_count}")

        relation_count = session.run("MATCH ()-[r:SITUE_SUR]->() RETURN count(r) as count").single()["count"]
        print(f"   - Relations Port-Île: {relation_count}")

    print("\n Seed Neo4J terminé avec succès!")
    driver.close()


if __name__ == "__main__":
    seed_neo4j()
