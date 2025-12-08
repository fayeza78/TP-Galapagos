from ariadne import gql

type_defs = gql("""
    # ========== Types de base ==========

    type Coordonnees {
        latitude: Float!
        longitude: Float!
    }

    # ========== Types MongoDB ==========

    type Hydravion {
        id: ID!
        nom: String!
        modele: String!
        capacite_caisses: Int!
        consommation_carburant: Float!
        statut: String!
        position: Coordonnees
        port_actuel: String
        carburant_actuel: Float
    }

    type Client {
        id: ID!
        nom: String!
        prenom: String!
        email: String!
        telephone: String!
        role: String!
        organisation: String!
        ile_principale: String!
    }

    type Produit {
        id: ID!
        nom: String!
        description: String!
        categorie: String!
        poids: Float!
        dimensions: Dimensions!
        stock_disponible: Int!
    }

    type Dimensions {
        hauteur: Float!
        largeur: Float!
        profondeur: Float!
    }

    type Commande {
        id: ID!
        client_id: String!
        client: Client
        produits: [ProduitCommande!]!
        port_destination: String!
        nombre_caisses_requises: Int!
        date_commande: String!
        date_livraison_souhaitee: String
        statut: String!
        priorite: Int!
    }

    type ProduitCommande {
        produit_id: String!
        produit: Produit
        quantite: Int!
    }

    type Stock {
        id: ID!
        produit_id: String!
        produit: Produit
        quantite_disponible: Int!
        quantite_reservee: Int!
        seuil_alerte: Int!
        derniere_mise_a_jour: String!
    }

    type Locker {
        id: ID!
        numero: Int!
        ile: String!
        port: String!
        taille_caisse: Int!
        statut: String!
        commande_id: String
        date_remplissage: String
    }

    type Livraison {
        id: ID!
        commande_id: String!
        commande: Commande
        hydravion_id: String!
        hydravion: Hydravion
        itineraire: [String!]!
        caisses_livrees: Int!
        distance_totale: Float!
        consommation_estimee: Float!
        date_depart: String!
        date_arrivee_estimee: String!
        date_arrivee_reelle: String
        statut: String!
    }

    # ========== Types Neo4J ==========

    type Ile {
        nom: String!
        coordonnees: Coordonnees!
        superficie: Float!
        population: Int
        description: String!
        ports: [Port!]
    }

    type Port {
        nom: String!
        ile: String!
        coordonnees: Coordonnees!
        nombre_lockers: Int!
        capacite_hydravions: Int!
        lockers_disponibles: Int
        lockers_occupes: Int
    }

    type Route {
        port_depart: String!
        port_arrivee: String!
        distance: Float!
        temps_vol_estime: Float!
    }

    type Itineraire {
        ports: [String!]!
        distance_totale: Float!
        temps_total_estime: Float!
        consommation_estimee: Float!
        segments: [SegmentItineraire!]!
    }

    type SegmentItineraire {
        depart: String!
        arrivee: String!
        distance: Float!
        temps_vol: Float!
    }

    # ========== Inputs ==========

    input CoordonneesInput {
        latitude: Float!
        longitude: Float!
    }

    input HydravionInput {
        nom: String!
        modele: String!
        capacite_caisses: Int!
        consommation_carburant: Float!
        statut: String!
        port_actuel: String
    }

    input ClientInput {
        nom: String!
        prenom: String!
        email: String!
        telephone: String!
        role: String!
        organisation: String!
        ile_principale: String!
    }

    input ProduitInput {
        nom: String!
        description: String!
        categorie: String!
        poids: Float!
        dimensions: DimensionsInput!
        stock_disponible: Int!
    }

    input DimensionsInput {
        hauteur: Float!
        largeur: Float!
        profondeur: Float!
    }

    input ProduitCommandeInput {
        produit_id: String!
        quantite: Int!
    }

    input CommandeInput {
        client_id: String!
        produits: [ProduitCommandeInput!]!
        port_destination: String!
        date_livraison_souhaitee: String
        priorite: Int
    }

    input IleInput {
        nom: String!
        coordonnees: CoordonneesInput!
        superficie: Float!
        population: Int
        description: String!
    }

    input PortInput {
        nom: String!
        ile: String!
        coordonnees: CoordonneesInput!
        nombre_lockers: Int!
        capacite_hydravions: Int!
    }

    # ========== Queries ==========

    type Query {
        # Hydravions
        hydravions: [Hydravion!]!
        hydravion(id: ID!): Hydravion
        hydravionsParStatut(statut: String!): [Hydravion!]!
        hydravionsDisponibles: [Hydravion!]!

        # Clients
        clients: [Client!]!
        client(id: ID!): Client
        clientsParIle(ile: String!): [Client!]!

        # Produits
        produits: [Produit!]!
        produit(id: ID!): Produit
        produitsParCategorie(categorie: String!): [Produit!]!
        produitsEnRupture: [Produit!]!

        # Commandes
        commandes: [Commande!]!
        commande(id: ID!): Commande
        commandesParStatut(statut: String!): [Commande!]!
        commandesParClient(client_id: String!): [Commande!]!

        # Stock
        stocks: [Stock!]!
        stock(produit_id: String!): Stock
        stocksEnAlerte: [Stock!]!

        # Lockers
        lockers: [Locker!]!
        lockersParPort(port: String!): [Locker!]!
        lockersDisponibles(port: String!): [Locker!]!
        lockersParIle(ile: String!): [Locker!]!

        # Livraisons
        livraisons: [Livraison!]!
        livraison(id: ID!): Livraison
        livraisonsEnCours: [Livraison!]!
        historiqueClient(client_id: String!): [Livraison!]!

        # Îles (Neo4J)
        iles: [Ile!]!
        ile(nom: String!): Ile

        # Ports (Neo4J)
        ports: [Port!]!
        port(nom: String!): Port
        portsParIle(ile: String!): [Port!]!

        # Routes et itinéraires (Neo4J)
        routeOptimale(port_depart: String!, port_arrivee: String!): Itineraire
        itineraireMultiPorts(ports: [String!]!): Itineraire

        # Requêtes complexes
        optimiserLivraison(
            port_depart: String!,
            commandes: [String!]!
        ): Itineraire
    }

    # ========== Mutations ==========

    type Mutation {
        # Hydravions
        creerHydravion(input: HydravionInput!): Hydravion!
        modifierStatutHydravion(id: ID!, statut: String!, position: CoordonneesInput): Hydravion!

        # Clients
        creerClient(input: ClientInput!): Client!

        # Produits
        creerProduit(input: ProduitInput!): Produit!
        mettreAJourStock(produit_id: String!, quantite: Int!): Stock!

        # Commandes
        creerCommande(input: CommandeInput!): Commande!
        modifierStatutCommande(id: ID!, statut: String!): Commande!

        # Livraisons
        creerLivraison(
            commande_id: String!,
            hydravion_id: String!,
            itineraire: [String!]!
        ): Livraison!

        # Lockers
        reserverLocker(port: String!, commande_id: String!): Locker!
        libererLocker(id: ID!): Locker!

        # Îles (Neo4J)
        creerIle(input: IleInput!): Ile!

        # Ports (Neo4J)
        creerPort(input: PortInput!): Port!

        # Routes (Neo4J)
        creerRoute(port_depart: String!, port_arrivee: String!): Route!
    }
""")
