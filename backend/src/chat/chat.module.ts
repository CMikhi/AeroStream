import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { ChatGateway } from "./chat.gateway";
import { User } from "../entities/user.entity";
import { Room } from "../entities/room.entity";
import { Message } from "../entities/message.entity";
import { JwtModule } from "../jwt/jwt.module";

@Module({
  imports: [
    TypeOrmModule.forFeature([User, Room, Message]),
    JwtModule,
  ],
  providers: [ChatGateway],
  exports: [ChatGateway],
})
export class ChatModule {}