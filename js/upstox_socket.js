const config = require('./config');
const db = require('./mongo_db');
const WebSocket = require('ws').WebSocket;
const protobuf = require("protobufjs");
let protobufRoot = null;



const ws = new WebSocket(config['marketDataFeedWsUrl'], {
  headers: {
    "Api-Version": "2.0",
    "Authorization": "Bearer " + config['bearerAccessToken']
  },
  followRedirects: true
});

ws.on('open', function open() {
  console.log('connected');

  setTimeout(function timeout() {
    const data = {
      guid: "someguid",
      method: "sub",
      data: {
        mode: "full",
        instrumentKeys: ["NSE_INDEX|Nifty Bank"]
      }
    }
    ws.send(Buffer.from(JSON.stringify(data)))
  }, 1000);
});

ws.on('close', function close() {
  console.log('disconnected');
});
const prev = {"ts": 0}
ws.on('message', function message(data) {
    //console.log(data);
    const buff = Buffer.from(data);

    // buffer to JSON
    // using the toJSON() method
    const json = buff.toJSON();
    //console.log(json);

    // var d = parseBinary(e)
    // if(e.data instanceof ArrayBuffer) {
    //     // Trigger on message event when binary message is received
    //     trigger("message", [e.data]);
    //     if(e.data.byteLength > 2) {
    //         var d = parseBinary(e.data);
    //         if(d) trigger("ticks", [d]);
    //     }
    // } else {
    //     parseTextMessage(e.data)
    // }
    //console.log("=======================================================");
    const data1 = decodeProtobuf(data);
    //console.log(data1, " data1");
    var ohlc = data1['feeds']['NSE_INDEX|Nifty Bank']['ff']['indexFF']['marketOHLC']['ohlc'];
    //console.log(data1['feeds']['NSE_INDEX|Nifty Bank']['ff']['indexFF']['marketOHLC']['ohlc'][0]['ts'], " data1['feeds']['NSE_INDEX|Nifty Bank']");
    //console.log(JSON.stringify(ohlc));
    if(ohlc.length > 1) {
      var ohlc_1min = ohlc[1];
      for(let i = 0; i < ohlc.length; i++) {
        // console.log(JSON.stringify(ohlc[i]));
        // console.log("=======================================================");
      }
      //console.log(JSON.stringify(ohlc_1min), " ohlc_1min");
      const time = parseInt(ohlc_1min['ts']);
      
      var d = new Date(time);
      //console.log(d, " d");
      var hours = d.getHours();
      // Minutes
      var minutes = d.getMinutes();
      // Seconds
      var seconds = d.getSeconds();
      var date = d.getDate() + '/' + (d.getMonth()+1) + '/' + d.getFullYear()+' '+hours+':'+minutes+':'+seconds;
      // console.log(JSON.stringify(ohlc_1min));
      // console.log(date);

      //ISODate("2021-11-17T03:19:56.186Z")
      var s = new Date(time);

      if(time > prev['ts']) {
        prev['ts'] = time;
        s.setHours(s.getHours() + 5)
        s.setMinutes(s.getMinutes() + 30)
        ohlc_1min['ts'] = s;
        db(ohlc_1min)
      }
    }
    
    
    
    
});

async function initProtobuf() {
  protobufRoot = await protobuf.load(__dirname + "/MarketDataFeed.proto");
  console.log("Protobuf part initialization complete");
}

function decodeProtobuf(buffer) {
  if (protobufRoot == null) {
    console.warn("Protobuf part not initialized yet!");
    return null;
  }

  const FeedResponse = protobufRoot.lookupType("com.upstox.marketdatafeeder.rpc.proto.FeedResponse");
  return FeedResponse.decode(buffer);
}

initProtobuf();