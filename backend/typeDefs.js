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
}

type Port {
  id: ID!
  nom: String!
  ile: String
  lat: Float
  lng: Float
}

extend type Query {
  hydravions: [Hydravion!]!
  ports: [Port!]!
}
`;
