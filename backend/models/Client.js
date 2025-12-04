import mongoose from "mongoose";

const clientSchema = new mongoose.Schema({
  name: String,
  type: String,
  email: String,
});

export const Client = mongoose.model("Client", clientSchema);
