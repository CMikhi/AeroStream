import { IsString, IsNotEmpty } from "class-validator";

export class loginUserDto {
  @IsString({ message: "Username must be a string" })
  @IsNotEmpty({ message: "Username is required" })
  username: string;

  @IsNotEmpty({ message: "Password is required" })
  password: string;
}
