import {
  Body,
  Controller,
  Get,
  Post,
  UseGuards,
  Request,
} from "@nestjs/common";
import { RoomsService } from "./rooms.service";
import { CreateRoomDto } from "../dto/create-room.dto";
import { JoinRoomDto } from "../dto/join-room.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { BodyRequiredGuard } from "../auth/body-required.guard";

interface AuthenticatedRequest {
  user: {
    id: string;
    email: string;
    username: string;
    role: string;
  };
}

@Controller()
export class RoomsController {
  constructor(private readonly roomsService: RoomsService) {}

  @Post("create_room")
  @UseGuards(JwtAuthGuard, BodyRequiredGuard)
  async createRoom(
    @Body() createRoomDto: CreateRoomDto,
    @Request() req: AuthenticatedRequest,
  ) {
    const room = await this.roomsService.createRoom(createRoomDto, req.user.id);
    return {
      message: `Room '${createRoomDto.room_name}' created successfully`,
      room_id: room.id,
      room_name: room.name,
    };
  }

  @Post("join_room")
  @UseGuards(JwtAuthGuard, BodyRequiredGuard)
  async joinRoom(
    @Body() joinRoomDto: JoinRoomDto,
    @Request() req: AuthenticatedRequest,
  ) {
    const result = await this.roomsService.joinRoom(joinRoomDto, req.user.id);
    return {
      message: result.message,
      room_id: result.room.id,
      room_name: result.room.name,
    };
  }

  @Get("rooms")
  @UseGuards(JwtAuthGuard)
  async getRooms(@Request() req: AuthenticatedRequest) {
    const rooms = await this.roomsService.getRooms(req.user.id);
    return {
      message: "Rooms retrieved successfully",
      count: rooms.length,
      rooms: rooms.map((room) => ({
        id: room.id,
        name: room.name,
        private: room.private,
        created_at: room.createdAt,
        user_count: room.users ? room.users.length : 0,
      })),
    };
  }
}
