import { Module, forwardRef } from "@nestjs/common";
import { RolesController } from "./roles.controller";
import { RolesService } from "./roles.service";
import { RolesGuard } from "./roles.guard";
import { DbModule } from "../db/db.module";
import { JwtModule } from "../jwt/jwt.module";
import { AuthModule } from "../auth/auth.module";

@Module({
  imports: [DbModule, JwtModule, forwardRef(() => AuthModule)],
  controllers: [RolesController],
  providers: [RolesService, RolesGuard],
  exports: [RolesService, RolesGuard],
})
export class RolesModule {}
