import mongoose from "mongoose";

const livraisonSchema = new mongoose.Schema({
  commandeId: { type: mongoose.Schema.Types.ObjectId, ref: "Commande", required: true },
  trajetId: { type: mongoose.Schema.Types.ObjectId, ref: "Trajet", required: true },
  dockerId: { type: mongoose.Schema.Types.ObjectId, ref: "Docker" },
  statut: { type: String, default: "prévu" },
  dateEstimee: String
});

export const Livraison = mongoose.model("Livraison", livraisonSchema);
