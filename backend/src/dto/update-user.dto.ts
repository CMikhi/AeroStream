/* eslint-disable prettier/prettier */
import { IsOptional, IsString, IsStrongPassword } from "class-validator";

export class UpdateUserDto {
  @IsOptional()
  @IsString()
  @IsStrongPassword({
      minLength: 12,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    },
    {
      message:
        "Password is too weak. It must be at least 12 characters long and include uppercase letters, lowercase letters, numbers, and symbols.",
    })
  password?: string;
}
