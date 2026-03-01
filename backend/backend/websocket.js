import { WebSocketServer } from "ws";

export default function setupWS(server) {
  const wss = new WebSocketServer({ server });

  wss.on("connection", ws => {
    ws.send(JSON.stringify({ message: "Connected" }));

    setInterval(() => {
      ws.send(
        JSON.stringify({
          type: "heartbeat",
          time: Date.now()
        })
      );
    }, 5000);
  });
}
