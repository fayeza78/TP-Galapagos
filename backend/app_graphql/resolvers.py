from ariadne import QueryType, MutationType, ObjectType
from bson import ObjectId
from datetime import datetime
from db_connection import get_database
from graph_db_connection import (
    driver,
    creer_ile, creer_port, lier_port_a_ile,
    creer_routes_bidirectionnelles, calculer_distance,
    obtenir_tous_les_ports, obtenir_route_optimale,
    obtenir_ports_par_ile, obtenir_itineraire_multi_ports
)

query = QueryType()
mutation = MutationType()

# Object Types pour les résolutions de champs
hydravion_type = ObjectType("Hydravion")
client_type = ObjectType("Client")
commande_type = ObjectType("Commande")
produit_commande_type = ObjectType("ProduitCommande")
stock_type = ObjectType("Stock")
livraison_type = ObjectType("Livraison")
ile_type = ObjectType("Ile")
port_type = ObjectType("Port")


# ========== Helpers ==========

def serialize_mongo_doc(doc):
    """Convertir un document MongoDB en dict avec id au lieu de _id"""
    if doc is None:
        return None
    doc["id"] = str(doc["_id"])
    return doc


async def get_client_by_id(db, client_id):
    """Récupérer un client par son ID"""
    client = await db.clients.find_one({"_id": ObjectId(client_id)})
    return serialize_mongo_doc(client)


async def get_produit_by_id(db, produit_id):
    """Récupérer un produit par son ID"""
    produit = await db.produits.find_one({"_id": ObjectId(produit_id)})
    return serialize_mongo_doc(produit)


# ========== Resolvers pour les champs d'objets ==========

@commande_type.field("client")
async def resolve_commande_client(obj, info):
    """Résoudre le client d'une commande"""
    db = get_database()
    return await get_client_by_id(db, obj["client_id"])


@produit_commande_type.field("produit")
async def resolve_produit_commande_produit(obj, info):
    """Résoudre le produit d'un ProduitCommande"""
    db = get_database()
    return await get_produit_by_id(db, obj["produit_id"])


@commande_type.field("produits")
def resolve_commande_produits(obj, info):
    """Résoudre la liste des produits d'une commande"""
    return obj.get("produits", [])


@stock_type.field("produit")
async def resolve_stock_produit(obj, info):
    """Résoudre le produit d'un stock"""
    db = get_database()
    return await get_produit_by_id(db, obj["produit_id"])


@livraison_type.field("commande")
async def resolve_livraison_commande(obj, info):
    """Résoudre la commande d'une livraison"""
    db = get_database()
    commande = await db.commandes.find_one({"_id": ObjectId(obj["commande_id"])})
    return serialize_mongo_doc(commande)


@livraison_type.field("hydravion")
async def resolve_livraison_hydravion(obj, info):
    """Résoudre l'hydravion d'une livraison"""
    db = get_database()
    hydravion = await db.hydravions.find_one({"_id": ObjectId(obj["hydravion_id"])})
    return serialize_mongo_doc(hydravion)


@ile_type.field("ports")
def resolve_ile_ports(obj, info):
    """Résoudre les ports d'une île"""
    with driver.session() as session:
        ports = session.execute_read(obtenir_ports_par_ile, obj["nom"])
        return [dict(p) for p in ports]


@port_type.field("lockers_disponibles")
async def resolve_port_lockers_disponibles(obj, info):
    """Compter les lockers disponibles d'un port"""
    db = get_database()
    count = await db.lockers.count_documents({
        "port": obj["nom"],
        "statut": "vide"
    })
    return count


@port_type.field("lockers_occupes")
async def resolve_port_lockers_occupes(obj, info):
    """Compter les lockers occupés d'un port"""
    db = get_database()
    count = await db.lockers.count_documents({
        "port": obj["nom"],
        "statut": "plein"
    })
    return count


# ========== Query Resolvers ==========

# Hydravions
@query.field("hydravions")
async def resolve_hydravions(_, info):
    db = get_database()
    hydravions = []
    async for h in db.hydravions.find({}):
        hydravions.append(serialize_mongo_doc(h))
    return hydravions


