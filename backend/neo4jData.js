import { getSession } from "./neo4j.js";

// Creation des noeuds
export async function initNeo4jData() {
  const session = getSession();
  try {
    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H1", modele: "Seaplane X", capacite: 100, consommation: 50 }
    );

    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H2", modele: "Poco 5", capacite: 10, consommation: 1 }
    );

    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H3", modele: "Charles", capacite: 150, consommation: 70 }
    );

    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H4", modele: "Vespa", capacite: 190, consommation: 100 }
    );

    await session.run(
      `CREATE (h:Hydravion {id: $id, modele: $modele, capacite: $capacite, consommation: $consommation})`,
      { id: "H5", modele: "Sharingan", capacite: 70, consommation: 30 }
    );

    await session.run(
      `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
      { id: "P1", nom: "Puerto Baquerizo Moreno", ile: "San Cristobal", lat: -0.9, lng: -89.6 }
    );

    await session.run(
      `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
      { id: "P2", nom: "Puerto Ayora", ile: "Santa Cruz", lat: -0.9, lng: -89.6 }
    );

    await session.run(
      `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
      { id: "P3", nom: "Puerto Villamil", ile: "Isabela", lat: -0.9, lng: -89.6 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P4", nom: "Puerto Chino Dock", ile: "San Cristóbal", lat: -0.88, lng: -89.58 }
    );
    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P5", nom: "Baltra", ile: "Baltra", lat: -0.4411, lng: -90.2839 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P6", nom: "Puerto Velasco Ibarra", ile: "Floreana", lat: -1.2744, lng: -90.4877 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P7", nom: "Post Office Bay", ile: "Floreana", lat: -1.3, lng: -90.44 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P8", nom: "Bartolomé Island Port", ile: "Bartolomé", lat: -0.29, lng: -90.21 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P9", nom: "Mosquera Island Dock", ile: "Mosquera", lat: -0.37, lng: -90.25 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P10", nom: "North Seymour Dock", ile: "North Seymour", lat: -0.28, lng: -90.3 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P11", nom: "Rábida Island Landing", ile: "Rábida", lat: -0.8, lng: -90.1 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P12", nom: "Española Island Port", ile: "Española", lat: -1.3, lng: -89.7 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P13", nom: "Santiago Sullivan Bay Dock", ile: "Santiago", lat: -0.24, lng: -90.7 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P14", nom: "Floreana – Devil’s Crown Access", ile: "Floreana", lat: -1.25, lng: -90.45 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P15", nom: "Fernandina Island Landing", ile: "Fernandina", lat: -0.28, lng: -91.4 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P16", nom: "Tintoreras Islet Dock", ile: "Isabela", lat: -0.97, lng: -91.0 }
    );

    await session.run(
    `CREATE (p:Port {id: $id, nom: $nom, ile: $ile, lat: $lat, lng: $lng})`,
    { id: "P17", nom: "Concha de Perla Dock", ile: "Isabela", lat: -0.95, lng: -90.95 }
    );

    console.log("Données Neo4j initialisées");
  } finally {
    await session.close();
  }
}
