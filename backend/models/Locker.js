import mongoose from "mongoose";

const lockerSchema = new mongoose.Schema({
  location: String,
  capacity: Number,
  isAvailable: { type: Boolean, default: true },
});

export const Locker = mongoose.model("Locker", lockerSchema);