@query.field("hydravion")
async def resolve_hydravion(_, info, id):
    db = get_database()
    hydravion = await db.hydravions.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(hydravion)


@query.field("hydravionsParStatut")
async def resolve_hydravions_par_statut(_, info, statut):
    db = get_database()
    hydravions = []
    async for h in db.hydravions.find({"statut": statut}):
        hydravions.append(serialize_mongo_doc(h))
    return hydravions


@query.field("hydravionsDisponibles")
async def resolve_hydravions_disponibles(_, info):
    db = get_database()
    hydravions = []
    async for h in db.hydravions.find({"statut": {"$in": ["entrepot", "port"]}}):
        hydravions.append(serialize_mongo_doc(h))
    return hydravions


# Clients
@query.field("clients")
async def resolve_clients(_, info):
    db = get_database()
    clients = []
    async for c in db.clients.find({}):
        clients.append(serialize_mongo_doc(c))
    return clients


@query.field("client")
async def resolve_client(_, info, id):
    db = get_database()
    client = await db.clients.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(client)


@query.field("clientsParIle")
async def resolve_clients_par_ile(_, info, ile):
    db = get_database()
    clients = []
    async for c in db.clients.find({"ile_principale": ile}):
        clients.append(serialize_mongo_doc(c))
    return clients


# Produits
@query.field("produits")
async def resolve_produits(_, info):
    db = get_database()
    produits = []
    async for p in db.produits.find({}):
        produits.append(serialize_mongo_doc(p))
    return produits


@query.field("produit")
async def resolve_produit(_, info, id):
    db = get_database()
    produit = await db.produits.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(produit)


@query.field("produitsParCategorie")
async def resolve_produits_par_categorie(_, info, categorie):
    db = get_database()
    produits = []
    async for p in db.produits.find({"categorie": categorie}):
        produits.append(serialize_mongo_doc(p))
    return produits


@query.field("produitsEnRupture")
async def resolve_produits_en_rupture(_, info):
    db = get_database()
    produits = []
    async for p in db.produits.find({"stock_disponible": {"$lte": 0}}):
        produits.append(serialize_mongo_doc(p))
    return produits


# Commandes
@query.field("commandes")
async def resolve_commandes(_, info):
    db = get_database()
    commandes = []
    async for c in db.commandes.find({}):
        commandes.append(serialize_mongo_doc(c))
    return commandes


@query.field("commande")
async def resolve_commande(_, info, id):
    db = get_database()
    commande = await db.commandes.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(commande)


@query.field("commandesParStatut")
async def resolve_commandes_par_statut(_, info, statut):
    db = get_database()
    commandes = []
    async for c in db.commandes.find({"statut": statut}):
        commandes.append(serialize_mongo_doc(c))
    return commandes


@query.field("commandesParClient")
async def resolve_commandes_par_client(_, info, client_id):
    db = get_database()
    commandes = []
    async for c in db.commandes.find({"client_id": client_id}):
        commandes.append(serialize_mongo_doc(c))
    return commandes


# Stocks
@query.field("stocks")
async def resolve_stocks(_, info):
    db = get_database()
    stocks = []
    async for s in db.stocks.find({}):
        stocks.append(serialize_mongo_doc(s))
    return stocks


@query.field("stock")
async def resolve_stock(_, info, produit_id):
    db = get_database()
    stock = await db.stocks.find_one({"produit_id": produit_id})
    return serialize_mongo_doc(stock)


@query.field("stocksEnAlerte")
async def resolve_stocks_en_alerte(_, info):
    db = get_database()
    stocks = []
    async for s in db.stocks.find({}):
        if s["quantite_disponible"] <= s["seuil_alerte"]:
            stocks.append(serialize_mongo_doc(s))
    return stocks


# Lockers
@query.field("lockers")
async def resolve_lockers(_, info):
    db = get_database()
    lockers = []
    async for l in db.lockers.find({}):
        lockers.append(serialize_mongo_doc(l))
    return lockers


