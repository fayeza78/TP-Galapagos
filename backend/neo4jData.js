import { getSession } from "./neo4j.js";

export async function initNeo4jData() {
  const session = getSession();
  try {
    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H1", modele: "Seaplane X", capacite: 100, consommation: 50 }
    );

    await session.run(
      `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
      { id: "P1", nom: "Puerto Baquerizo Moreno", ile: "San Cristobal", lat: -0.9, lng: -89.6 }
    );

    console.log("Données Neo4j initialisées");
  } finally {
    await session.close();
  }
}
