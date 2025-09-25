import { Module } from "@nestjs/common";
import { JwtModule as NestJwtModule } from "@nestjs/jwt";
import { ConfigModule, ConfigService } from "@nestjs/config";
import { JwtService } from "./jwt.service";

@Module({
  imports: [
    ConfigModule.forRoot({
      envFilePath: ".env",
    }),
    NestJwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => {
        const secret = configService.get<string>("JWT_SECRET");
        if (!secret) {
          throw new Error(
            "JWT_SECRET is not defined in the environment variables",
          );
        }

        return {
          secret, // Use the symmetric secret key
          signOptions: {
            algorithm: "HS256", // Switch to HS256
            expiresIn: configService.get<string>("JWT_ACCESS_EXP", "15m"),
          },
        };
      },
    }),
  ],
  providers: [JwtService],
  exports: [JwtService],
})
export class JwtModule {}
