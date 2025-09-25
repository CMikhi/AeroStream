// We can ignore these problems since this is meant to fail if something is wrong
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import bcrypt from "bcrypt";

import { AuthService } from "./auth.service";
import { DbService } from "../db/db.service";
import { JwtService } from "../jwt/jwt.service";

import { User } from "../entities/user.entity";
import { loginUserDto } from "../dto/loginUser.dto";
import { CreateUserDto } from "../dto/CreateUser.dto";

describe("AuthService", () => {
  let authService: AuthService;
  let dbService: jest.Mocked<DbService>;
  let jwtService: jest.Mocked<JwtService>;

  beforeEach(() => {
    dbService = {
      findOne: jest.fn(),
      create: jest.fn(),
      SaveRefreshToken: jest.fn(),
    } as any;
    jwtService = {
      rotateTokens: jest.fn(),
      compareToken: jest.fn(),
      verifyToken: jest.fn(),
    } as any;

    authService = new AuthService(dbService, jwtService);
  });

  describe("login", () => {
    it("should return tokens for valid credentials", async () => {
      const user: User = {
        email: "test@test.com",
        password: "hashed",
        createdAt: new Date(),
        id: "1",
        role: "user",
        refreshTokenHash: "hash",
      } as User;
      dbService.findOne.mockResolvedValue(user);
      jest.spyOn(bcrypt, "compare").mockResolvedValue(true);
      jwtService.rotateTokens.mockResolvedValue({
        accessToken: "access-token",
        refreshToken: "refresh-token",
        refreshTokenHash: "new-hash",
      });
      const dto: loginUserDto = {
        email: "test@test.com",
        password: "pass",
      };
      const result = await authService.login(dto);
      expect(result).toEqual({
        message: "User logged in successfully",
        userID: "1",
        accessToken: "access-token",
        refreshToken: "refresh-token",
      });
    });

    it("should throw error for invalid credentials", async () => {
      dbService.findOne.mockResolvedValue(null);
      const dto: loginUserDto = {
        email: "notfound@test.com",
        password: "pass",
      };
      await expect(authService.login(dto)).rejects.toThrow(
        "Invalid credentials",
      );
    });
  });

  describe("register", () => {
    it("should register a new user", async () => {
      jest.spyOn(bcrypt, "hash").mockResolvedValue("hashed");
      jwtService.rotateTokens.mockResolvedValue({
        accessToken: "access-token",
        refreshToken: "refresh-token",
        refreshTokenHash: "new-hash",
      });
      dbService.create.mockResolvedValue({
        email: "new@test.com",
        password: "hashed",
        createdAt: new Date(),
        id: "2",
        role: "user",
        refreshTokenHash: "",
        firstName: "New",
        lastName: "User",
      });
      const dto: CreateUserDto = {
        email: "new@test.com",
        password: "pass",
        firstName: "New",
        lastName: "User",
        username: "newuser",
      };
      const result = await authService.register(dto);
      expect(result).toEqual({
        message: "User registered successfully",
        userID: "2",
        accessToken: "access-token",
        refreshToken: "refresh-token",
      });
    });
  });

  describe("refresh", () => {
    it("should refresh tokens for valid refresh token", async () => {
      const user: User = {
        id: "1",
        refreshTokenHash: "hash",
      } as User;
      dbService.findOne.mockResolvedValue(user);
      jwtService.compareToken.mockResolvedValue(true);
      jwtService.rotateTokens.mockResolvedValue({
        accessToken: "new-access-token",
        refreshToken: "new-refresh-token",
        refreshTokenHash: "new-hash",
      });
      const result = await authService.refresh("1", "refresh-token");
      expect(result).toEqual({
        message: "Token refreshed successfully",
        accessToken: "new-access-token",
        newRefreshToken: "new-refresh-token",
      });
    });
  });

  describe("getLoggedIn", () => {
    it("should return loggedIn true for valid token", async () => {
      jwtService.verifyToken.mockResolvedValue(true);
      const result = await authService.getLoggedIn("valid-token");
      expect(result).toEqual({ loggedIn: true });
    });

    it("should return loggedIn false for invalid token", async () => {
      jwtService.verifyToken.mockRejectedValue(new Error("Invalid token"));
      const result = await authService.getLoggedIn("invalid-token");
      expect(result).toEqual({ loggedIn: false });
    });
  });
});
