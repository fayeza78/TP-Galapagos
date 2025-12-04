import { ApolloServer, gql } from "apollo-server";
import { connectMongo } from "./mongo.js";
import { getSession } from "./neo4j.js";
import { typeDefs } from "./typeDefs.js";
import { resolvers } from "./resolvers.js";
import { initNeo4jData } from "./neo4jData.js";

async function startServer() {
    try {
        await connectMongo();
        await initNeo4jData();


        const server = new ApolloServer({ typeDefs, resolvers });

        const { url } = await server.listen({ port: 4000, host: '0.0.0.0' });
        console.log(`GraphQL prêt à ${url}`);
        }catch (error) {
        console.error("Erreur lors du démarrage du serveur :", error);
    }
}
startServer();