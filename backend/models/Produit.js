import mongoose from "mongoose";

const produitSchema = new mongoose.Schema({
  name: String,
  description: String,
  price: Number,
  stock: Number,
});
export const Produit = mongoose.model("Produit", produitSchema);