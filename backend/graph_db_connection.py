import os
from neo4j import GraphDatabase
import logging
import math

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://galapagos-neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "galapagos2024")

logger = logging.getLogger("uvicorn.error")

# Driver Neo4J
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def verify_connectivity():
    """Vérifier la connexion à Neo4J"""
    try:
        driver.verify_connectivity()
        logger.info("Connecté à Neo4J")
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion Neo4J: {e}")
        return False


# ========== Fonctions pour les Îles ==========

def creer_ile(tx, ile: dict):
    """Créer un nœud Île dans Neo4J"""
    query = """
    CREATE (i:Ile {
        nom: $nom,
        latitude: $latitude,
        longitude: $longitude,
        superficie: $superficie,
        population: $population,
        description: $description
    })
    RETURN i
    """
    result = tx.run(query,
                    nom=ile["nom"],
                    latitude=ile["coordonnees"]["latitude"],
                    longitude=ile["coordonnees"]["longitude"],
                    superficie=ile["superficie"],
                    population=ile.get("population", 0),
                    description=ile["description"])
    return result.single()


# ========== Fonctions pour les Ports ==========

def creer_port(tx, port: dict):
    """Créer un nœud Port dans Neo4J"""
    query = """
    CREATE (p:Port {
        nom: $nom,
        ile: $ile,
        latitude: $latitude,
        longitude: $longitude,
        nombre_lockers: $nombre_lockers,
        capacite_hydravions: $capacite_hydravions
    })
    RETURN p
    """
    result = tx.run(query,
                    nom=port["nom"],
                    ile=port["ile"],
                    latitude=port["coordonnees"]["latitude"],
                    longitude=port["coordonnees"]["longitude"],
                    nombre_lockers=port["nombre_lockers"],
                    capacite_hydravions=port["capacite_hydravions"])
    return result.single()


def lier_port_a_ile(tx, port_nom: str, ile_nom: str):
    """Créer une relation SITUE_SUR entre un port et une île"""
    query = """
    MATCH (p:Port {nom: $port_nom})
    MATCH (i:Ile {nom: $ile_nom})
    CREATE (p)-[:SITUE_SUR]->(i)
    """
    tx.run(query, port_nom=port_nom, ile_nom=ile_nom)


# ========== Fonctions pour les Routes ==========

def calculer_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculer la distance en km entre deux points GPS (formule de Haversine)
    """
    R = 6371  # Rayon de la Terre en km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def creer_route(tx, port_depart: str, port_arrivee: str, distance: float):
    """Créer une relation ROUTE entre deux ports"""
    # Vitesse moyenne d'un hydravion: 200 km/h
    temps_vol_estime = (distance / 200) * 60  # En minutes

    query = """
    MATCH (p1:Port {nom: $port_depart})
    MATCH (p2:Port {nom: $port_arrivee})
    CREATE (p1)-[:ROUTE {
        distance: $distance,
        temps_vol_estime: $temps_vol_estime
    }]->(p2)
    """
    tx.run(query,
           port_depart=port_depart,
           port_arrivee=port_arrivee,
           distance=distance,
           temps_vol_estime=temps_vol_estime)


def creer_routes_bidirectionnelles(tx, port_depart: str, port_arrivee: str, distance: float):
    """Créer des routes dans les deux sens"""
    creer_route(tx, port_depart, port_arrivee, distance)
    creer_route(tx, port_arrivee, port_depart, distance)


# ========== Fonctions pour les Livraisons ==========

def creer_livraison_node(tx, livraison: dict):
    """Créer un nœud Livraison dans Neo4J"""
    query = """
    CREATE (l:Livraison {
        livraison_id: $livraison_id,
        commande_id: $commande_id,
        hydravion_id: $hydravion_id,
        distance_totale: $distance_totale,
        consommation_estimee: $consommation_estimee,
        date_depart: $date_depart,
        statut: $statut
    })
    RETURN l
    """
    result = tx.run(query,
                    livraison_id=str(livraison["_id"]),
                    commande_id=livraison["commande_id"],
                    hydravion_id=livraison["hydravion_id"],
                    distance_totale=livraison["distance_totale"],
                    consommation_estimee=livraison["consommation_estimee"],
                    date_depart=livraison["date_depart"].isoformat(),
                    statut=livraison["statut"])
    return result.single()


def lier_livraison_itineraire(tx, livraison_id: str, itineraire: list):
    """Créer les relations VISITE entre une livraison et les ports de l'itinéraire"""
    for index, port_nom in enumerate(itineraire):
        query = """
        MATCH (l:Livraison {livraison_id: $livraison_id})
        MATCH (p:Port {nom: $port_nom})
        CREATE (l)-[:VISITE {ordre: $ordre}]->(p)
        """
        tx.run(query, livraison_id=livraison_id, port_nom=port_nom, ordre=index)


# ========== Fonctions de requête ==========

def obtenir_tous_les_ports(tx):
    """Récupérer tous les ports"""
    query = "MATCH (p:Port) RETURN p"
    result = tx.run(query)
    return [record["p"] for record in result]


def obtenir_route_optimale(tx, port_depart: str, port_arrivee: str):
    """Trouver la route la plus courte entre deux ports"""
    query = """
    MATCH path = shortestPath((p1:Port {nom: $port_depart})-[:ROUTE*]-(p2:Port {nom: $port_arrivee}))
    RETURN path,
           reduce(dist = 0, rel in relationships(path) | dist + rel.distance) as distance_totale
    """
    result = tx.run(query, port_depart=port_depart, port_arrivee=port_arrivee)
    return result.single()


def obtenir_ports_par_ile(tx, ile_nom: str):
    """Récupérer tous les ports d'une île"""
    query = """
    MATCH (p:Port)-[:SITUE_SUR]->(i:Ile {nom: $ile_nom})
    RETURN p
    """
    result = tx.run(query, ile_nom=ile_nom)
    return [record["p"] for record in result]


def obtenir_itineraire_multi_ports(tx, ports: list):
    """
    Calculer un itinéraire optimisé pour visiter plusieurs ports
    (problème du voyageur de commerce simplifié)
    """
    # Pour simplifier, on utilise l'ordre donné et on calcule la distance totale
    distance_totale = 0
    itineraire = []

    for i in range(len(ports) - 1):
        query = """
        MATCH (p1:Port {nom: $port1})-[r:ROUTE]->(p2:Port {nom: $port2})
        RETURN r.distance as distance
        """
        result = tx.run(query, port1=ports[i], port2=ports[i+1])
        record = result.single()
        if record:
            distance_totale += record["distance"]
            itineraire.append({
                "depart": ports[i],
                "arrivee": ports[i+1],
                "distance": record["distance"]
            })

    return {
        "itineraire": itineraire,
        "distance_totale": distance_totale
    }


def close_driver():
    """Fermer le driver Neo4J"""
    driver.close()
    logger.info("Connexion Neo4J fermée")
