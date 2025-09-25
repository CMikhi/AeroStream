import { RolesGuard } from "./roles.guard";
import { Reflector } from "@nestjs/core";
import { ForbiddenException } from "@nestjs/common";

const mockExecutionContext = (user?: any) =>
  ({
    switchToHttp: () => ({ getRequest: () => ({ user }) }),
    getHandler: () => function handler() {},
    // Unused but required shape
    getClass: () => function clazz() {},
  }) as any;

describe("RolesGuard", () => {
  let reflector: Reflector;
  let guard: RolesGuard;

  beforeEach(() => {
    reflector = new Reflector();
    guard = new RolesGuard(reflector);
  });

  it("allows when no roles metadata", () => {
    jest.spyOn(reflector, "get").mockReturnValue(undefined);
    const can = guard.canActivate(mockExecutionContext({ roles: ["user"] }));
    expect(can).toBe(true);
  });

  it("allows when user has required role", () => {
    jest.spyOn(reflector, "get").mockReturnValue(["admin"]);
    const can = guard.canActivate(mockExecutionContext({ roles: ["admin"] }));
    expect(can).toBe(true);
  });

  it("denies when user missing role", () => {
    jest.spyOn(reflector, "get").mockReturnValue(["admin"]);
    expect(() =>
      guard.canActivate(mockExecutionContext({ roles: ["user"] })),
    ).toThrow(ForbiddenException);
  });

  it("throws when user missing", () => {
    jest.spyOn(reflector, "get").mockReturnValue(["user"]);
    expect(() => guard.canActivate(mockExecutionContext(undefined))).toThrow(
      ForbiddenException,
    );
  });

  it("throws when roles not array", () => {
    jest.spyOn(reflector, "get").mockReturnValue(["user"]);
    expect(() =>
      guard.canActivate(mockExecutionContext({ roles: "user" })),
    ).toThrow(ForbiddenException);
  });
});
