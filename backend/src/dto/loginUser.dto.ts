/* eslint-disable @typescript-eslint/no-unsafe-call */
import { IsString, IsNotEmpty, ValidateIf } from "class-validator";

export class loginUserDto {
  @ValidateIf((o) => !o.email)
  @IsString({ message: "Username must be a string" })
  @IsNotEmpty({ message: "Username is required when email is not provided" })
  username?: string;

  @ValidateIf((o) => !o.username)
  @IsString({ message: "Email must be a string" })
  @IsNotEmpty({ message: "Email is required when username is not provided" })
  email?: string;

  @IsNotEmpty({ message: "Password is required" })
  password: string;
}
