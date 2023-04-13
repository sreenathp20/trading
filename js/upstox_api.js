var Upstox = require("upstox");
const config = require('./config');

var upstox = new Upstox("a33d9f29-4518-4b91-8a0f-2dc149061507");

//console.log(upstox, " upstox");

var loginUrl = upstox.getLoginUri('http://127.0.0.1');
var accessToken = config['bearerAccessToken'];

upstox.setToken(accessToken);
console.log(upstox, " upstox");
upstox.connectSocket()
        .then(function(){
            // Socket Connection successfull
            // Now you can setup listeners
            upstox.on("open", function(message) {
                console.log(message)
                //message for order updates
            });
            upstox.on("orderUpdate", function(message) {
                //message for order updates
            });
            upstox.on("positionUpdate", function(message) {
                //message for position conversion
            });
            upstox.on("tradeUpdate", function(message) {
                //message for trade updates
            });
            upstox.on("liveFeed", function(message) {
                console.log(message)
                //message for live feed
            });
            upstox.on("disconnected", function(message) {
                //listener after socket connection is disconnected
            });
            upstox.on("error", function(error) {
                //error listener
            });
            //You can call upstox.closeSocket() to disconnect
        }).catch(function(err) {
            // Something went wrong.
        })

        upstox.getProfile()
      .then(function (response) {
          console.log(response);
      })
      .catch(function(error){
          console.log("Error", error);
      });

//upstox.connectSocket()