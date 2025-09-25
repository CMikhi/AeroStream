/* eslint-disable @typescript-eslint/no-unsafe-call */
import {
  IsEmail,
  IsNotEmpty,
  IsString,
  Length,
  Matches,
  IsStrongPassword,
  IsOptional,
} from "class-validator";

export class CreateUserDto {
  @IsNotEmpty({ message: "Email is required" })
  @IsEmail({}, { message: "Invalid email format" })
  email: string;

  @IsNotEmpty()
  @IsString()
  firstName: string;

  @IsNotEmpty()
  @IsString()
  lastName: string;

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

  @IsNotEmpty({ message: "Username is required" })
  @Length(3, 20, { message: "Username must be between 3 and 20 characters" })
  username: string;

  @IsOptional()
  @IsString()
  role?: string;
}
