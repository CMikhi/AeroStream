import { Test, TestingModule } from "@nestjs/testing";
import { AuthController } from "./auth.controller";
import { AuthService } from "./auth.service";
import { JwtService } from "../jwt/jwt.service";
import { JwtAuthGuard } from "./jwt-auth.guard";
import { DbService } from "../db/db.service";

describe("AuthController", () => {
  let controller: AuthController;

  beforeEach(async () => {
    const mockAuthService = {
      login: jest.fn(),
      register: jest.fn(),
      refresh: jest.fn(),
      getLoggedIn: jest.fn(),
    };

    const mockJwtService = {
      verifyToken: jest.fn(),
      decodeToken: jest.fn(),
    };

    const mockDbService = {
      findOne: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [AuthController],
      providers: [
        { provide: AuthService, useValue: mockAuthService },
        { provide: JwtService, useValue: mockJwtService },
        { provide: JwtAuthGuard, useValue: {} },
        { provide: DbService, useValue: mockDbService },
      ],
    }).compile();

    controller = module.get<AuthController>(AuthController);
  });

  it("should be defined", () => {
    expect(controller).toBeDefined();
  });
});