@query.field("lockersParPort")
async def resolve_lockers_par_port(_, info, port):
    db = get_database()
    lockers = []
    async for l in db.lockers.find({"port": port}):
        lockers.append(serialize_mongo_doc(l))
    return lockers


@query.field("lockersDisponibles")
async def resolve_lockers_disponibles(_, info, port):
    db = get_database()
    lockers = []
    async for l in db.lockers.find({"port": port, "statut": "vide"}):
        lockers.append(serialize_mongo_doc(l))
    return lockers


@query.field("lockersParIle")
async def resolve_lockers_par_ile(_, info, ile):
    db = get_database()
    lockers = []
    async for l in db.lockers.find({"ile": ile}):
        lockers.append(serialize_mongo_doc(l))
    return lockers


# Livraisons
@query.field("livraisons")
async def resolve_livraisons(_, info):
    db = get_database()
    livraisons = []
    async for l in db.livraisons.find({}):
        livraisons.append(serialize_mongo_doc(l))
    return livraisons


@query.field("livraison")
async def resolve_livraison(_, info, id):
    db = get_database()
    livraison = await db.livraisons.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(livraison)


@query.field("livraisonsEnCours")
async def resolve_livraisons_en_cours(_, info):
    db = get_database()
    livraisons = []
    async for l in db.livraisons.find({"statut": {"$in": ["en_cours", "en_vol"]}}):
        livraisons.append(serialize_mongo_doc(l))
    return livraisons


@query.field("historiqueClient")
async def resolve_historique_client(_, info, client_id):
    db = get_database()
    # Trouve toutes les commandes du client
    commandes = []
    async for c in db.commandes.find({"client_id": client_id}):
        commandes.append(str(c["_id"]))

    # Trouve toutes les livraisons pour ces commandes
    livraisons = []
    async for l in db.livraisons.find({"commande_id": {"$in": commandes}}):
        livraisons.append(serialize_mongo_doc(l))
    return livraisons


# Îles (Neo4J)
@query.field("iles")
def resolve_iles(_, info):
    with driver.session() as session:
        result = session.run("MATCH (i:Ile) RETURN i")
        iles = []
        for record in result:
            ile_node = record["i"]
            iles.append({
                "nom": ile_node["nom"],
                "coordonnees": {
                    "latitude": ile_node["latitude"],
                    "longitude": ile_node["longitude"]
                },
                "superficie": ile_node["superficie"],
                "population": ile_node.get("population", 0),
                "description": ile_node["description"]
            })
        return iles


@query.field("ile")
def resolve_ile(_, info, nom):
    with driver.session() as session:
        result = session.run("MATCH (i:Ile {nom: $nom}) RETURN i", nom=nom)
        record = result.single()
        if record:
            ile_node = record["i"]
            return {
                "nom": ile_node["nom"],
                "coordonnees": {
                    "latitude": ile_node["latitude"],
                    "longitude": ile_node["longitude"]
                },
                "superficie": ile_node["superficie"],
                "population": ile_node.get("population", 0),
                "description": ile_node["description"]
            }
        return None


# Ports (Neo4J)
@query.field("ports")
def resolve_ports(_, info):
    with driver.session() as session:
        ports = session.execute_read(obtenir_tous_les_ports)
        return [dict(p) for p in ports]


@query.field("port")
def resolve_port(_, info, nom):
    with driver.session() as session:
        result = session.run("MATCH (p:Port {nom: $nom}) RETURN p", nom=nom)
        record = result.single()
        if record:
            return dict(record["p"])
        return None


@query.field("portsParIle")
def resolve_ports_par_ile(_, info, ile):
    with driver.session() as session:
        ports = session.execute_read(obtenir_ports_par_ile, ile)
        return [dict(p) for p in ports]


# Routes et itinéraires
@query.field("routeOptimale")
def resolve_route_optimale(_, info, port_depart, port_arrivee):
    with driver.session() as session:
        result = session.execute_read(obtenir_route_optimale, port_depart, port_arrivee)
        if result:
            
            return {
                "ports": [port_depart, port_arrivee],
                "distance_totale": result["distance_totale"],
                "temps_total_estime": (result["distance_totale"] / 200) * 60,
                "consommation_estimee": result["distance_totale"] * 0.20,
                "segments": []
            }
        return None


