/* eslint-disable prettier/prettier */
import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import { JwtService } from "../jwt/jwt.service";
import { DbService } from "../db/db.service";

interface RequestWithUser {
  headers: {
    authorization?: string;
  };
  user?: {
    id: string;
    username: string;
    role: string;
    roles: string[];
  };
}

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    private readonly jwtService: JwtService,
    private readonly dbService: DbService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<RequestWithUser>();
    const authorization = request.headers.authorization;

    if (!authorization || typeof authorization !== 'string') {
      throw new UnauthorizedException("Authorization header is missing");
    }

    const [bearer, token] = authorization.split(" ");
    if (bearer !== "Bearer" || !token) {
      throw new UnauthorizedException("Invalid authorization format");
    }

    try {
      // Verify the token
      const isValid = await this.jwtService.verifyToken(token);
      if (!isValid) {
        throw new UnauthorizedException("Invalid token");
      }

      // Decode the token to get user info
      const payload = this.jwtService.decodeToken(token);
      if (!payload || !payload.sub) {
        throw new UnauthorizedException("Invalid token payload");
      }

      // Get user from database to ensure they still exist and get current role
      const user = await this.dbService.findOne(payload.sub);
      if (!user) {
        throw new UnauthorizedException("User not found");
      }

      // Attach user info to request, including roles array for compatibility with RolesGuard
      request.user = {
        id: user.id!,
        username: user.username,
        role: user.role,
        roles: [user.role], // Convert single role to array for RolesGuard compatibility
      };

      return true;
    } catch {
      throw new UnauthorizedException("Token validation failed");
    }
  }
}