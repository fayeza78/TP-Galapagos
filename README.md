# ESGI - Projet Galapagos: GraphQL / Neo4J / MongoDB

## Présentation

**Richnou Galap** est une société de transport de matériels scientifiques qui couvre les îles Galápagos. Cette application gère l'ensemble de la logistique de livraison avec une architecture mixte MongoDB/Neo4J et une API GraphQL.

### Contexte

Richnou Galap possède:
- Un entrepôt à **Puerto Baquerizo Moreno** (île San Cristóbal)
- Une flotte d'une dizaine d'hydravions
- Des clients scientifiques répartis sur 19 îles principales
- Des lockers automatiques sur différents ports
- Un stock de produits scientifiques à gérer

### Objectifs du système

Le système permet de répondre aux questions suivantes via GraphQL:
- Où se trouvent tous les hydravions à un instant T et leur état?
- Quel parcours permet d'optimiser le trajet pour livrer X ports avec Y clients?
- Quels lockers sont vides/pleins sur les différentes îles?
- Quel est l'état des stocks de produits?
- Quel est l'historique de livraison d'un client?

## Architecture

### Technologies utilisées

- **Backend**: Python 3.11 avec FastAPI
- **GraphQL**: Ariadne
- **Bases de données**:
  - **MongoDB**: Données transactionnelles (hydravions, clients, produits, commandes, stocks, lockers, livraisons)
  - **Neo4J**: Données géographiques et relationnelles (îles, ports, routes)
- **Conteneurisation**: Docker & Docker Compose

### Répartition des données

#### MongoDB
- **Hydravions**: Informations sur la flotte (modèle, capacité, statut, position)
- **Clients**: Scientifiques utilisant le service
- **Produits**: Matériel scientifique disponible
- **Commandes**: Demandes de livraison des clients
- **Stocks**: Gestion des quantités disponibles
- **Lockers**: État des casiers de stockage
- **Livraisons**: Historique et suivi des livraisons

#### Neo4J
- **Îles**: Nœuds représentant les îles avec coordonnées GPS réelles
- **Ports**: Points de livraison avec nombre de lockers et capacité
- **Routes**: Relations entre ports avec distance et temps de vol
- **Relations**: SITUE_SUR (Port→Île), ROUTE (Port→Port)

## Installation et Lancement

### Prérequis

- Docker et Docker Compose installés
- Au moins 4 GB de RAM disponible

### Lancement avec Docker Compose

docker-compose up --build

Les services seront disponibles sur:
- **API GraphQL**: http://localhost:8000/graphql
- **Neo4J Browser**: http://localhost:7474 (user: neo4j, password: galapagos2024)
- **MongoDB**: localhost:27017

### Seed des données

Pour initialiser les bases de données avec des données de test:


# Lancer le seed complet
cd seeds

# Ou individuellement
python seed_mongodb.py  # MongoDB uniquement
python seed_neo4j.py    # Neo4J uniquement


## Modèle de données

### MongoDB - Collections

#### Hydravions

{
  "nom": "Albatros-1",
  "modele": "petit|moyen|grand",
  "capacite_caisses": 50-150,
  "consommation_carburant": 15.0-25.0,
  "statut": "entrepot|port|en_vol|maintenance",
  "position": {"latitude": -0.7406, "longitude": -90.3120},
  "port_actuel": "Puerto Baquerizo Moreno",
  "carburant_actuel": 100.0
}

#### Clients

{
  "nom": "Darwin",
  "prenom": "Charles",
  "email": "c.darwin@research.org",
  "telephone": "+593-xxx-xxx-xxx",
  "role": "biologiste_marin|volcanologue|zoologue|botaniste|geologue",
  "organisation": "Charles Darwin Research Station",
  "ile_principale": "Santa Cruz"
}


#### Produits

{
  "nom": "Équipement de plongée profonde",
  "description": "Kit complet...",
  "categorie": "equipement_plongee|materiel_laboratoire|...",
  "poids": 25.5,
  "dimensions": {"hauteur": 80.0, "largeur": 60.0, "profondeur": 40.0},
  "stock_disponible": 15
}

#### Commandes

{
  "client_id": "ObjectId",
  "produits": [{"produit_id": "ObjectId", "quantite": 2}],
  "port_destination": "Puerto Ayora",
  "nombre_caisses_requises": 3,
  "date_commande": "2024-12-06T10:00:00",
  "statut": "en_attente|en_preparation|prete|en_livraison|livree",
  "priorite": 1-5
}

### Neo4J - Graphe

#### Nœuds

**Île**

(i:Ile {
  nom: "San Cristóbal",
  latitude: -0.8406,
  longitude: -89.4325,
  superficie: 558.0,
  population: 7000,
  description: "..."
})


**Port**

(p:Port {
  nom: "Puerto Baquerizo Moreno",
  ile: "San Cristóbal",
  latitude: -0.9019,
  longitude: -89.6108,
  nombre_lockers: 50,
  capacite_hydravions: 5
})

#### Relations


(port)-[:SITUE_SUR]->(ile)
(port1)-[:ROUTE {distance: 85.5, temps_vol_estime: 25.65}]->(port2)


## Exemples de requêtes GraphQL

### Consulter tous les hydravions

query {
  hydravions {
    id
    nom
    modele
    statut
    capacite_caisses
    carburant_actuel
    port_actuel
  }
}

### Trouver les hydravions disponibles


query {
  hydravionsDisponibles {
    nom
    modele
    capacite_caisses
    port_actuel
  }
}