@query.field("itineraireMultiPorts")
def resolve_itineraire_multi_ports(_, info, ports):
    with driver.session() as session:
        result = session.execute_read(obtenir_itineraire_multi_ports, ports)
        return {
            "ports": ports,
            "distance_totale": result["distance_totale"],
            "temps_total_estime": (result["distance_totale"] / 200) * 60,
            "consommation_estimee": result["distance_totale"] * 0.20,
            "segments": result["itineraire"]
        }


# ========== Mutation Resolvers ==========

# Hydravions
@mutation.field("creerHydravion")
async def resolve_creer_hydravion(_, info, input):
    db = get_database()
    hydravion = {
        "nom": input["nom"],
        "modele": input["modele"],
        "capacite_caisses": input["capacite_caisses"],
        "consommation_carburant": input["consommation_carburant"],
        "statut": input["statut"],
        "port_actuel": input.get("port_actuel"),
        "carburant_actuel": 100.0
    }
    result = await db.hydravions.insert_one(hydravion)
    hydravion["_id"] = result.inserted_id
    return serialize_mongo_doc(hydravion)


@mutation.field("modifierStatutHydravion")
async def resolve_modifier_statut_hydravion(_, info, id, statut, position=None):
    db = get_database()
    update_data = {"statut": statut}
    if position:
        update_data["position"] = position

    await db.hydravions.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    hydravion = await db.hydravions.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(hydravion)


# Clients
@mutation.field("creerClient")
async def resolve_creer_client(_, info, input):
    db = get_database()
    client = dict(input)
    result = await db.clients.insert_one(client)
    client["_id"] = result.inserted_id
    return serialize_mongo_doc(client)


# Produits
@mutation.field("creerProduit")
async def resolve_creer_produit(_, info, input):
    db = get_database()
    produit = dict(input)
    result = await db.produits.insert_one(produit)
    produit["_id"] = result.inserted_id

    # Crée l'entrée de stock
    stock = {
        "produit_id": str(result.inserted_id),
        "quantite_disponible": produit["stock_disponible"],
        "quantite_reservee": 0,
        "seuil_alerte": 10,
        "derniere_mise_a_jour": datetime.now()
    }
    await db.stocks.insert_one(stock)

    return serialize_mongo_doc(produit)


@mutation.field("mettreAJourStock")
async def resolve_mettre_a_jour_stock(_, info, produit_id, quantite):
    db = get_database()
    await db.stocks.update_one(
        {"produit_id": produit_id},
        {
            "$set": {
                "quantite_disponible": quantite,
                "derniere_mise_a_jour": datetime.now()
            }
        }
    )
    stock = await db.stocks.find_one({"produit_id": produit_id})
    return serialize_mongo_doc(stock)


# Commandes
@mutation.field("creerCommande")
async def resolve_creer_commande(_, info, input):
    db = get_database()

    # Calcule le nombre de caisses requises
    # Simplification: 1 caisse par produit
    nombre_caisses = sum(p["quantite"] for p in input["produits"])

    commande = {
        "client_id": input["client_id"],
        "produits": input["produits"],
        "port_destination": input["port_destination"],
        "nombre_caisses_requises": nombre_caisses,
        "date_commande": datetime.now(),
        "date_livraison_souhaitee": input.get("date_livraison_souhaitee"),
        "statut": "en_attente",
        "priorite": input.get("priorite", 1)
    }

    result = await db.commandes.insert_one(commande)
    commande["_id"] = result.inserted_id
    return serialize_mongo_doc(commande)


@mutation.field("modifierStatutCommande")
async def resolve_modifier_statut_commande(_, info, id, statut):
    db = get_database()
    await db.commandes.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"statut": statut}}
    )
    commande = await db.commandes.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(commande)


