import { RolesModule } from "./roles/roles.module";
import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { UsersModule } from "./users/users.module";
import { RoomsModule } from "./rooms/rooms.module";
import { MessagesModule } from "./messages/messages.module";
import { ChatModule } from "./chat/chat.module";
import { User } from "./entities/user.entity";
import { Room } from "./entities/room.entity";
import { Message } from "./entities/message.entity";
import { AuthModule } from "./auth/auth.module";
import { JwtModule } from "./jwt/jwt.module";
import { DbModule } from "./db/db.module";
import { ConfigModule } from "@nestjs/config";

/** DO NOT DELETE
 * app.module is the master module that imports all other modules
 * Deleting app.module means that no other modules would be runnable
 *
 */
@Module({
  imports: [
    RolesModule,
    TypeOrmModule.forRoot({
      type: "sqlite",
      database: "../database.db", // Use repo root database for compatibility
      entities: [User, Room, Message],
      synchronize: true,
    }),
    ConfigModule.forRoot({
      isGlobal: true,
      // Allow dynamic resolution: prefer process.env already injected by Docker, fallback to file
      envFilePath: [
        process.env.NODE_ENV ? `./src/.env.${process.env.NODE_ENV}` : "",
        "./src/.env",
      ].filter(Boolean),
    }),
    UsersModule,
    RoomsModule,
    MessagesModule,
    ChatModule,
    AuthModule,
    JwtModule,
    DbModule,
  ],
})
export class AppModule {}
