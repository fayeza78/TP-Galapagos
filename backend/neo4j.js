import neo4j from "neo4j-driver";

export const driver = neo4j.driver(
  "bolt://neo4j:7687",
  neo4j.auth.basic("neo4j", "Fayeza123!")
);

export const getSession = () => driver.session();
