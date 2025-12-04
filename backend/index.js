import { ApolloServer, gql } from "apollo-server";
import { connectMongo } from "./mongo.js";
import { getSession } from "./neo4j.js";

await connectMongo();

const typeDefs = gql`
  type Query {
    hello: String!
  }
`;

const resolvers = {
  Query: {
    hello: () => "Bienvenue dans Galapagos GraphQL !",
  },
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen({ port: 4000, host: '0.0.0.0' }).then(({ url }) => {
  console.log(`GraphQL prêt à ${url}`);
});

const session = getSession();
const result = await session.run("RETURN 'Neo4j fonctionne' AS message");
console.log(result.records[0].get("message"));
await session.close();
