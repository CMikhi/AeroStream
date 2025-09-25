import {
  Body,
  Controller,
  Get,
  Post,
  Param,
  Query,
  UseGuards,
  Request,
} from "@nestjs/common";
import { MessagesService } from "./messages.service";
import { SendMessageDto } from "../dto/send-message.dto";
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
export class MessagesController {
  constructor(private readonly messagesService: MessagesService) {}

  @Post("send_message")
  @UseGuards(JwtAuthGuard, BodyRequiredGuard)
  async sendMessage(
    @Body() sendMessageDto: SendMessageDto,
    @Request() req: AuthenticatedRequest,
  ) {
    const message = await this.messagesService.sendMessage(
      sendMessageDto,
      req.user.id,
    );
    return {
      message: "Message sent successfully",
      id: message.id,
      content: message.content,
      timestamp: message.timestamp,
      username: message.username,
      room_name: sendMessageDto.room_name,
    };
  }

  @Get("messages/:room_name")
  @UseGuards(JwtAuthGuard)
  async getMessages(
    @Param("room_name") roomName: string,
    @Request() req: AuthenticatedRequest,
    @Query("limit") limit?: string,
  ) {
    // Validate user has access to the room
    const hasAccess = await this.messagesService.validateUserInRoom(
      req.user.id,
      roomName,
    );

    if (!hasAccess) {
      return {
        message: "Access denied to room",
        status: 403,
      };
    }

    const messages = await this.messagesService.getMessages(
      roomName,
      limit ? parseInt(limit, 10) : undefined,
    );

    return {
      message: "Messages retrieved successfully",
      count: messages.length,
      data: messages.map((msg) => ({
        id: msg.id,
        content: msg.content,
        username: msg.username,
        timestamp: msg.timestamp,
      })),
    };
  }

  @Get("messages/count/:room_id")
  @UseGuards(JwtAuthGuard)
  async getMessageCount(@Param("room_id") roomId: string) {
    const count = await this.messagesService.getMessageCount(roomId);
    return {
      message: "Message count retrieved successfully",
      room_id: roomId,
      count,
    };
  }
}