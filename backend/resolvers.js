import { Client } from "./models/Client.js";
import { Produit } from "./models/Produit.js";
import { Commande } from "./models/Commande.js";
import { getSession } from "./neo4j.js";
import { Trajet } from "./models/Trajet.js";
import { Livraison } from "./models/Livraison.js";

export const resolvers = {
  Query: {
    hello: () => "Bienvenue dans Galapagos GraphQL !",
    clients: async () => await Client.find(),
    produits: async () => await Produit.find(),
    commandes: async () => await Commande.find().populate("clientId"),
    trajets: async () => await Trajet.find(),
    livraisons: async () => await Livraison.find(),
    dockers: async () => await Docker.find(),

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
  routes: async () => {
    const session = getSession();
    try {
      const result = await session.run(`
        MATCH (a:Port)-[r:ROUTE]->(b:Port)
        RETURN a.id AS from, b.id AS to, r.km AS km
      `);

      return result.records.map(row => ({
        from: row.get("from"),
        to: row.get("to"),
        km: row.get("km")
      }));
    } finally {
      await session.close();
    }
  }
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

    addTrajet: async (_, { hydravionId, depart, arrivee }) => {
    const session = getSession();
    try {
        
        const result = await session.run(
        `
        MATCH (a:Port {id: $depart})-[r:ROUTE]->(b:Port {id: $arrivee})
        RETURN r.km AS distance
        `,
        { depart, arrivee }
        );

        if (result.records.length === 0) {
        throw new Error("Aucune route entre ces ports !");
        }

        let distanceKm = result.records[0].get("distance");

        if (distanceKm && typeof distanceKm.toNumber === "function") {
        distanceKm = distanceKm.toNumber();
        } else {
        distanceKm = Number(distanceKm);
        }
        const vitesseKmH = 250;
        const dureeMinutes = Math.round((distanceKm / vitesseKmH) * 60);

        const trajet = new Trajet({
        hydravionId,
        depart,
        arrivee,
        distanceKm,
        dureeMinutes,
        });

        const saved = await trajet.save();
        return saved;
    } finally {
        await session.close();
    }
},
addLivraison: async (_, { commandeId, hydravionId, depart, arrivee, dateEstimee }) => {
  const session = getSession();
  try {
    
    const result = await session.run(`
      MATCH (a:Port {id: $depart})-[r:ROUTE]->(b:Port {id: $arrivee})
      RETURN r.km AS distance
    `, { depart, arrivee });

    if (result.records.length === 0) {
      throw new Error("Route introuvable !");
    }

    const distanceKm = result.records[0].get("distance");
    const dureeMinutes = Math.round(distanceKm / 250 * 60);

    
    const trajet = await new Trajet({
      hydravionId,
      depart,
      arrivee,
      distanceKm,
      dureeMinutes
    }).save();

    
    const livraison = await new Livraison({
      commandeId,
      trajetId: trajet._id,
      dateEstimee
    }).save();

    return livraison;

  } finally {
    await session.close();
  }
},

  },

  Commande: {
    client: async (parent) => {
      return await Client.findById(parent.clientId);
    },
  },
};
