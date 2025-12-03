import mongoose from "mongoose";

export async function connectMongo() {
  try {
    await mongoose.connect("mongodb://mongo:27017/galapagos");
    console.log("Tu es connecté à MongoDB");
  } catch (err) {
    console.error(err);
  }
}