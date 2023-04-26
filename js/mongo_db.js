const mongoose = require("mongoose");

mongoose.connect("mongodb://0.0.0.0:27017/upstox", {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const db = mongoose.connection;
db.on("error", console.error.bind(console, "connection error: "));
db.once("open", function () {
  console.log("Connected successfully");
});

const UserSchema = new mongoose.Schema({
    interval: {
      type: String,
      required: true,
    },
    open: {
      type: Number,
      default: 0,
    },
    high: {
        type: Number,
        default: 0,
      },
      low: {
        type: Number,
        default: 0,
      },
      close: {
        type: Number,
        default: 0,
      },
      ts: {
        type: Date,
        default: 0,
      },
  });
  
  const User = mongoose.model("NiftyBankTick", UserSchema);

  async function run(data) {
        console.log(data, "   data")
        const user = new User(data);
    
        try {
        await user.save();
        console.log("saved successfully");
        } catch (error) {
            console.log(error);
        }
  }

  module.exports = run;