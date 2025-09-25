import { Test, TestingModule } from "@nestjs/testing";
import { DbService } from "./db.service";

describe("DbService", () => {
  let service: DbService;

  beforeEach(async () => {
    const mockUserRepository = {};
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        DbService,
        { provide: "UserRepository", useValue: mockUserRepository },
      ],
    }).compile();

    service = module.get<DbService>(DbService);
  });

  it("should be defined", () => {
    expect(service).toBeDefined();
  });
});
