import { Client } from "./models/Client.js";
import { Produit } from "./models/Produit.js";
import { Commande } from "./models/Commande.js";
import { getSession } from "./neo4j.js";
import { Trajet } from "./models/Trajet.js";
import { Livraison } from "./models/Livraison.js";
import { Docker } from "./models/Docker.js";

// Constante pour le calcul de la durée de vol
const VITESSE_KM_H = 250; 

// Fonction utilitaire pour convertir les entiers Neo4j
const convertNeo4jInt = (neo4jInt) => {
    if (neo4jInt && typeof neo4jInt.toNumber === "function") {
        return neo4jInt.toNumber();
    }
    return Number(neo4jInt);
};

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

    // RESOLVER ENRICHI : Statut et position des Hydravions
    hydravions: async () => {
        const session = getSession();
        try {
            // 1. Récupérer les Hydravions de Neo4j et leur stationnement
            const result = await session.run(`
                MATCH (h:Hydravion)
                OPTIONAL MATCH (h)-[:STATIONNE_A]->(p:Port)
                RETURN h, p
            `);

            const hydravionsData = result.records.map(record => {
                const hydravionProps = record.get("h").properties;
                const portNode = record.get("p");
                
                let statut = portNode ? 'Stationné' : 'Entrepôt/Maintenance';
                let portActuel = portNode ? portNode.properties : null;
                
                return { ...hydravionProps, statut, portActuel };
            });

            // 2. Vérifier les trajets/livraisons en cours pour marquer 'En Vol'
            const livraisonsEnCours = await Livraison.find({ statut: "en cours" }).populate('trajetId');
            
            livraisonsEnCours.forEach(livraison => {
                const trajet = livraison.trajetId;
                if (trajet) {
                    const hydravion = hydravionsData.find(h => h.id === trajet.hydravionId);
                    if (hydravion) {
                        hydravion.statut = 'En Vol';
                        // Le port de départ est considéré comme la dernière position au début du vol
                        hydravion.portActuel = { id: trajet.depart, nom: `Port ${trajet.depart}` }; 
                    }
                }
            });

            return hydravionsData;
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
                km: convertNeo4jInt(row.get("km"))
            }));
        } finally {
            await session.close();
        }
    }, 

    // RESOLVER DU PLUS COURT CHEMIN
    shortestPath: async (_, { depart, arrivee }) => {
        const session = getSession();
        try {
            const result = await session.run(
                `
                MATCH (a:Port {id: $depart}), (b:Port {id: $arrivee})
                MATCH p = shortestPath((a)-[:ROUTE*]-(b))
                WHERE p IS NOT NULL
                RETURN REDUCE(km = 0, r IN relationships(p) | km + r.km) AS totalKm,
                       nodes(p) AS ports,
                       relationships(p) AS routes
                `,
                { depart, arrivee }
            );

            if (result.records.length === 0) {
                throw new Error("Aucun chemin trouvé entre les ports " + depart + " et " + arrivee + ".");
            }

            const record = result.records[0];
            let totalKm = convertNeo4jInt(record.get("totalKm"));
            const dureeMinutes = Math.round((totalKm / VITESSE_KM_H) * 60);

            const ports = record.get("ports");
            const routes = record.get("routes");
            
            const etapes = ports.map((port, index) => {
                let kmToNext = routes[index] ? convertNeo4jInt(routes[index].properties.km) : null;
                return {
                    portId: port.properties.id,
                    nom: port.properties.nom,
                    kmToNext: kmToNext,
                };
            });

            return {
                distanceKm: totalKm,
                dureeMinutes: dureeMinutes,
                etapes: etapes,
            };
        } finally {
            await session.close();
        }
    },
    
    // RESOLVER AJOUTÉ : Historique de livraison d'un client
    clientHistory: async (_, { clientId }) => {
      // Retourne toutes les commandes. Le resolver Commande: { livraisons } fait le reste.
      return await Commande.find({ clientId: clientId }).sort({ dateCommande: -1 });
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
      const commande = new Commande({ clientId, products, statut: "en attente" });
      return await commande.save();
    },

    // MUTATION OBSOLÈTE : Utiliser addLivraison à la place pour l'optimisation.
    addTrajet: async (_, { hydravionId, depart, arrivee }) => { 
        throw new Error("Utilisez la mutation addLivraison, qui calcule le trajet optimal via shortestPath."); 
    },

    // RESOLVER CORRIGÉ ET COMPLÉTÉ : addLivraison (avec Stock/Locker/ShortestPath)
    addLivraison: async (_, { commandeId, hydravionId, depart, arrivee, dateEstimee }) => {
        
        // 1. VÉRIFICATION DE LA COMMANDE ET DU STOCK
        const commande = await Commande.findById(commandeId);
        if (!commande) throw new Error("Commande introuvable.");

        let totalCaisseRequis = 0;
        
        for (const item of commande.products) {
            const produit = await Produit.findById(item.productId);
            if (!produit) throw new Error(`Produit ${item.productId} introuvable.`);
            
            if (produit.stock < item.quantity) {
                throw new Error(`Stock insuffisant pour le produit ${produit.name}. Requis: ${item.quantity}, Stock: ${produit.stock}`);
            }
            // Simplification : 1 caisse/locker par unité de produit commandée
            totalCaisseRequis += item.quantity; 
        }

        // 2. VÉRIFICATION DES LOCKERS (Dockers)
        const dockersDisponibles = await Docker.find({ disponible: true });
        if (dockersDisponibles.length < totalCaisseRequis) {
            throw new Error(`Manque de lockers (dockers) disponibles. Requis: ${totalCaisseRequis}, Disponibles: ${dockersDisponibles.length}`);
        }
        const dockersAAllouer = dockersDisponibles.slice(0, totalCaisseRequis);

        // 3. CALCUL DU TRAJET OPTIMAL
        const chemin = await resolvers.Query.shortestPath(null, { depart, arrivee });
        const { distanceKm, dureeMinutes, etapes } = chemin;

        // 4. CRÉATION DU TRAJET
        const trajet = await new Trajet({
            hydravionId,
            depart: etapes[0].portId, 
            arrivee: etapes[etapes.length - 1].portId, 
            distanceKm,
            dureeMinutes,
        }).save();

        // 5. MISE À JOUR DU STOCK (décrémentation)
        for (const item of commande.products) {
            await Produit.findByIdAndUpdate(item.productId, { $inc: { stock: -item.quantity } });
        }
        
        // 6. MISE À JOUR DES LOCKERS/DOCKERS (rendus indisponibles)
        const alloueDockerIds = [];
        for (const docker of dockersAAllouer) {
            await Docker.findByIdAndUpdate(docker._id, { disponible: false });
            alloueDockerIds.push(docker._id);
        }

        // 7. CRÉATION DES LIVRAISONS (une par caisse/locker)
        const livraisonsCrees = [];
        for (const dockerId of alloueDockerIds) {
            const livraison = await new Livraison({
                commandeId,
                trajetId: trajet._id,
                dockerId: dockerId, 
                dateEstimee,
                statut: "en cours", 
            }).save();
            livraisonsCrees.push(livraison);
        }

        // Mise à jour du statut de la commande
        await Commande.findByIdAndUpdate(commandeId, { statut: "en cours" });

        return livraisonsCrees[0]; 
    },

  },

  // RESOLVERS POUR LES TYPES IMBRIQUÉS
  
  // Résolveur pour le type Commande
  Commande: {
    client: async (parent) => await Client.findById(parent.clientId),
    livraisons: async (parent) => await Livraison.find({ commandeId: parent._id }).populate('trajetId dockerId'),
  },

  // Résolveur pour le type Livraison
  Livraison: {
    commande: async (parent) => await Commande.findById(parent.commandeId),
    trajet: async (parent) => await Trajet.findById(parent.trajetId),
    docker: async (parent) => await Docker.findById(parent.dockerId),
  },

  // Résolveur pour le type Hydravion
  Hydravion: {
    // Résout le champ portActuel en allant chercher les données complètes du port dans Neo4j
    portActuel: async (parent) => {
        if (!parent.portActuel || !parent.portActuel.id) return null;
        const session = getSession();
        try {
            const result = await session.run(`MATCH (p:Port {id: $id}) RETURN p`, { id: parent.portActuel.id });
            return result.records[0] ? result.records[0].get("p").properties : null;
        } finally {
            await session.close();
        }
    }
  },
};