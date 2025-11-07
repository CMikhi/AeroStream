import {
  IsNotEmpty,
  IsString,
  Length,
  IsStrongPassword,
  IsOptional,
  Matches,
} from "class-validator";
import { Transform } from "class-transformer";

export class CreateUserDto {
  @IsNotEmpty({ message: "Username is required" })
  @Length(3, 20, { message: "Username must be between 3 and 20 characters" })
  @IsString()
  username: string;

  @IsNotEmpty({ message: "Password is required" })
  @IsStrongPassword(
    {
      minLength: 12,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    },
    {
      message:
        "Password must be 12 characters, 1 lowercase, 1 uppercase, 1 number, and 1 symbol",
    },
  )
  password: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => value.toLowerCase() as string)
  @Matches(/^(admin|user)$/, {
    message: "Role must be either 'admin' or 'user'",
  })
  role?: string;
}
