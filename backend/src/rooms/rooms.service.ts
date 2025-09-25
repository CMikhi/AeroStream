import { Injectable, NotFoundException, ConflictException, UnauthorizedException, BadRequestException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Room } from "../entities/room.entity";
import { User } from "../entities/user.entity";
import { CreateRoomDto } from "../dto/create-room.dto";
import { JoinRoomDto } from "../dto/join-room.dto";
import * as bcrypt from "bcrypt";

@Injectable()
export class RoomsService {
  constructor(
    @InjectRepository(Room)
    private roomRepository: Repository<Room>,
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async createRoom(createRoomDto: CreateRoomDto, userId: string): Promise<Room> {
    // Check if room with same name already exists
    const existingRoom = await this.roomRepository.findOne({
      where: { name: createRoomDto.room_name }
    });

    if (existingRoom) {
      throw new ConflictException(`Room '${createRoomDto.room_name}' already exists`);
    }

    // Get the user creating the room
    const user = await this.userRepository.findOne({
      where: { id: userId }
    });

    if (!user) {
      throw new UnauthorizedException("User not found");
    }

    let hashedPassword: string | undefined;
    if (createRoomDto.password && createRoomDto.private) {
      hashedPassword = await bcrypt.hash(createRoomDto.password, 12);
    }

    // Create the room
    const room = this.roomRepository.create({
      name: createRoomDto.room_name,
      private: createRoomDto.private || false,
      password: hashedPassword,
      createdAt: new Date(),
      createdBy: userId,
      users: [user], // Creator automatically joins the room
    });

    return await this.roomRepository.save(room);
  }

  async joinRoom(joinRoomDto: JoinRoomDto, userId: string): Promise<{ message: string; room: Room }> {
    // Find the room
    const room = await this.roomRepository.findOne({
      where: { name: joinRoomDto.room_name },
      relations: ['users']
    });

    if (!room) {
      throw new NotFoundException(`Room '${joinRoomDto.room_name}' not found`);
    }

    // Get the user
    const user = await this.userRepository.findOne({
      where: { id: userId }
    });

    if (!user) {
      throw new UnauthorizedException("User not found");
    }

    // Check if user is already in the room
    const isUserInRoom = room.users.some(u => u.id === userId);
    if (isUserInRoom) {
      return { message: `Already joined room '${joinRoomDto.room_name}'`, room };
    }

    // Check if room is private and password is required
    if (room.private && room.password) {
      if (!joinRoomDto.password) {
        throw new BadRequestException("Password required for private room");
      }

      const isPasswordValid = await bcrypt.compare(joinRoomDto.password, room.password);
      if (!isPasswordValid) {
        throw new UnauthorizedException("Invalid room password");
      }
    }

    // Add user to room
    room.users.push(user);
    await this.roomRepository.save(room);

    return { message: `Successfully joined room '${joinRoomDto.room_name}'`, room };
  }

  async getRooms(userId: string): Promise<Room[]> {
    // Get all public rooms and private rooms the user has joined
    const publicRooms = await this.roomRepository.find({
      where: { private: false },
      relations: ['users']
    });

    const userRooms = await this.roomRepository
      .createQueryBuilder('room')
      .leftJoinAndSelect('room.users', 'user')
      .where('user.id = :userId', { userId })
      .andWhere('room.private = :private', { private: true })
      .getMany();

    // Combine and deduplicate
    const allRooms = [...publicRooms, ...userRooms];
    const uniqueRooms = allRooms.filter((room, index, self) => 
      index === self.findIndex(r => r.id === room.id)
    );

    return uniqueRooms;
  }

  async getRoomByName(roomName: string): Promise<Room | null> {
    return await this.roomRepository.findOne({
      where: { name: roomName },
      relations: ['users', 'messages']
    });
  }

  async isUserInRoom(userId: string, roomName: string): Promise<boolean> {
    const room = await this.roomRepository.findOne({
      where: { name: roomName },
      relations: ['users']
    });

    if (!room) {
      return false;
    }

    return room.users.some(user => user.id === userId);
  }
}