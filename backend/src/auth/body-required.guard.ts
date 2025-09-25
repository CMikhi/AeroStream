import {
  Injectable,
  CanActivate,
  ExecutionContext,
  BadRequestException,
} from "@nestjs/common";
import { Request } from "express";
import { CreateUserDto } from "src/dto/CreateUser.dto";
import { loginUserDto } from "src/dto/loginUser.dto";

@Injectable()
export class BodyRequiredGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const req = context.switchToHttp().getRequest<Request>();
    const body: unknown = req.body;

    // Type guard for a non-empty plain object
    const isNonEmptyPlainObject = (
      value: unknown,
    ): value is Record<string, unknown> =>
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value) &&
      Object.keys(value).length > 0;

    if (!isNonEmptyPlainObject(body)) {
      throw new BadRequestException("Request body is required");
    }

    // Safely derive route path if present (express adds `route` only after matching)
    // Helper to safely extract route path without using `any`
    const getRoutePath = (r: Request): string | undefined => {
      const maybeRoute: unknown = (r as unknown as { route?: unknown }).route;
      if (
        typeof maybeRoute === "object" &&
        maybeRoute !== null &&
        "path" in maybeRoute &&
        typeof (maybeRoute as { path?: unknown }).path === "string"
      ) {
        return (maybeRoute as { path: string }).path;
      }
      return undefined;
    };
    const routePath = getRoutePath(req);

    // Type guards for DTOs
    const isLoginDto = (v: unknown): v is loginUserDto =>
      typeof v === "object" &&
      v !== null &&
      "username" in v &&
      typeof (v as { username?: unknown }).username === "string" &&
      "password" in v &&
      typeof (v as { password?: unknown }).password === "string";
    const isCreateUserDto = (v: unknown): v is CreateUserDto =>
      typeof v === "object" &&
      v !== null &&
      "username" in v &&
      typeof (v as { username?: unknown }).username === "string" &&
      "password" in v &&
      typeof (v as { password?: unknown }).password === "string";

    if (routePath?.includes("login")) {
      if (!isLoginDto(body)) {
        throw new BadRequestException("username and password are required");
      }
      if (!body.username || !body.password) {
        throw new BadRequestException("username and password are required");
      }
    } else if (routePath?.includes("register")) {
      if (!isCreateUserDto(body)) {
        throw new BadRequestException("username and password are required");
      }
      if (!body.username || !body.password) {
        throw new BadRequestException("username and password are required");
      }
    }

    return true;
  }
}
