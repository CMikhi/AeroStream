import {
  Injectable,
  NotFoundException,
  UnauthorizedException,
} from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Message } from "../entities/message.entity";
import { Room } from "../entities/room.entity";
import { User } from "../entities/user.entity";
import { SendMessageDto } from "../dto/send-message.dto";

@Injectable()
export class MessagesService {
  constructor(
    @InjectRepository(Message)
    private messageRepository: Repository<Message>,
    @InjectRepository(Room)
    private roomRepository: Repository<Room>,
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async sendMessage(
    sendMessageDto: SendMessageDto,
    userId: string,
  ): Promise<Message> {
    // Find the room
    const room = await this.roomRepository.findOne({
      where: { name: sendMessageDto.room_name },
      relations: ["users"],
    });

    if (!room) {
      throw new NotFoundException(
        `Room '${sendMessageDto.room_name}' not found`,
      );
    }

    // Get the user
    const user = await this.userRepository.findOne({
      where: { id: userId },
    });

    if (!user) {
      throw new UnauthorizedException("User not found");
    }

    // Check if user is in the room
    const isUserInRoom = room.users.some((u) => u.id === userId);
    if (!isUserInRoom) {
      throw new UnauthorizedException("User is not a member of this room");
    }

    // Create and save the message
    const message = this.messageRepository.create({
      content: sendMessageDto.message,
      timestamp: new Date(),
      user,
      userId,
      room,
      roomId: room.id!,
      username: user.username,
    });

    return await this.messageRepository.save(message);
  }

  async getMessages(roomName: string, limit?: number): Promise<Message[]> {
    // Find the room first to validate it exists
    const room = await this.roomRepository.findOne({
      where: { name: roomName },
    });

    if (!room) {
      throw new NotFoundException(`Room '${roomName}' not found`);
    }

    const queryBuilder = this.messageRepository
      .createQueryBuilder("message")
      .leftJoinAndSelect("message.user", "user")
      .where("message.roomId = :roomId", { roomId: room.id })
      .orderBy("message.timestamp", "ASC");

    if (limit) {
      queryBuilder.limit(limit);
    }

    return await queryBuilder.getMany();
  }

  async getMessageCount(roomId: string): Promise<number> {
    // Validate room exists
    const room = await this.roomRepository.findOne({
      where: { id: roomId },
    });

    if (!room) {
      throw new NotFoundException(`Room not found`);
    }

    return await this.messageRepository.count({
      where: { roomId },
    });
  }

  async validateUserInRoom(userId: string, roomName: string): Promise<boolean> {
    const room = await this.roomRepository.findOne({
      where: { name: roomName },
      relations: ["users"],
    });

    if (!room) {
      return false;
    }

    return room.users.some((user) => user.id === userId);
  }
}
