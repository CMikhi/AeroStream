import { RolesService, UserRole } from "./roles.service";
import { DbService } from "../db/db.service";

// Minimal user type for tests
interface TestUser {
  id: string;
  role: string;
  email: string;
  firstName: string;
  lastName: string;
  createdAt: Date;
  password: string;
  refreshTokenHash: string;
}

describe("RolesService", () => {
  let service: RolesService;
  let db: jest.Mocked<DbService>;

  beforeEach(() => {
    db = {
      findOne: jest.fn(),
      updateRole: jest.fn(),
    } as any;
    service = new RolesService(db);
  });

  describe("hasPermission", () => {
    it("admin should have user permissions", () => {
      expect(service.hasPermission([UserRole.ADMIN], [UserRole.USER])).toBe(
        true,
      );
    });
    it("user should not have admin permissions", () => {
      expect(service.hasPermission([UserRole.USER], [UserRole.ADMIN])).toBe(
        false,
      );
    });
    it("multiple required roles - any match passes", () => {
      expect(
        service.hasPermission([UserRole.USER], [UserRole.ADMIN, UserRole.USER]),
      ).toBe(true);
    });
  });

  describe("getAllowedRoles", () => {
    it("admin should list admin and user", () => {
      expect(service.getAllowedRoles(UserRole.ADMIN)).toEqual([
        UserRole.ADMIN,
        UserRole.USER,
      ]);
    });
    it("user should only list user", () => {
      expect(service.getAllowedRoles(UserRole.USER)).toEqual([UserRole.USER]);
    });
    it("unknown role returns empty array", () => {
      expect(service.getAllowedRoles("ghost")).toEqual([]);
    });
  });

  describe("isValidRole", () => {
    it("accepts valid roles", () => {
      expect(service.isValidRole("admin")).toBe(true);
      expect(service.isValidRole("user")).toBe(true);
    });
    it("rejects invalid role", () => {
      expect(service.isValidRole("root")).toBe(false);
    });
  });

  describe("getRole", () => {
    it("returns role when user exists", async () => {
      db.findOne.mockResolvedValue({
        id: "1",
        role: "admin",
        email: "admin@test.com",
        firstName: "Admin",
        lastName: "User",
        createdAt: new Date(),
        password: "hashed",
        refreshTokenHash: "hash",
      } as TestUser);
      await expect(service.getRole("1")).resolves.toBe("admin");
    });
    it("throws when user not found", async () => {
      db.findOne.mockResolvedValue(null);
      await expect(service.getRole("x")).rejects.toThrow();
    });
  });

  describe("update", () => {
    it("updates user role", async () => {
      const updated = {
        id: "1",
        role: "admin",
        email: "admin@test.com",
        firstName: "Admin",
        lastName: "User",
        createdAt: new Date(),
        password: "hashed",
        refreshTokenHash: "hash",
      } as TestUser;
      (db.updateRole as jest.Mock).mockResolvedValue(updated);
      await expect(service.update("1", "admin")).resolves.toEqual(updated);
    });
  });
});
