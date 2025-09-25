import { Test, TestingModule } from "@nestjs/testing";
import { RolesController } from "./roles.controller";
import { RolesService } from "./roles.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { RolesGuard } from "./roles.guard";
import { JwtService } from "../jwt/jwt.service";
import { DbService } from "../db/db.service";

describe("RolesController", () => {
  let controller: RolesController;
  let service: jest.Mocked<RolesService>;

  beforeEach(async () => {
    service = {
      getRole: jest.fn(),
      update: jest.fn(),
      isValidRole: jest.fn(),
    } as any;

    const module: TestingModule = await Test.createTestingModule({
      controllers: [RolesController],
      providers: [
        { provide: RolesService, useValue: service },
        // Provide real guard tokens but with simple canActivate always true
        { provide: JwtAuthGuard, useValue: { canActivate: () => true } },
        { provide: RolesGuard, useValue: { canActivate: () => true } },
        // Satisfy JwtAuthGuard constructor deps so Nest doesn't complain if it inspects them
        {
          provide: JwtService,
          useValue: {
            verifyToken: jest.fn().mockResolvedValue(true),
            decodeToken: jest.fn().mockReturnValue({ sub: "1", role: "admin" }),
          },
        },
        {
          provide: DbService,
          useValue: {
            findOne: jest.fn().mockResolvedValue({
              id: "1",
              email: "test@test.com",
              role: "admin",
              firstName: "Test",
              lastName: "User",
            }),
          },
        },
      ],
    }).compile();

    controller = module.get(RolesController);
  });

  it("returns not found for missing user role", async () => {
    service.getRole.mockResolvedValue(undefined as any);
    const res = await controller.getRole("x");
    expect(res.status).toBe(404);
  });

  it("returns role when found", async () => {
    service.getRole.mockResolvedValue("admin");
    const res = await controller.getRole("1");
    expect(res.data).toBe("admin");
  });

  it("rejects invalid role update", async () => {
    service.isValidRole.mockReturnValue(false);
    const res = await controller.updateUser("1", "root");
    expect(res.status).toBe(400);
  });

  it("updates user role", async () => {
    service.isValidRole.mockReturnValue(true);
    service.update.mockResolvedValue({
      id: "1",
      email: "a@b.com",
      role: "admin",
    } as any);
    const res = await controller.updateUser("1", "admin");
    expect(res.status).toBe(200);
    expect(res.data.role).toBe("admin");
  });
});
