import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { RoomsService } from "./rooms.service";
import { RoomsController } from "./rooms.controller";
import { Room } from "../entities/room.entity";
import { User } from "../entities/user.entity";
import { DbModule } from "../db/db.module";
import { JwtModule } from "../jwt/jwt.module";

@Module({
  imports: [TypeOrmModule.forFeature([Room, User]), DbModule, JwtModule],
  controllers: [RoomsController],
  providers: [RoomsService],
  exports: [RoomsService],
})
export class RoomsModule {}
