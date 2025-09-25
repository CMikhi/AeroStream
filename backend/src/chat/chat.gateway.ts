import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayConnection,
  OnGatewayDisconnect,
  ConnectedSocket,
  MessageBody,
} from "@nestjs/websockets";
import { Server, Socket } from "socket.io";
import { Injectable, Logger } from "@nestjs/common";
import { JwtService } from "../jwt/jwt.service";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { User } from "../entities/user.entity";
import { Room } from "../entities/room.entity";
import { Message } from "../entities/message.entity";

interface AuthenticatedSocket extends Socket {
  user?: User;
  roomName?: string;
}

interface ClientToServerEvents {
  auth: (data: { token: string }) => void;
  send_message: (data: { message: string }) => void;
  ping: () => void;
}

interface ServerToClientEvents {
  auth_success: (data: { user: User; room: string }) => void;
  message_history: (data: { data: Message[] }) => void;
  new_message: (data: { data: Message }) => void;
  message_sent: (data: { data: Message }) => void;
  user_joined: (data: { message: string }) => void;
  user_left: (data: { message: string }) => void;
  connection_replaced: (data: { message: string }) => void;
  force_disconnect: (data: { message: string }) => void;
  error: (data: { message: string }) => void;
  pong: () => void;
}

@Injectable()
@WebSocketGateway({
  namespace: /^\/ws\/(.+)$/,
  cors: {
    origin: true,
    credentials: true,
  },
})
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server<ClientToServerEvents, ServerToClientEvents>;

  private readonly logger = new Logger(ChatGateway.name);
  private connectedUsers = new Map<string, AuthenticatedSocket>(); // username -> socket
  private roomConnections = new Map<string, Set<string>>(); // roomName -> Set of usernames

  constructor(
    private jwtService: JwtService,
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(Room)
    private roomRepository: Repository<Room>,
    @InjectRepository(Message)
    private messageRepository: Repository<Message>,
  ) {}

  async handleConnection(client: AuthenticatedSocket) {
    this.logger.log(`Client connected: ${client.id}`);
    
    // Extract room name from namespace
    const roomName = client.nsp.name.replace("/ws/", "");
    client.roomName = roomName;

    this.logger.log(`Client ${client.id} attempting to connect to room: ${roomName}`);
  }

  async handleDisconnect(client: AuthenticatedSocket) {
    this.logger.log(`Client disconnected: ${client.id}`);
    
    if (client.user && client.roomName) {
      const username = client.user.username;
      const roomName = client.roomName;

      // Remove from connected users
      this.connectedUsers.delete(username);

      // Remove from room connections
      const roomUsers = this.roomConnections.get(roomName);
      if (roomUsers) {
        roomUsers.delete(username);
        if (roomUsers.size === 0) {
          this.roomConnections.delete(roomName);
        }
      }

      // Notify other users in the room
      client.to(roomName).emit("user_left", {
        message: `${username} left the room`,
      });

      this.logger.log(`User ${username} left room ${roomName}`);
    }
  }

  @SubscribeMessage("auth")
  async handleAuth(
    @ConnectedSocket() client: AuthenticatedSocket,
    @MessageBody() data: { token: string },
  ) {
    try {
      if (!data.token) {
        client.emit("error", { message: "Token is required" });
        client.disconnect();
        return;
      }

      // Verify JWT token
      const isValid = await this.jwtService.verifyToken(data.token);
      if (!isValid) {
        client.emit("error", { message: "Invalid token" });
        client.disconnect();
        return;
      }

      // Decode the token
      const decoded = this.jwtService.decodeToken(data.token);
      const userId = decoded?.sub;

      if (!userId) {
        client.emit("error", { message: "Invalid token" });
        client.disconnect();
        return;
      }

      // Get user from database
      const user = await this.userRepository.findOne({
        where: { id: userId },
      });

      if (!user) {
        client.emit("error", { message: "User not found" });
        client.disconnect();
        return;
      }

      const roomName = client.roomName!;

      // Validate that user has access to the room
      const room = await this.roomRepository.findOne({
        where: { name: roomName },
        relations: ["users"],
      });

      if (!room) {
        client.emit("error", { message: "Room not found" });
        client.disconnect();
        return;
      }

      const isUserInRoom = room.users.some((u) => u.id === userId);
      if (!isUserInRoom) {
        client.emit("error", { message: "User is not a member of this room" });
        client.disconnect();
        return;
      }

      // Check if user is already connected in this room
      const existingConnection = this.connectedUsers.get(user.username);
      if (existingConnection) {
        // Disconnect existing connection
        existingConnection.emit("connection_replaced", {
          message: "Your connection was replaced by a new one",
        });
        existingConnection.disconnect();
      }

      // Set authenticated user
      client.user = user;
      this.connectedUsers.set(user.username, client);

      // Add to room connections
      if (!this.roomConnections.has(roomName)) {
        this.roomConnections.set(roomName, new Set());
      }
      this.roomConnections.get(roomName)!.add(user.username);

      // Join the socket room
      await client.join(roomName);

      // Send authentication success
      client.emit("auth_success", {
        user,
        room: roomName,
      });

      // Send message history
      const messages = await this.messageRepository.find({
        where: { roomId: room.id },
        relations: ["user"],
        order: { timestamp: "ASC" },
        take: 50, // Last 50 messages
      });

      client.emit("message_history", { data: messages });

      // Notify other users
      client.to(roomName).emit("user_joined", {
        message: `${user.username} joined the room`,
      });

      this.logger.log(`User ${user.username} authenticated for room ${roomName}`);
    } catch (error) {
      this.logger.error("Authentication failed:", error);
      client.emit("error", { message: "Authentication failed" });
      client.disconnect();
    }
  }

  @SubscribeMessage("send_message")
  async handleSendMessage(
    @ConnectedSocket() client: AuthenticatedSocket,
    @MessageBody() data: { message: string },
  ) {
    try {
      if (!client.user || !client.roomName) {
        client.emit("error", { message: "Not authenticated" });
        return;
      }

      if (!data.message || data.message.trim().length === 0) {
        client.emit("error", { message: "Message content is required" });
        return;
      }

      const roomName = client.roomName;
      const user = client.user;

      // Get room
      const room = await this.roomRepository.findOne({
        where: { name: roomName },
      });

      if (!room) {
        client.emit("error", { message: "Room not found" });
        return;
      }

      // Create and save message
      const message = this.messageRepository.create({
        content: data.message.trim(),
        timestamp: new Date(),
        user,
        userId: user.id!,
        room,
        roomId: room.id!,
        username: user.username,
      });

      const savedMessage = await this.messageRepository.save(message);

      // Send confirmation to sender
      client.emit("message_sent", { data: savedMessage });

      // Broadcast to other users in the room
      client.to(roomName).emit("new_message", { data: savedMessage });

      this.logger.log(`Message sent by ${user.username} in room ${roomName}`);
    } catch (error) {
      this.logger.error("Error sending message:", error);
      client.emit("error", { message: "Failed to send message" });
    }
  }

  @SubscribeMessage("ping")
  handlePing(@ConnectedSocket() client: AuthenticatedSocket) {
    client.emit("pong");
  }

  // Helper methods
  getUsersInRoom(roomName: string): string[] {
    const roomUsers = this.roomConnections.get(roomName);
    return roomUsers ? Array.from(roomUsers) : [];
  }

  isUserConnected(username: string): boolean {
    return this.connectedUsers.has(username);
  }
}