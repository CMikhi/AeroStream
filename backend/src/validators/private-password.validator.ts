/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */

/* PasswordMatchesPrivate function for rooms.controller
 * A function that checks if the room availablity is private, and if so,
 * allow a password parameter. If the room is public, do not allow a password
 * parameter to be passed.
 */
import {
  registerDecorator,
  ValidationOptions,
  ValidationArguments,
} from "class-validator";

export function PasswordMatchesPrivate(validationOptions?: ValidationOptions) {
  return function (object: any, propertyName: string) {
    registerDecorator({
      name: "passwordMatchesPrivate",
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any, args: ValidationArguments) {
          const obj = args.object as any;
          if (obj.private) {
            return typeof value === "string" && value.trim() !== "";
          } else {
            return value === undefined || value === null;
          }
        },
        defaultMessage(args: ValidationArguments) {
          const obj = args.object as any;
          return obj.private
            ? "Password is required for private rooms"
            : "Password must not be set for public rooms";
        },
      },
    });
  };
}
