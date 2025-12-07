import { gql } from "apollo-server";

export const typeDefs = gql`
type Client {
  id: ID!
  name: String!
  type: String
  email: String
}

type Produit {
  id: ID!
  name: String!
  description: String
  price: Float
  stock: Int
}

type Commande {
  id: ID!
  client: Client
  products: [ProduitInCommande!]!
  statut: String
  dateCommande: String
  livraisons: [Livraison!]
}

type ProduitInCommande {
  productId: ID!
  quantity: Int!
}

type Query {
  hello: String!
  clients: [Client!]!
  produits: [Produit!]!
  commandes: [Commande!]!
  testNeo4j: String!
}

type Mutation {
  addClient(name: String!, type: String, email: String): Client!
  addProduit(name: String!, description: String, price: Float, stock: Int): Produit!
  addCommande(clientId: ID!, products: [ProduitInCommandeInput!]!): Commande!
  addTrajet(hydravionId: ID!, depart: String!, arrivee: String!): Trajet!
  addLivraison(commandeId: ID!, hydravionId: ID!, dockerId: ID, dateEstimee: String): Livraison!
}

input ProduitInCommandeInput {
  productId: ID!
  quantity: Int!
}
type Hydravion {
  id: ID!
  modele: String!
  capacite: Int
  consommation: Int
  statut: String! 
  portActuel: Port 
}

type Port {
  id: ID!
  nom: String!
  ile: String
  lat: Float
  lng: Float
}
type Route {
  from: String!
  to: String!
  km: Float!
}

type Trajet {
  id: ID!
  hydravionId: ID!
  depart: String!
  arrivee: String!
  distanceKm: Float
  dureeMinutes: Float
}

type Livraison {
  id: ID!
  commande: Commande!
  trajet: Trajet!
  docker: Docker
  statut: String
  dateEstimee: String
}
type Docker {
  id: ID!
  name: String!
  disponible: Boolean!
}

type CheminEtape {
  portId: ID!
  nom: String!
  kmToNext: Float
}

type Chemin {
  distanceKm: Float!
  dureeMinutes: Float!
  etapes: [CheminEtape!]!
}

extend type Query {
  hydravions: [Hydravion!]!
  ports: [Port!]!
  routes: [Route!]!
  trajets: [Trajet!]!
  livraisons: [Livraison!]!   
  dockers: [Docker!]!
  shortestPath(depart: ID!, arrivee: ID!): Chemin
  clientHistory(clientId: ID!): [Commande!]!
}
`;



