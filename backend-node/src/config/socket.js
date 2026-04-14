let io;

export function setIO(socketIOInstance) {
  io = socketIOInstance;
}

export function getIO() {
  if (!io) {
    throw new Error("Socket.io has not been initialized yet.");
  }
  return io;
}
