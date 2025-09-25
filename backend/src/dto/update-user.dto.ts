/* eslint-disable @typescript-eslint/no-unsafe-call */
import {
  IsOptional,
  IsString,
  IsStrongPassword,
  Matches,
} from "class-validator";

export class UpdateUserDto {
  @IsOptional()
  @IsString()
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
  password?: string;
}
