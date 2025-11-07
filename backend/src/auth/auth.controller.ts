import {
  Body,
  Controller,
  Get,
  Patch,
  Post,
  UseGuards,
  Request,
} from "@nestjs/common";

import { AuthService } from "./auth.service";

import { BodyRequiredGuard } from "./body-required.guard";
import { JwtAuthGuard } from "./jwt-auth.guard";
import { RefreshUserTokensDto } from "../dto/refreshUserTokens.dto";
import { CreateUserDto } from "../dto/CreateUser.dto";
import { loginUserDto } from "../dto/loginUser.dto";

interface AuthenticatedRequest {
  user: {
    id: string;
    role: string;
    roles: string[];
    username: string;
  };
}

@Controller()
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  /**
   * Root endpoint for API health check
   */
  @Get()
  getRoot() {
    return {
      message: "Ignite Chat API",
      status: "healthy",
      version: "1.0.0",
    };
  }

  /**
   * Handles user login authentication
   * @param loginUserDto - The login credentials containing username and password
   * @returns Promise resolving to authentication result with user data and token on success,
   *          or error response with status 400 if credentials are missing/invalid
   *
   * @example
   * ```
   * POST /login
   * {
   *   "username": "cam",
   *   "password": "123456"
   * }
   * ```
   */
  @Post("login")
  @UseGuards(BodyRequiredGuard) // Checks input before hitting route
  async login(@Body() loginUserDto: loginUserDto) {
    const result = await this.authService.login(loginUserDto);
    return {
      access_token: result.accessToken,
      refresh_token: result.refreshToken,
      token_type: "bearer",
      user_id: result.userID,
      message: result.message,
    };
  }

  @Post("register")
  @UseGuards(BodyRequiredGuard) // Checks input before hitting route
  async register(@Body() createUserDto: CreateUserDto) {
    const user = await this.authService.register(createUserDto);
    return {
      message: "User created successfully",
      status: 201,
      access_token: user.accessToken,
      refresh_token: user.refreshToken,
      token_type: "bearer",
      user_id: user.userID,
    };
  }

  @Patch("auth/refresh")
  @UseGuards(BodyRequiredGuard)
  async refresh(@Body() refreshTokenDto: RefreshUserTokensDto) {
    // eslint-disable-next-line prettier/prettier
    const result = await this.authService.refresh(refreshTokenDto.refresh_token);
    return {
      access_token: result.accessToken,
      refresh_token: result.newRefreshToken,
      token_type: "bearer",
      message: result.message,
    };
  }

  /**
   * Get current user information - requires authorization header with
   * valid JWT bearer token
   * @returns status 200 on success with user data
   * @throws UnauthorizedException if no valid JWT token is provided
   * @throws ForbiddenException if user does not have access (Should not happen)
   */
  @Get("auth/me")
  @UseGuards(JwtAuthGuard)
  getCurrentUser(@Request() req: AuthenticatedRequest) {
    return {
      message: "User info retrieved successfully",
      status: 200,
      data: {
        id: req.user.id,
        username: req.user.username,
        role: req.user.role,
      },
    };
  }
}
