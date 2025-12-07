import { getSession } from "./neo4j.js";

export const Neo4jRoutes = async () => {
  const session = getSession();
  try {
    console.log("Initialisation des routes et stationnements Neo4j...");

    // ============================
    //  STATIONNEMENTS HYDRAVIONS
    // ============================
    const stationnements = [
      ["H1", "P1"],
      ["H2", "P4"],
      ["H3", "P7"],
      ["H4", "P10"],
      ["H5", "P13"],
    ];

    for (const [hydra, port] of stationnements) {
      await session.run(
        `
        MATCH (h:Hydravion {id: $hydra}), (p:Port {id: $port})
        MERGE (h)-[:STATIONNE_A]->(p)
      `,
        { hydra, port }
      );
    }

    // ============================
    //  ROUTES ENTRE PORTS
    //  Réseau réaliste simplifié
    // ============================
    const routes = [
      ["P1", "P2", 12],
      ["P2", "P3", 18],
      ["P3", "P4", 20],
      ["P4", "P5", 15],
      ["P5", "P6", 22],
      ["P6", "P7", 10],
      ["P7", "P8", 14],
      ["P8", "P9", 25],
      ["P9", "P10", 30],
      ["P10", "P11", 16],
      ["P11", "P12", 19],
      ["P12", "P13", 21],
      ["P13", "P14", 17],
      ["P14", "P15", 23],
      ["P15", "P16", 11],
      ["P16", "P17", 26],

      // Quelques connexions transversales
      ["P1", "P5", 33],
      ["P3", "P7", 29],
      ["P4", "P9", 41],
      ["P6", "P12", 45],
      ["P8", "P14", 52],
      ["P10", "P16", 48],
    ];

    for (const [from, to, km] of routes) {
      await session.run(
        `
        MATCH (a:Port {id: $from}), (b:Port {id: $to})
        MERGE (a)-[:ROUTE {km: $km}]->(b)
        MERGE (b)-[:ROUTE {km: $km}]->(a)
      `,
        { from, to, km }
      );
    }

    console.log("Routes + stationnements Neo4j OK !");
  } catch (err) {
    console.error("Erreur Neo4jRoutes :", err);
  } finally {
    await session.close();
  }
};
