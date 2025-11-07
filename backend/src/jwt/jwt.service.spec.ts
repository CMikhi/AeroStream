import { JwtService } from "./jwt.service";
import { ConfigService } from "@nestjs/config";
import { JwtService as NestJwtService } from "@nestjs/jwt";

jest.mock("@nestjs/jwt");
jest.mock("@nestjs/config");

describe("JwtService", () => {
  let service: JwtService;
  let mockJwtService: NestJwtService;
  let mockConfigService: ConfigService;

  beforeEach(() => {
    mockJwtService = new NestJwtService();
    mockConfigService = new ConfigService();
    service = new JwtService(mockJwtService, mockConfigService);

    jest.spyOn(mockConfigService, "get").mockImplementation((key: string) => {
      if (key === "JWT_PRIVATE_KEY") return "test-private-key";
      if (key === "JWT_PUBLIC_KEY") return "test-public-key";
      if (key === "JWT_ACCESS_EXP") return "15m";
      if (key === "JWT_REFRESH_EXP") return "7d";
      return null;
    });
  });

  it("generateAccessToken produces a 3-part token", async () => {
    jest
      .spyOn(mockJwtService, "signAsync")
      .mockResolvedValue("header.payload.signature");
    const token = await service.generateAccessToken({
      sub: "user1",
      role: "user",
    });
    expect(typeof token).toBe("string");
    expect(token.split(".")).toHaveLength(3);
  });

  it("verifyToken returns true for a valid token", async () => {
    jest.spyOn(mockJwtService, "verifyAsync").mockResolvedValue({
      sub: "user-123",
      role: "user",
    });
    const isValid = await service.verifyToken("valid.token");
    expect(isValid).toBe(true);
  });

  it("verifyToken returns false for an invalid token", async () => {
    jest
      .spyOn(mockJwtService, "verifyAsync")
      .mockRejectedValue(new Error("Invalid token"));
    const isValid = await service.verifyToken("invalid.token");
    expect(isValid).toBe(false);
  });

  it("decodeToken extracts payload without validation", () => {
    jest.spyOn(mockJwtService, "decode").mockReturnValue({
      sub: "user-123",
      role: "user",
    });
    const payload = service.decodeToken("header.payload.signature");
    expect(payload).toHaveProperty("sub", "user-123");
    expect(payload).toHaveProperty("role", "user");
  });

  it("rotateTokens generates access and refresh tokens", async () => {
    jest
      .spyOn(service, "generateAccessToken")
      .mockResolvedValue("access.token");
    jest
      .spyOn(service, "generateRefreshToken")
      .mockResolvedValue("refresh.token");
    jest.spyOn(service, "hashToken").mockResolvedValue("hashed.refresh.token");

    const tokens = await service.rotateTokens("user-123", "user");
    expect(tokens).toHaveProperty("accessToken", "access.token");
    expect(tokens).toHaveProperty("refreshToken", "refresh.token");
    expect(tokens).toHaveProperty("refreshTokenHash", "hashed.refresh.token");
  });
});
