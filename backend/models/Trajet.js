import mongoose from "mongoose";

const trajetSchema = new mongoose.Schema({
  hydravionId: String,              
  depart: String,                   
  arrivee: String,                  
  distanceKm: Number,               
  dureeMinutes: Number,
});

export const Trajet = mongoose.model("Trajet", trajetSchema);