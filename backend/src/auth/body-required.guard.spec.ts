import { BodyRequiredGuard } from "./body-required.guard";
import { BadRequestException, ExecutionContext } from "@nestjs/common";

// Minimal mock ExecutionContext (only what's needed by the guard)
const mockCtx = (body: unknown, routePath: string): ExecutionContext =>
  ({
    switchToHttp: () => ({
      getRequest: () => ({ body, route: { path: routePath } }),
    }),
  }) as unknown as ExecutionContext;

describe("BodyRequiredGuard", () => {
  let guard: BodyRequiredGuard;

  beforeEach(() => {
    guard = new BodyRequiredGuard();
  });

  const invalidBodies: Array<{ label: string; value: unknown }> = [
    { label: "null", value: null },
    { label: "undefined", value: undefined },
    { label: "empty object", value: {} },
    { label: "array", value: [] },
    { label: "string", value: "hello" },
  ];

  invalidBodies.forEach(({ label, value }) => {
    it(`throws when body is ${label}`, () => {
      expect(() => guard.canActivate(mockCtx(value, "/auth/login"))).toThrow(
        BadRequestException,
      );
    });
  });

  it("throws when login body missing email", () => {
    expect(() =>
      guard.canActivate(mockCtx({ password: "x" }, "/auth/login")),
    ).toThrow(BadRequestException);
  });

  it("throws when login body missing password", () => {
    expect(() =>
      guard.canActivate(mockCtx({ email: "a@b.com" }, "/auth/login")),
    ).toThrow(BadRequestException);
  });

  it("passes with valid login body", () => {
    const can = guard.canActivate(
      mockCtx({ email: "a@b.com", password: "Secret123!" }, "/auth/login"),
    );
    expect(can).toBe(true);
  });

  it("throws when register body missing email", () => {
    expect(() =>
      guard.canActivate(
        mockCtx(
          { password: "XyZ123!pass", username: "user1" },
          "/auth/register",
        ),
      ),
    ).toThrow(BadRequestException);
  });

  it("throws when register body missing password", () => {
    expect(() =>
      guard.canActivate(
        mockCtx({ email: "a@b.com", username: "user1" }, "/auth/register"),
      ),
    ).toThrow(BadRequestException);
  });

  it("passes with valid register body (only checks email/password in guard)", () => {
    const can = guard.canActivate(
      mockCtx(
        {
          email: "a@b.com",
          password: "StrongPass123!",
          username: "user1",
          firstName: "A",
          lastName: "B",
        },
        "/auth/register",
      ),
    );
    expect(can).toBe(true);
  });

  it("ignores unrelated routes (should allow since only body presence enforced)", () => {
    const can = guard.canActivate(mockCtx({ any: "value" }, "/other/route"));
    expect(can).toBe(true);
  });
});
