import { ApolloServer, gql } from "apollo-server";

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
