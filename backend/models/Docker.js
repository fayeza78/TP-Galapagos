import mongoose from "mongoose";

const dockerSchema = new mongoose.Schema({
  name: String,
  disponible: { type: Boolean, default: true },
});

export const Docker = mongoose.model("Docker", dockerSchema);
