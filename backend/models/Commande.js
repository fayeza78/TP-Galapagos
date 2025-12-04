import mongoose from "mongoose";

const commandeSchema = new mongoose.Schema({
  clientId: { type: mongoose.Schema.Types.ObjectId, ref: "Client", required: true },
  products: [
    { 
      productId: { type: mongoose.Schema.Types.ObjectId, ref: "Produit", required: true },
      quantity: { type: Number, required: true, min: 1 }
    }
  ],
  statut: { type: String, enum: ["en attente", "en cours", "livrée"], default: "en attente" },
  dateCommande: { type: Date, default: Date.now },
});

export const Commande = mongoose.model("Commande", commandeSchema);
