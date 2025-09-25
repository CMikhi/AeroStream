import { Module, forwardRef } from "@nestjs/common";
import { AuthService } from "./auth.service";
import { AuthController } from "./auth.controller";
import { JwtAuthGuard } from "./jwt-auth.guard";
import { DbModule } from "../db/db.module";
import { JwtModule } from "../jwt/jwt.module";

@Module({
  imports: [
    DbModule,
    // Use forwardRef to handle potential circular dependencies
    forwardRef(() => JwtModule),
  ],
  controllers: [AuthController],
  providers: [AuthService, JwtAuthGuard],
  exports: [AuthService, JwtAuthGuard],
})
export class AuthModule {}