### Consulter les îles et leurs ports


query {
  iles {
    nom
    coordonnees {
      latitude
      longitude
    }
    superficie
    population
    ports {
      nom
      nombre_lockers
      lockers_disponibles
      lockers_occupes
    }
  }
}

### Trouver la route optimale entre deux ports


query {
  routeOptimale(
    port_depart: "Puerto Baquerizo Moreno"
    port_arrivee: "Puerto Ayora"
  ) {
    ports
    distance_totale
    temps_total_estime
    consommation_estimee
  }
}

### Calculer un itinéraire multi-ports


query {
  itineraireMultiPorts(
    ports: [
      "Puerto Baquerizo Moreno",
      "Puerto Ayora",
      "Puerto Villamil"
    ]
  ) {
    ports
    distance_totale
    temps_total_estime
    consommation_estimee
    segments {
      depart
      arrivee
      distance
      temps_vol
    }
  }
}


### Consulter l'historique d'un client


query {
  client(id: "client_id_here") {
    nom
    prenom
    organisation
  }

  historiqueClient(client_id: "client_id_here") {
    id
    date_depart
    date_arrivee_reelle
    statut
    itineraire
    distance_totale
    hydravion {
      nom
      modele
    }
  }
}


### Vérifier les lockers disponibles sur un port

query {
  lockersDisponibles(port: "Puerto Ayora") {
    numero
    ile
    port
    statut
  }

  port(nom: "Puerto Ayora") {
    lockers_disponibles
    lockers_occupes
    capacite_hydravions
  }
}

### Créer une nouvelle commande


mutation {
  creerCommande(input: {
    client_id: "client_id_here"
    produits: [
      {produit_id: "produit_id_1", quantite: 2}
      {produit_id: "produit_id_2", quantite: 1}
    ]
    port_destination: "Puerto Ayora"
    priorite: 3
  }) {
    id
    nombre_caisses_requises
    statut
    date_commande
  }
}


### Créer une livraison


mutation {
  creerLivraison(
    commande_id: "commande_id_here"
    hydravion_id: "hydravion_id_here"
    itineraire: ["Puerto Baquerizo Moreno", "Puerto Ayora"]
  ) {
    id
    distance_totale
    consommation_estimee
    statut
  }
}


### Réserver un locker


mutation {
  reserverLocker(
    port: "Puerto Ayora"
    commande_id: "commande_id_here"
  ) {
    numero
    port
    statut
    date_remplissage
  }
}


## Structure du projet

Logistics-app/
├── backend/
│   ├── app.py                      # Application FastAPI principale
│   ├── db_connection.py            # Connexion MongoDB
│   ├── graph_db_connection.py      # Connexion Neo4J
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── models.py               # Modèles Pydantic
│   ├── graphql/
│   │   ├── __init__.py
│   │   ├── schema.py               # Schéma GraphQL
│   │   └── resolvers.py            # Resolvers GraphQL
│   └── seeds/
│       ├── __init__.py
│       ├── seed_mongodb.py         # Seed MongoDB
│       ├── seed_neo4j.py           # Seed Neo4J
│       └── seed_all.py             # Seed complet
├── docker-compose.yml
└── README.md

### technologies Frontend

Html, tailwind css et javascript


### Accéder au shell d'un conteneur

# API
docker exec -it galapagos-api bash

# MongoDB
docker exec -it galapagos-mongodb mongosh

# Neo4J (Cypher Shell)
docker exec -it galapagos-neo4j cypher-shell -u neo4j -p galapagos2024


### Requêtes Cypher utiles (Neo4J)


// Voir toutes les îles
MATCH (i:Ile) RETURN i

// Voir tous les ports d'une île
MATCH (p:Port)-[:SITUE_SUR]->(i:Ile {nom: "Santa Cruz"})
RETURN p

// Trouver le chemin le plus court entre deux ports
MATCH path = shortestPath(
  (p1:Port {nom: "Puerto Baquerizo Moreno"})-[:ROUTE*]-(p2:Port {nom: "Puerto Villamil"})
)
RETURN path

// Calculer la distance totale d'un chemin
MATCH path = shortestPath(
  (p1:Port {nom: "Puerto Ayora"})-[:ROUTE*]-(p2:Port {nom: "Darwin Bay"})
)
RETURN reduce(dist = 0, rel in relationships(path) | dist + rel.distance) as distance_totale


## Fonctionnalités clés

### Calcul des distances
- Utilisation de la formule de Haversine pour calculer les distances réelles entre ports
- Coordonnées GPS réelles des îles Galápagos

### Optimisation des routes
- Algorithme de plus court chemin via Neo4J
- Calcul de la consommation de carburant selon la distance
- Prise en compte de la capacité des hydravions

### Gestion des lockers
- Système de réservation automatique
- Vérification de disponibilité par port
- Statuts: vide, plein, réservé

### Gestion du stock
- Suivi en temps réel
- Alertes de stock bas
- Réservation lors de commandes

## Configuration

### Variables d'environnement

Les variables sont définies dans `docker-compose.yml`:


MONGODB_URL=mongodb://mongodb:27017
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=galapagos2024


## Notes importantes

- **Coordonnées GPS**: Toutes les coordonnées des îles et ports sont réelles
- **Distances**: Calculées avec la formule de Haversine (ligne droite)
- **Vitesse hydravions**: 200 km/h en moyenne
- **Consommation**: Variable selon le modèle (15-25L/100km)
- **Caisses**: Taille standardisée, 1 locker = 1 caisse


