import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { MessagesService } from "./messages.service";
import { MessagesController } from "./messages.controller";
import { Message } from "../entities/message.entity";
import { Room } from "../entities/room.entity";
import { User } from "../entities/user.entity";
import { DbModule } from "../db/db.module";
import { JwtModule } from "../jwt/jwt.module";

@Module({
  imports: [
    TypeOrmModule.forFeature([Message, Room, User]),
    DbModule,
    JwtModule,
  ],
  controllers: [MessagesController],
  providers: [MessagesService],
  exports: [MessagesService],
})
export class MessagesModule {}