/* eslint-disable @typescript-eslint/no-unsafe-call */
import {
  IsNotEmpty,
  IsString,
  Length,
  Matches,
  IsStrongPassword,
  IsOptional,
} from "class-validator";

export class CreateUserDto {
  @IsNotEmpty({ message: "Username is required" })
  @Length(3, 20, { message: "Username must be between 3 and 20 characters" })
  @IsString()
  username: string;

  @IsNotEmpty({ message: "Password is required" })
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, {
    message: "Password must contain uppercase, lowercase, and a number",
  })
  @IsStrongPassword({
    minLength: 12,
    minLowercase: 1,
    minUppercase: 1,
    minNumbers: 1,
    minSymbols: 1,
  })
  password: string;

  @IsOptional()
  @IsString()
  role?: string;
}
