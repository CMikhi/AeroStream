import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { User } from "../entities/user.entity";
import { DbService } from "./db.service";

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  providers: [DbService],
  exports: [DbService],
})
export class DbModule {}
