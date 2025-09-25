import { JwtAuthGuard } from "./jwt-auth.guard";
import { JwtService } from "../jwt/jwt.service";
import { DbService } from "../db/db.service";
import { UnauthorizedException } from "@nestjs/common";

const mockContext = (authHeader?: string) => {
  const req: any = { headers: {} as Record<string, string> };
  if (authHeader) req.headers.authorization = authHeader;
  return {
    switchToHttp: () => ({ getRequest: () => req }),
  } as any;
};

describe("JwtAuthGuard", () => {
  let jwt: jest.Mocked<JwtService>;
  let db: jest.Mocked<DbService>;
  let guard: JwtAuthGuard;

  beforeEach(() => {
    jwt = {
      verifyToken: jest.fn(),
      decodeToken: jest.fn(),
    } as any;
    db = {
      findOne: jest.fn(),
    } as any;
    guard = new JwtAuthGuard(jwt, db);
  });

  it("throws if header missing", async () => {
    await expect(guard.canActivate(mockContext())).rejects.toThrow(
      UnauthorizedException,
    );
  });

  it("throws on invalid format", async () => {
    await expect(guard.canActivate(mockContext("Bad token"))).rejects.toThrow(
      UnauthorizedException,
    );
  });

  it("throws on invalid token", async () => {
    jwt.verifyToken.mockResolvedValue(false);
    await expect(guard.canActivate(mockContext("Bearer abc"))).rejects.toThrow(
      UnauthorizedException,
    );
  });

  it("throws when payload invalid", async () => {
    jwt.verifyToken.mockResolvedValue(true);
    jwt.decodeToken.mockReturnValue(null as any);
    await expect(guard.canActivate(mockContext("Bearer abc"))).rejects.toThrow(
      UnauthorizedException,
    );
  });

  it("throws when user not found", async () => {
    jwt.verifyToken.mockResolvedValue(true);
    jwt.decodeToken.mockReturnValue({ sub: "1", role: "user" });
    db.findOne.mockResolvedValue(null);
    await expect(guard.canActivate(mockContext("Bearer good"))).rejects.toThrow(
      UnauthorizedException,
    );
  });

  it("attaches user on success", async () => {
    jwt.verifyToken.mockResolvedValue(true);
    jwt.decodeToken.mockReturnValue({ sub: "1", role: "user" });
    db.findOne.mockResolvedValue({
      id: "1",
      email: "a@b.com",
      role: "user",
      firstName: "A",
      lastName: "B",
    } as any);
    const ctx = mockContext("Bearer good");
    const result = await guard.canActivate(ctx);
    expect(result).toBe(true);
    const req = ctx.switchToHttp().getRequest();
    expect(req.user).toBeDefined();
    expect(req.user.id).toBe("1");
    expect(req.user.roles).toEqual(["user"]);
  });
});
