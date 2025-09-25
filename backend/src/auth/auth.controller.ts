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
import { JwtService } from "../jwt/jwt.service";

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
  constructor(
    private readonly authService: AuthService,
    private readonly jwtService: JwtService,
  ) {}

  /**
   * Root endpoint for API health check
   */
  @Get()
  getRoot() {
    return {
      message: "Ignite Chat API",
      status: "ok",
      version: "1.0.0",
    };
  }

  /**
   * Test endpoint
   */
  @Get("test")
  getTest() {
    return {
      message: "Test endpoint working",
      status: "ok",
    };
  }

  /**
   * Handles user login authentication
   *
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
      token_type: "bearer",
      user_id: user.userID,
    };
  }

  @Patch("auth/refresh")
  refresh(@Body() refreshTokenDto: RefreshUserTokensDto) {
    return this.authService.refresh(
      refreshTokenDto.userID,
      refreshTokenDto.refreshToken,
    );
  }

  @Get("auth/loggedIn")
  loggedIn(@Body("accessToken") accessToken: string) {
    return this.authService.getLoggedIn(accessToken);
  }

  /**
   * Get current user information - requires authentication
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
