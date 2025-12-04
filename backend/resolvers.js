import { Client } from "./models/Client.js";
import { Produit } from "./models/Produit.js";
import { Commande } from "./models/Commande.js";
import { getSession } from "./neo4j.js";

export const resolvers = {
  Query: {
    hello: () => "Bienvenue dans Galapagos GraphQL !",
    clients: async () => await Client.find(),
    produits: async () => await Produit.find(),
    commandes: async () => await Commande.find().populate("clientId"),
    testNeo4j: async () => {
      const session = getSession();
      try {
        const result = await session.run("RETURN 'Neo4j fonctionne' AS message");
        return result.records[0].get("message");
      } finally {
        await session.close();
      }
    },
  hydravions: async () => {
    const session = getSession();
    try {
      const result = await session.run("MATCH (h:Hydravion) RETURN h");
      return result.records.map(record => record.get("h").properties);
    } finally {
      await session.close();
    }
  },

  ports: async () => {
    const session = getSession();
    try {
      const result = await session.run("MATCH (p:Port) RETURN p");
      return result.records.map(record => record.get("p").properties);
    } finally {
      await session.close();
    }
  },
  },
  Mutation: {
    addClient: async (_, { name, type, email }) => {
      const client = new Client({ name, type, email });
      return await client.save();
    },

    addProduit: async (_, { name, description, price, stock }) => {
      const produit = new Produit({ name, description, price, stock });
      return await produit.save();
    },

    addCommande: async (_, { clientId, products }) => {
      const commande = new Commande({ clientId, products, statut: "en cours" });
      return await commande.save();
    },
  },

  Commande: {
    client: async (parent) => {
      return await Client.findById(parent.clientId);
    },
  },
};
