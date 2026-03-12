export type PacketStoreState = {
  activePacketId: string | null;
};

export const packetStore: PacketStoreState = {
  activePacketId: null,
};