# Livraisons
@mutation.field("creerLivraison")
async def resolve_creer_livraison(_, info, commande_id, hydravion_id, itineraire):
    db = get_database()

    # Récupére la commande pour avoir les infos
    commande = await db.commandes.find_one({"_id": ObjectId(commande_id)})

    # Calcule la distance totale via Neo4J
    with driver.session() as session:
        result = session.execute_read(obtenir_itineraire_multi_ports, itineraire)
        distance_totale = result["distance_totale"]

    # Récupère l'hydravion pour la consommation
    hydravion = await db.hydravions.find_one({"_id": ObjectId(hydravion_id)})
    consommation_estimee = distance_totale * (hydravion["consommation_carburant"] / 100)

    livraison = {
        "commande_id": commande_id,
        "hydravion_id": hydravion_id,
        "itineraire": itineraire,
        "caisses_livrees": commande["nombre_caisses_requises"],
        "distance_totale": distance_totale,
        "consommation_estimee": consommation_estimee,
        "date_depart": datetime.now(),
        "date_arrivee_estimee": datetime.now(),  # TODO: calculer avec vitesse
        "statut": "en_cours"
    }

    result = await db.livraisons.insert_one(livraison)
    livraison["_id"] = result.inserted_id

    # Mis à jour du statut de la commande
    await db.commandes.update_one(
        {"_id": ObjectId(commande_id)},
        {"$set": {"statut": "en_livraison"}}
    )

    return serialize_mongo_doc(livraison)


# Lockers
@mutation.field("reserverLocker")
async def resolve_reserver_locker(_, info, port, commande_id):
    db = get_database()

    # Trouve un locker disponible
    locker = await db.lockers.find_one({"port": port, "statut": "vide"})
    if not locker:
        raise Exception("Aucun locker disponible sur ce port")

    # Réserve le locker
    await db.lockers.update_one(
        {"_id": locker["_id"]},
        {
            "$set": {
                "statut": "reserve",
                "commande_id": commande_id,
                "date_remplissage": datetime.now()
            }
        }
    )

    locker = await db.lockers.find_one({"_id": locker["_id"]})
    return serialize_mongo_doc(locker)


@mutation.field("libererLocker")
async def resolve_liberer_locker(_, info, id):
    db = get_database()
    await db.lockers.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "statut": "vide",
                "commande_id": None,
                "date_remplissage": None
            }
        }
    )
    locker = await db.lockers.find_one({"_id": ObjectId(id)})
    return serialize_mongo_doc(locker)


# Îles (Neo4J)
@mutation.field("creerIle")
def resolve_creer_ile(_, info, input):
    with driver.session() as session:
        session.execute_write(creer_ile, dict(input))
    return dict(input)


# Ports (Neo4J)
@mutation.field("creerPort")
def resolve_creer_port(_, info, input):
    with driver.session() as session:
        session.execute_write(creer_port, dict(input))
        session.execute_write(lier_port_a_ile, input["nom"], input["ile"])
    return dict(input)


# Routes (Neo4J)
@mutation.field("creerRoute")
def resolve_creer_route(_, info, port_depart, port_arrivee):
    # Calcul la distance entre les deux ports
    with driver.session() as session:
        # Récupère les coordonnées des ports
        result1 = session.run("MATCH (p:Port {nom: $nom}) RETURN p", nom=port_depart)
        result2 = session.run("MATCH (p:Port {nom: $nom}) RETURN p", nom=port_arrivee)

        port1 = result1.single()["p"]
        port2 = result2.single()["p"]

        distance = calculer_distance(
            port1["latitude"], port1["longitude"],
            port2["latitude"], port2["longitude"]
        )

        session.execute_write(creer_routes_bidirectionnelles, port_depart, port_arrivee, distance)

    return {
        "port_depart": port_depart,
        "port_arrivee": port_arrivee,
        "distance": distance,
        "temps_vol_estime": (distance / 200) * 60
    }


# Export des resolvers
resolvers = [
    query,
    mutation,
    hydravion_type,
    client_type,
    commande_type,
    produit_commande_type,
    stock_type,
    livraison_type,
    ile_type,
    port_type
]
